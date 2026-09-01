"""Installers API router for generating and serving raw bootstrap installer scripts."""
from fastapi import APIRouter, HTTPException, status, Response
from app.storage import ProjectStore
from app.generator.powershell import PowerShellGenerator
from app.generator.unix import UnixGenerator

router = APIRouter(tags=["installers"])


@router.get("/i/{project_id}.ps1")
async def get_powershell_installer(project_id: str):
    """Returns the generated PowerShell installation script (.ps1)."""
    clean_id = project_id.replace(".ps1", "").strip()
    plan = ProjectStore.get_plan(clean_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installation plan not found for this project")

    script = PowerShellGenerator.generate(plan)
    return Response(
        content=script,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="install_{clean_id}.ps1"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


@router.get("/i/{project_id}.sh")
async def get_unix_installer(project_id: str):
    """Returns the generated Bash installation script (.sh)."""
    clean_id = project_id.replace(".sh", "").strip()
    plan = ProjectStore.get_plan(clean_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installation plan not found for this project")

    script = UnixGenerator.generate(plan)
    return Response(
        content=script,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="install_{clean_id}.sh"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


@router.get("/api/installers/{project_id}/plan")
async def get_raw_plan(project_id: str):
    """Returns the intermediate JSON installation plan."""
    plan = ProjectStore.get_plan(project_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installation plan not found")
    return plan
