"""Main project analyzer orchestrator."""
from pathlib import Path
from typing import List
from datetime import datetime, timezone
from app.models.project import ProjectAnalysis, SecurityWarning
from app.analyzer.python import PythonVersionDetector
from app.analyzer.entrypoint import EntryPointDetector
from app.resolver.resolver import DependencyResolver
from app.security.scanner import ProjectScanner
from app.security.limits import SecurityLimits


class ProjectAnalyzer:
    """Orchestrates comprehensive static analysis of an extracted project."""

    @classmethod
    def analyze_project(
        cls,
        project_id: str,
        project_name: str,
        extracted_root: Path,
    ) -> ProjectAnalysis:
        # 1. Normalize project root (handle single folder nested zip, e.g. project-main/)
        actual_root = cls._resolve_effective_root(extracted_root)

        # 2. Count files and size
        file_count = 0
        total_size = 0
        py_files_count = 0

        for f in actual_root.rglob("*"):
            if f.is_file():
                file_count += 1
                total_size += f.stat().st_size
                if f.suffix.lower() == ".py":
                    py_files_count += 1

        warnings: List[str] = []
        if py_files_count == 0:
            warnings.append("No Python source files (.py) detected in this project.")

        # 3. Detect Python Version Requirement
        python_req = PythonVersionDetector.detect_version_requirement(actual_root)

        # 4. Resolve Dependencies
        dependencies, dep_source, dep_warnings = DependencyResolver.resolve_dependencies(actual_root)
        warnings.extend(dep_warnings)

        # 5. Detect Entry Points
        entry_point, framework, candidates, is_ambiguous = EntryPointDetector.detect_entry_points(actual_root)

        if not entry_point:
            warnings.append("No obvious Python entry point was detected. You can select one manually.")
        elif is_ambiguous:
            warnings.append(f"Multiple possible entry points found ({len(candidates)} candidates). Please confirm your preferred entry point.")

        # 6. Security & Secrets Scanning
        security_warnings = ProjectScanner.scan_project(actual_root)

        return ProjectAnalysis(
            project_id=project_id,
            project_name=project_name,
            language="python",
            python_requirement=python_req,
            entry_point=entry_point,
            entry_point_framework=framework,
            candidate_entry_points=candidates,
            is_ambiguous_entrypoint=is_ambiguous,
            dependencies=dependencies,
            dependency_source=dep_source,
            warnings=warnings,
            security_warnings=security_warnings,
            file_count=file_count,
            total_size_bytes=total_size,
            analyzed_at=datetime.now(timezone.utc),
        )

    @classmethod
    def _resolve_effective_root(cls, root: Path) -> Path:
        """If zip extracted into a single top-level folder (e.g., repo-main/), use that folder."""
        children = [c for c in root.iterdir() if not c.name.startswith(".")]
        if len(children) == 1 and children[0].is_dir():
            return children[0]
        return root
