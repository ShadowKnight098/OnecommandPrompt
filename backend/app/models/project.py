"""Project data models and schemas."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ProjectStatus(str, Enum):
    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    NEEDS_INPUT = "needs_input"
    READY = "ready"
    FAILED = "failed"
    EXPIRED = "expired"


class DependencyItem(BaseModel):
    name: str
    version_specifier: str = ""
    source: str = "requirements.txt"  # "requirements.txt", "inferred_import", "pyproject.toml", "user"
    mapped_from: Optional[str] = None  # e.g., "cv2" -> "opencv-python"
    enabled: bool = True
    confidence: float = 1.0  # 1.0 for explicit, 0.8 for mapped imports


class EntryPointCandidate(BaseModel):
    file_path: str
    score: int
    has_main_block: bool = False
    framework: Optional[str] = None  # e.g., "fastapi", "flask", "streamlit", "generic"
    preview_lines: List[str] = Field(default_factory=list)


class SecurityWarning(BaseModel):
    severity: str  # "warning", "info", "error"
    message: str
    file_path: Optional[str] = None


class ProjectAnalysis(BaseModel):
    project_id: str
    project_name: str
    description: Optional[str] = None
    language: str = "python"
    python_requirement: str = ">=3.10"
    entry_point: Optional[str] = None
    entry_point_framework: Optional[str] = None
    candidate_entry_points: List[EntryPointCandidate] = Field(default_factory=list)
    is_ambiguous_entrypoint: bool = False
    dependencies: List[DependencyItem] = Field(default_factory=list)
    dependency_source: str = "requirements.txt"  # "requirements.txt" or "inferred_imports"
    warnings: List[str] = Field(default_factory=list)
    security_warnings: List[SecurityWarning] = Field(default_factory=list)
    file_count: int = 0
    total_size_bytes: int = 0
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectRecord(BaseModel):
    id: str
    original_filename: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.UPLOADED
    error_message: Optional[str] = None
    analysis: Optional[ProjectAnalysis] = None
    archive_path: str
    extracted_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EntryPointSelectionRequest(BaseModel):
    entry_point: str


class DependenciesUpdateRequest(BaseModel):
    dependencies: List[DependencyItem]


class GenerateRequest(BaseModel):
    entry_point: Optional[str] = None
    dependencies: Optional[List[DependencyItem]] = None
    python_requirement: Optional[str] = None
