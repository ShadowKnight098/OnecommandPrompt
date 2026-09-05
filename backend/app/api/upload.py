"""Upload API endpoint for accepting and safely unpacking project ZIP archives."""
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Request
from app.config import get_effective_base_url
from app.models.project import ProjectRecord, ProjectStatus
from app.models.plan import InstallationPlan, RuntimeConfig, ProjectDownloadConfig, EnvironmentConfig, EntryPointConfig
from app.security.limits import SecurityLimits, SecurityLimitsException
from app.security.zip_validator import SafeZipExtractor, ZipValidationError
from app.analyzer.project import ProjectAnalyzer
from app.storage import ProjectStore

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_project_zip(
    request: Request,
    file: UploadFile = File(...),
    project_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    user_email: Optional[str] = Form(None),
    is_public: Optional[bool] = Form(True),
):
    """
    Accepts a ZIP file, checks security limits, safely extracts contents,
    and runs static analysis.
    """
    # 1. Validate file extension
    filename = file.filename or "project.zip"
    if not filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only ZIP archives (.zip) are supported."
        )

    # 2. Generate unique project ID
    project_id = uuid.uuid4().hex[:8].upper()
    clean_project_name = project_name or Path(filename).stem or f"project_{project_id}"

    project_dir = ProjectStore.get_project_dir(project_id)
    zip_dest = project_dir / "project.zip"
    extracted_dest = project_dir / "extracted"

    # 3. Stream upload while checking file size limit
    total_bytes = 0
    try:
        with open(zip_dest, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                total_bytes += len(chunk)
                if total_bytes > SecurityLimits.MAX_UPLOAD_SIZE:
                    raise SecurityLimitsException(
                        f"Uploaded file exceeds size limit of {SecurityLimits.MAX_UPLOAD_SIZE / (1024 * 1024):.0f} MB."
                    )
                f.write(chunk)
    except SecurityLimitsException as e:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))
    except Exception as e:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {str(e)}")

    # 4. Safely Extract ZIP
    try:
        SafeZipExtractor.extract_safely(zip_dest, extracted_dest)
    except (ZipValidationError, SecurityLimitsException) as e:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Extraction failed: {str(e)}")

    # 5. Run Static Analysis Engine
    try:
        analysis = ProjectAnalyzer.analyze_project(
            project_id=project_id,
            project_name=clean_project_name,
            extracted_root=extracted_dest,
        )
        if description:
            analysis.description = description

        # If ambiguous entrypoint, status is NEEDS_INPUT, otherwise READY
        project_status = ProjectStatus.NEEDS_INPUT if analysis.is_ambiguous_entrypoint else ProjectStatus.READY

        # Upload archive to Supabase Storage in background thread
        supabase_url = ProjectStore.upload_archive(project_id, zip_dest)
        archive_path_val = supabase_url if supabase_url else str(zip_dest)

        record = ProjectRecord(
            id=project_id,
            original_filename=filename,
            description=description,
            status=project_status,
            analysis=analysis,
            archive_path=archive_path_val,
            extracted_path=str(extracted_dest),
            user_id=user_id,
            user_email=user_email,
            is_public=bool(is_public) if is_public is not None else True,
        )
        ProjectStore.save_project(record)

        base_url = get_effective_base_url(request)

        # 6. Generate initial installation plan
        plan = InstallationPlan(
            project_id=project_id,
            project_name=clean_project_name,
            runtime=RuntimeConfig(
                type="python",
                version=analysis.python_requirement,
            ),
            project=ProjectDownloadConfig(
                project_id=project_id,
                archive_name="project.zip",
                download_url=f"{base_url}/api/projects/{project_id}/download",
                target_directory_name=clean_project_name,
            ),
            environment=EnvironmentConfig(
                type="venv",
                path=".venv",
            ),
            dependencies_source=analysis.dependency_source,
            dependencies=[
                d.name + (d.version_specifier if d.version_specifier else "")
                for d in analysis.dependencies
                if d.enabled
            ],
            entrypoint=EntryPointConfig(
                command_type=analysis.entry_point_framework or "python",
                entry_file=analysis.entry_point or "main.py",
                run_command=f"python {analysis.entry_point or 'main.py'}",
            ),
        )
        ProjectStore.save_plan(project_id, plan)

        return record
    except Exception as e:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Analysis failed: {str(e)}")


@router.post("/upload-folder", status_code=status.HTTP_201_CREATED)
async def upload_project_folder(
    request: Request,
    files: list[UploadFile] = File(...),
    project_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    user_email: Optional[str] = Form(None),
    is_public: Optional[bool] = Form(True),
):
    """
    Accepts raw multi-file folder uploads (with relative paths preserved in filenames),
    builds a project archive, and analyzes the project.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided in folder upload."
        )

    # 1. Determine folder/project name
    first_path = files[0].filename or "project/main.py"
    parts = Path(first_path).parts
    folder_name = parts[0] if len(parts) > 1 else "project"
    
    project_id = uuid.uuid4().hex[:8].upper()
    clean_project_name = folder_name or f"project_{project_id}"

    project_dir = ProjectStore.get_project_dir(project_id)
    extracted_dest = project_dir / "extracted"
    zip_dest = project_dir / "project.zip"

    try:
        import zipfile
        extracted_dest.mkdir(parents=True, exist_ok=True)
        total_size = 0

        # Create zip and write files directly
        with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_item in files:
                rel_filename = file_item.filename.replace("\\", "/").lstrip("/")
                content = await file_item.read()
                total_size += len(content)

                if total_size > SecurityLimits.MAX_EXTRACTED_SIZE:
                    raise SecurityLimitsException(
                        f"Folder size exceeds limit of {SecurityLimits.MAX_EXTRACTED_SIZE / (1024*1024):.0f} MB."
                    )

                # Path traversal check
                if ".." in Path(rel_filename).parts:
                    continue

                # Add to ZIP
                zf.writestr(rel_filename, content)

                # Extract to disk
                file_dest = (extracted_dest / rel_filename).resolve()
                try:
                    file_dest.relative_to(extracted_dest)
                except ValueError:
                    continue

                file_dest.parent.mkdir(parents=True, exist_ok=True)
                file_dest.write_bytes(content)

        # Static Analysis
        analysis = ProjectAnalyzer.analyze_project(
            project_id=project_id,
            project_name=clean_project_name,
            extracted_root=extracted_dest,
        )
        if description:
            analysis.description = description

        project_status = ProjectStatus.NEEDS_INPUT if analysis.is_ambiguous_entrypoint else ProjectStatus.READY

        # Upload archive to Supabase Storage
        supabase_url = ProjectStore.upload_archive(project_id, zip_dest)
        archive_path_val = supabase_url if supabase_url else str(zip_dest)

        record = ProjectRecord(
            id=project_id,
            original_filename=f"{clean_project_name}.zip",
            description=description,
            status=project_status,
            analysis=analysis,
            archive_path=archive_path_val,
            extracted_path=str(extracted_dest),
            user_id=user_id,
            user_email=user_email,
            is_public=bool(is_public) if is_public is not None else True,
        )
        ProjectStore.save_project(record)

        base_url = get_effective_base_url(request)

        # Plan
        plan = InstallationPlan(
            project_id=project_id,
            project_name=clean_project_name,
            runtime=RuntimeConfig(
                type="python",
                version=analysis.python_requirement,
            ),
            project=ProjectDownloadConfig(
                project_id=project_id,
                archive_name="project.zip",
                download_url=f"{base_url}/api/projects/{project_id}/download",
                target_directory_name=clean_project_name,
            ),
            environment=EnvironmentConfig(
                type="venv",
                path=".venv",
            ),
            dependencies_source=analysis.dependency_source,
            dependencies=[
                d.name + (d.version_specifier if d.version_specifier else "")
                for d in analysis.dependencies
                if d.enabled
            ],
            entrypoint=EntryPointConfig(
                command_type=analysis.entry_point_framework or "python",
                entry_file=analysis.entry_point or "main.py",
                run_command=f"python {analysis.entry_point or 'main.py'}",
            ),
        )
        ProjectStore.save_plan(project_id, plan)

        return record
    except Exception as e:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Folder upload failed: {str(e)}")

