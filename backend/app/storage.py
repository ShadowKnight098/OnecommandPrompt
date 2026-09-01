"""Project persistence and repository management using Supabase and local storage."""
import json
import threading
from pathlib import Path
from typing import Dict, Optional, List, Union
from datetime import datetime, timezone
from app.config import STORAGE_DIR, supabase_client, SUPABASE_BUCKET_NAME
from app.models.project import ProjectRecord, ProjectStatus, ProjectAnalysis
from app.models.plan import InstallationPlan


class ProjectStore:
    """Manages project metadata persistence in Supabase PostgreSQL + Storage with local caching."""

    _memory_cache: Dict[str, ProjectRecord] = {}
    _plan_cache: Dict[str, InstallationPlan] = {}

    @classmethod
    def get_project_dir(cls, project_id: str) -> Path:
        """Returns the local project directory (used for temporary extraction/analysis)."""
        pdir = STORAGE_DIR / project_id
        pdir.mkdir(parents=True, exist_ok=True)
        return pdir

    @classmethod
    def save_project(cls, record: ProjectRecord):
        """Saves project record to Supabase and local cache."""
        cls._memory_cache[record.id] = record

        # 1. Local disk backup
        meta_file = cls.get_project_dir(record.id) / "metadata.json"
        try:
            with open(meta_file, "w", encoding="utf-8") as f:
                f.write(record.model_dump_json(indent=2))
        except Exception:
            pass

        # 2. Supabase PostgreSQL persistence
        if supabase_client:
            try:
                payload = {
                    "id": record.id,
                    "original_filename": record.original_filename,
                    "description": record.description,
                    "status": record.status.value if hasattr(record.status, "value") else str(record.status),
                    "error_message": record.error_message,
                    "analysis": record.analysis.model_dump(mode="json") if record.analysis else None,
                    "archive_path": record.archive_path,
                    "extracted_path": record.extracted_path,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                supabase_client.table("projects").upsert(payload).execute()
            except Exception as e:
                print(f"[Supabase] save_project error: {e}")

    @classmethod
    def get_project(cls, project_id: str) -> Optional[ProjectRecord]:
        """Retrieves project record from memory cache, Supabase, or local disk."""
        if project_id in cls._memory_cache:
            return cls._memory_cache[project_id]

        # Try fetching from Supabase
        if supabase_client:
            try:
                res = supabase_client.table("projects").select("*").eq("id", project_id).execute()
                if res.data and len(res.data) > 0:
                    row = res.data[0]
                    analysis_obj = None
                    if row.get("analysis"):
                        analysis_obj = ProjectAnalysis.model_validate(row["analysis"])
                    
                    record = ProjectRecord(
                        id=row["id"],
                        original_filename=row["original_filename"],
                        description=row.get("description"),
                        status=ProjectStatus(row.get("status", "uploaded")),
                        error_message=row.get("error_message"),
                        analysis=analysis_obj,
                        archive_path=row.get("archive_path", ""),
                        extracted_path=row.get("extracted_path", ""),
                    )
                    cls._memory_cache[project_id] = record
                    return record
            except Exception as e:
                print(f"[Supabase] get_project error: {e}")

    @classmethod
    def list_projects(cls, limit: int = 30) -> List[ProjectRecord]:
        """Lists recently uploaded projects for the community showcase / marketplace."""
        projects: List[ProjectRecord] = []

        # 1. Fetch from Supabase
        if supabase_client:
            try:
                res = supabase_client.table("projects").select("*").order("created_at", desc=True).limit(limit).execute()
                if res.data:
                    for row in res.data:
                        analysis_obj = None
                        if row.get("analysis"):
                            try:
                                analysis_obj = ProjectAnalysis.model_validate(row["analysis"])
                            except Exception:
                                pass
                        
                        rec = ProjectRecord(
                            id=row["id"],
                            original_filename=row.get("original_filename", "project.zip"),
                            description=row.get("description"),
                            status=ProjectStatus(row.get("status", "ready")),
                            error_message=row.get("error_message"),
                            analysis=analysis_obj,
                            archive_path=row.get("archive_path", ""),
                            extracted_path=row.get("extracted_path", ""),
                        )
                        cls._memory_cache[rec.id] = rec
                        projects.append(rec)
                    if projects:
                        return projects
            except Exception as e:
                print(f"[Supabase] list_projects error: {e}")

        # 2. Fallback to in-memory cache
        if cls._memory_cache:
            return list(cls._memory_cache.values())[:limit]

        # 3. Fallback to local storage disk
        if STORAGE_DIR.exists():
            for pdir in STORAGE_DIR.iterdir():
                if pdir.is_dir():
                    meta = pdir / "metadata.json"
                    if meta.exists():
                        try:
                            data = json.loads(meta.read_text(encoding="utf-8"))
                            rec = ProjectRecord.model_validate(data)
                            cls._memory_cache[rec.id] = rec
                            projects.append(rec)
                        except Exception:
                            pass

        return projects[:limit]

        # Fallback to local disk
        meta_file = cls.get_project_dir(project_id) / "metadata.json"
        if meta_file.exists():
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                record = ProjectRecord.model_validate(data)
                cls._memory_cache[project_id] = record
                return record
            except Exception:
                return None
        return None

    @classmethod
    def save_plan(cls, project_id: str, plan: InstallationPlan):
        """Saves installation plan to Supabase and local cache."""
        cls._plan_cache[project_id] = plan

        # 1. Local disk backup
        plan_file = cls.get_project_dir(project_id) / "plan.json"
        try:
            with open(plan_file, "w", encoding="utf-8") as f:
                f.write(plan.model_dump_json(indent=2))
        except Exception:
            pass

        # 2. Supabase PostgreSQL persistence
        if supabase_client:
            try:
                payload = {
                    "project_id": project_id,
                    "plan_data": plan.model_dump(mode="json"),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                supabase_client.table("installation_plans").upsert(payload).execute()
            except Exception as e:
                print(f"[Supabase] save_plan error: {e}")

    @classmethod
    def get_plan(cls, project_id: str) -> Optional[InstallationPlan]:
        """Retrieves installation plan from memory cache, Supabase, or local disk."""
        if project_id in cls._plan_cache:
            return cls._plan_cache[project_id]

        # Try fetching from Supabase
        if supabase_client:
            try:
                res = supabase_client.table("installation_plans").select("*").eq("project_id", project_id).execute()
                if res.data and len(res.data) > 0:
                    row = res.data[0]
                    plan = InstallationPlan.model_validate(row["plan_data"])
                    cls._plan_cache[project_id] = plan
                    return plan
            except Exception as e:
                print(f"[Supabase] get_plan error: {e}")

        # Fallback to local disk
        plan_file = cls.get_project_dir(project_id) / "plan.json"
        if plan_file.exists():
            try:
                data = json.loads(plan_file.read_text(encoding="utf-8"))
                plan = InstallationPlan.model_validate(data)
                cls._plan_cache[project_id] = plan
                return plan
            except Exception:
                return None
        return None

    @classmethod
    def upload_archive(cls, project_id: str, file_path_or_bytes: Union[Path, str, bytes], filename: str = "project.zip") -> Optional[str]:
        """Uploads project archive ZIP to Supabase Storage bucket in background and returns public URL."""
        if not supabase_client:
            return None

        # Build the public URL immediately (it's deterministic)
        public_url = cls.get_archive_url(project_id, filename)

        # Do the actual upload in a background thread so it doesn't block the HTTP response
        def _do_upload():
            storage_path = f"{project_id}/{filename}"
            try:
                if isinstance(file_path_or_bytes, (Path, str)):
                    with open(file_path_or_bytes, "rb") as f:
                        file_content = f.read()
                else:
                    file_content = file_path_or_bytes

                supabase_client.storage.from_(SUPABASE_BUCKET_NAME).upload(
                    path=storage_path,
                    file=file_content,
                    file_options={"content-type": "application/zip", "upsert": "true"},
                )
                print(f"[Supabase Storage] Uploaded {storage_path} successfully")
            except Exception as e:
                print(f"[Supabase Storage] upload_archive error: {e}")

        thread = threading.Thread(target=_do_upload, daemon=True)
        thread.start()

        return public_url

    @classmethod
    def get_archive_url(cls, project_id: str, filename: str = "project.zip") -> Optional[str]:
        """Gets the public URL for an archive stored in Supabase Storage."""
        if not supabase_client:
            return None
        try:
            return supabase_client.storage.from_(SUPABASE_BUCKET_NAME).get_public_url(f"{project_id}/{filename}")
        except Exception as e:
            print(f"[Supabase Storage] get_archive_url error: {e}")
            return None
