"""Projects API router for inspecting and updating project configurations."""
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import FileResponse, RedirectResponse
from app.config import get_effective_base_url
from app.models.project import (
    ProjectRecord,
    ProjectStatus,
    EntryPointSelectionRequest,
    DependenciesUpdateRequest,
    GenerateRequest,
)
from app.models.plan import (
    InstallationPlan,
    RuntimeConfig,
    ProjectDownloadConfig,
    EnvironmentConfig,
    EntryPointConfig,
)
from app.storage import ProjectStore

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("")
async def list_projects(request: Request, limit: int = 30):
    """Lists recent public projects for marketplace / community showcase."""
    base_url = get_effective_base_url(request)
    records = ProjectStore.list_projects(limit=limit)

    return {
        "projects": [
            {
                "id": p.id,
                "project_name": (p.analysis and p.analysis.project_name) or p.original_filename.replace(".zip", ""),
                "description": p.description or (p.analysis and p.analysis.description) or "Python project with automated bootstrap installer",
                "python_requirement": p.analysis.python_requirement if p.analysis else ">=3.10",
                "entry_point": p.analysis.entry_point if p.analysis else "main.py",
                "entry_point_framework": p.analysis.entry_point_framework if p.analysis else "python",
                "dependencies_count": len([d for d in p.analysis.dependencies if d.enabled]) if p.analysis else 0,
                "file_count": p.analysis.file_count if p.analysis else 0,
                "total_size_bytes": p.analysis.total_size_bytes if p.analysis else 0,
                "created_at": p.created_at.isoformat(),
                "installer_commands": {
                    "windows": f"irm {base_url}/i/{p.id}.ps1 -OutFile install.ps1; .\\install.ps1",
                    "unix": f"curl -fsSL {base_url}/i/{p.id}.sh -o install.sh && bash install.sh",
                },
            }
            for p in records
            if p.analysis is not None
        ]
    }


@router.get("/{project_id}")
async def get_project(project_id: str, request: Request):
    """Retrieves project record, analysis results, and generated plan."""
    record = ProjectStore.get_project(project_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    base_url = get_effective_base_url(request)
    plan = ProjectStore.get_plan(project_id)
    return {
        "record": record,
        "plan": plan,
        "installer_commands": {
            "windows": f"irm {base_url}/i/{project_id}.ps1 -OutFile install.ps1; .\\install.ps1",
            "unix": f"curl -fsSL {base_url}/i/{project_id}.sh -o install.sh && bash install.sh",
        },
    }


@router.post("/{project_id}/entrypoint")
async def select_entrypoint(project_id: str, payload: EntryPointSelectionRequest):
    """Sets or overrides the entry point file for the project."""
    record = ProjectStore.get_project(project_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if record.analysis:
        record.analysis.entry_point = payload.entry_point
        record.status = ProjectStatus.READY

    ProjectStore.save_project(record)

    # Update installation plan entry point
    plan = ProjectStore.get_plan(project_id)
    if plan:
        plan.entrypoint.entry_file = payload.entry_point
        plan.entrypoint.run_command = f"python {payload.entry_point}"
        ProjectStore.save_plan(project_id, plan)

    return {"status": "ok", "entry_point": payload.entry_point}


@router.post("/{project_id}/dependencies")
async def update_dependencies(project_id: str, payload: DependenciesUpdateRequest):
    """Updates the project dependencies list."""
    record = ProjectStore.get_project(project_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if record.analysis:
        record.analysis.dependencies = payload.dependencies

    ProjectStore.save_project(record)

    # Update plan dependencies
    plan = ProjectStore.get_plan(project_id)
    if plan:
        plan.dependencies = [
            d.name + (d.version_specifier if d.version_specifier else "")
            for d in payload.dependencies
            if d.enabled
        ]
        ProjectStore.save_plan(project_id, plan)

    return {"status": "ok", "dependencies": record.analysis.dependencies if record.analysis else []}


@router.post("/{project_id}/generate")
async def generate_installers(project_id: str, request: Request, payload: GenerateRequest = None):
    """Rebuilds the intermediate installation plan and generates commands."""
    record = ProjectStore.get_project(project_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    analysis = record.analysis
    if not analysis:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project analysis missing")

    base_url = get_effective_base_url(request)
    entry_point = (payload and payload.entry_point) or analysis.entry_point or "main.py"
    deps_list = (payload and payload.dependencies) or analysis.dependencies
    py_req = (payload and payload.python_requirement) or analysis.python_requirement

    clean_deps = [
        d.name + (d.version_specifier if d.version_specifier else "")
        for d in deps_list
        if d.enabled
    ]

    plan = InstallationPlan(
        project_id=project_id,
        project_name=analysis.project_name,
        runtime=RuntimeConfig(
            type="python",
            version=py_req,
        ),
        project=ProjectDownloadConfig(
            project_id=project_id,
            archive_name="project.zip",
            download_url=f"{base_url}/api/projects/{project_id}/download",
            target_directory_name=analysis.project_name,
        ),
        environment=EnvironmentConfig(
            type="venv",
            path=".venv",
        ),
        dependencies_source=analysis.dependency_source,
        dependencies=clean_deps,
        entrypoint=EntryPointConfig(
            command_type=analysis.entry_point_framework or "python",
            entry_file=entry_point,
            run_command=f"python {entry_point}",
        ),
    )

    ProjectStore.save_plan(project_id, plan)
    record.status = ProjectStatus.READY
    ProjectStore.save_project(record)

    return {
        "status": "ready",
        "plan": plan,
        "installer_commands": {
            "windows": f"irm {base_url}/i/{project_id}.ps1 -OutFile install.ps1; .\\install.ps1",
            "unix": f"curl -fsSL {base_url}/i/{project_id}.sh -o install.sh && bash install.sh",
        },
    }


@router.get("/{project_id}/download")
async def download_project_archive(project_id: str):
    """Serves the project ZIP archive for installer scripts to download."""
    record = ProjectStore.get_project(project_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # If archive_path is a public Supabase URL, redirect directly
    if record.archive_path and record.archive_path.startswith("http"):
        return RedirectResponse(url=record.archive_path)

    # Check if Supabase storage has the file
    supabase_url = ProjectStore.get_archive_url(project_id)
    if supabase_url and not Path(record.archive_path).exists():
        return RedirectResponse(url=supabase_url)

    zip_path = Path(record.archive_path)
    if not zip_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archive file missing on server")

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"{record.analysis.project_name if record.analysis else project_id}.zip",
    )
