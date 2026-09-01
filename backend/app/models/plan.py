"""Intermediate Installation Plan models."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RuntimeConfig(BaseModel):
    type: str = "python"
    version: str = ">=3.10"
    target_install_version: str = "3.12"


class ProjectDownloadConfig(BaseModel):
    project_id: str
    archive_name: str
    download_url: str
    target_directory_name: str


class EnvironmentConfig(BaseModel):
    type: str = "venv"
    path: str = ".venv"


class EntryPointConfig(BaseModel):
    command_type: str = "python"  # "python", "streamlit", "uvicorn", "flask"
    entry_file: str
    run_command: str


class InstallationPlan(BaseModel):
    plan_version: str = "1.0"
    project_id: str
    project_name: str
    runtime: RuntimeConfig
    project: ProjectDownloadConfig
    environment: EnvironmentConfig
    dependencies_source: str
    dependencies: List[str]
    entrypoint: EntryPointConfig
    pre_checks: List[str] = Field(default_factory=lambda: ["check_python", "check_disk_space"])
    validation_files: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
