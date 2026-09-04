from pathlib import Path
from typing import List
from datetime import datetime, timezone
from app.models.project import ProjectAnalysis, SecurityWarning
from app.analyzer.python import PythonVersionDetector
from app.analyzer.entrypoint import EntryPointDetector
from app.analyzer.web import WebProjectAnalyzer
from app.resolver.resolver import DependencyResolver
from app.security.scanner import ProjectScanner
from app.security.limits import SecurityLimits


class ProjectAnalyzer:
    """Orchestrates comprehensive static analysis for Python, HTML/CSS, React, Vite, and Full-Stack projects."""

    @classmethod
    def analyze_project(
        cls,
        project_id: str,
        project_name: str,
        extracted_root: Path,
    ) -> ProjectAnalysis:
        # 1. Normalize project root (handle single folder nested zip, e.g. project-main/)
        actual_root = cls._resolve_effective_root(extracted_root)

        # 2. Count files and detect languages
        file_count = 0
        total_size = 0
        py_files_count = 0
        html_files_count = 0
        js_files_count = 0

        for f in actual_root.rglob("*"):
            if f.is_file():
                file_count += 1
                total_size += f.stat().st_size
                ext = f.suffix.lower()
                if ext == ".py":
                    py_files_count += 1
                elif ext in [".html", ".htm"]:
                    html_files_count += 1
                elif ext in [".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"]:
                    js_files_count += 1

        warnings: List[str] = []

        # 3. Perform Web / Node Analysis
        web_res = WebProjectAnalyzer.scan_web_project(actual_root)
        is_web = web_res["is_web_project"]

        # 4. Classify Project Domain (Python, Web, or Full-Stack)
        if py_files_count > 0 and (is_web and (actual_root / "package.json").exists() or html_files_count > 0):
            domain = "fullstack"
        elif is_web and py_files_count == 0:
            domain = "web"
        else:
            domain = "python"

        # 5. Language-Specific Resolution
        python_req = ">=3.10"
        node_req = web_res["web_metadata"].node_requirement if is_web else None

        if domain == "python":
            python_req = PythonVersionDetector.detect_version_requirement(actual_root)
            dependencies, dep_source, dep_warnings = DependencyResolver.resolve_dependencies(actual_root)
            warnings.extend(dep_warnings)
            entry_point, framework, candidates, is_ambiguous = EntryPointDetector.detect_entry_points(actual_root)
            project_type = framework if framework in ["fastapi", "flask", "streamlit", "gradio"] else "python"
            language = "python"

        elif domain == "web":
            dependencies = web_res["dependencies"]
            dep_source = web_res["dependency_source"]
            candidates = web_res["candidate_entry_points"]
            entry_point = web_res["entry_point"]
            framework = web_res["ui_framework"] or "html5"
            is_ambiguous = len(candidates) > 1 and not (actual_root / "index.html").exists()
            project_type = web_res["project_type"]
            language = "typescript" if any(f.suffix in [".ts", ".tsx"] for f in actual_root.rglob("*") if f.is_file()) else ("javascript" if js_files_count > 0 else "html")

        else:  # domain == "fullstack"
            python_req = PythonVersionDetector.detect_version_requirement(actual_root)
            py_deps, py_source, dep_warnings = DependencyResolver.resolve_dependencies(actual_root)
            warnings.extend(dep_warnings)
            dependencies = py_deps + web_res["dependencies"]
            dep_source = f"{py_source} + {web_res['dependency_source']}"
            
            py_entry, py_framework, py_candidates, _ = EntryPointDetector.detect_entry_points(actual_root)
            candidates = py_candidates + web_res["candidate_entry_points"]
            entry_point = py_entry or web_res["entry_point"]
            framework = f"{py_framework or 'python'} + {web_res['ui_framework'] or 'web'}"
            is_ambiguous = False
            project_type = "fullstack"
            language = "fullstack"

        # Check entrypoint presence
        if not entry_point:
            warnings.append("No obvious entry point was detected. You can select one manually.")
        elif is_ambiguous:
            warnings.append(f"Multiple possible entry points found ({len(candidates)} candidates). Please confirm your preferred entry point.")

        # 6. Security & Secrets Scanning
        security_warnings = ProjectScanner.scan_project(actual_root)

        return ProjectAnalysis(
            project_id=project_id,
            project_name=project_name,
            language=language,
            project_type=project_type,
            python_requirement=python_req,
            node_requirement=node_req,
            entry_point=entry_point,
            entry_point_framework=framework,
            candidate_entry_points=candidates,
            is_ambiguous_entrypoint=is_ambiguous,
            dependencies=dependencies,
            dependency_source=dep_source,
            web_metadata=web_res["web_metadata"] if is_web else None,
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
