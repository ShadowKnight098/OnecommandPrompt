"""Entry point detection and scoring engine."""
from pathlib import Path
from typing import List, Tuple, Optional
import re
from app.models.project import EntryPointCandidate
from app.security.limits import SecurityLimits


class EntryPointDetector:
    """Scans and scores Python files to identify the most suitable entry point."""

    COMMON_ENTRY_NAMES = {
        "main.py": 40,
        "app.py": 35,
        "run.py": 30,
        "server.py": 30,
        "start.py": 25,
        "manage.py": 25,
        "cli.py": 20,
        "asgi.py": 15,
        "wsgi.py": 15,
    }

    IGNORE_PATTERNS = {
        "setup.py",
        "conftest.py",
        "__init__.py",
        "test_",
        "_test.py",
        "test/",
        "tests/",
        "migrations/",
    }

    @classmethod
    def score_file(cls, py_path: Path, project_root: Path) -> Optional[EntryPointCandidate]:
        rel_path = py_path.relative_to(project_root).as_posix()
        name_lower = py_path.name.lower()

        # Filter out tests and non-entry files
        for pattern in cls.IGNORE_PATTERNS:
            if pattern in rel_path.lower():
                return None

        score = 0
        has_main_block = False
        framework: Optional[str] = None
        preview_lines: List[str] = []

        try:
            content = py_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            preview_lines = [l.rstrip() for l in lines[:15] if l.strip()]
        except Exception:
            return None

        # 1. Filename heuristic
        if name_lower in cls.COMMON_ENTRY_NAMES:
            score += cls.COMMON_ENTRY_NAMES[name_lower]

        # 2. Top-level file bonus
        if len(py_path.relative_to(project_root).parts) == 1:
            score += 20

        # 3. Main block check: if __name__ == '__main__':
        if re.search(r"""if\s+__name__\s*==\s*['"]__main__['"]""", content):
            score += 45
            has_main_block = True

        # 4. Framework heuristics
        if "FastAPI(" in content or "uvicorn.run" in content:
            score += 25
            framework = "fastapi"
        elif "Flask(" in content or "app.run(" in content:
            score += 25
            framework = "flask"
        elif "streamlit" in content and ("st.title" in content or "st.write" in content or "st.sidebar" in content):
            score += 25
            framework = "streamlit"
        elif "gradio" in content or "gr.Interface" in content:
            score += 20
            framework = "gradio"
        elif "argparse.ArgumentParser" in content or "click.command" in content or "typer.Typer" in content:
            score += 15
            framework = "cli"

        if score <= 0:
            return None

        return EntryPointCandidate(
            file_path=rel_path,
            score=score,
            has_main_block=has_main_block,
            framework=framework,
            preview_lines=preview_lines[:8],
        )

    @classmethod
    def detect_entry_points(cls, project_root: Path) -> Tuple[Optional[str], Optional[str], List[EntryPointCandidate], bool]:
        """
        Returns:
            (selected_entry_point, detected_framework, candidate_list, is_ambiguous)
        """
        candidates: List[EntryPointCandidate] = []

        for py_path in project_root.rglob("*.py"):
            if any(part in SecurityLimits.IGNORED_DIRS for part in py_path.parts):
                continue
            cand = cls.score_file(py_path, project_root)
            if cand:
                candidates.append(cand)

        # Sort candidates by score descending
        candidates.sort(key=lambda c: c.score, reverse=True)

        if not candidates:
            # Fallback: check if any py file exists in root
            root_py_files = [p.name for p in project_root.glob("*.py") if p.name != "__init__.py"]
            if root_py_files:
                first = root_py_files[0]
                return first, None, [EntryPointCandidate(file_path=first, score=10)], False
            return None, None, [], False

        top = candidates[0]

        # Check ambiguity: if top 2 candidates have scores within 15 points of each other
        if len(candidates) > 1 and candidates[0].score >= 30:
            second = candidates[1]
            if second.score >= 30 and (top.score - second.score) < 15:
                # Ambiguous entry points, e.g. main.py vs app.py
                return top.file_path, top.framework, candidates[:5], True

        return top.file_path, top.framework, candidates[:5], False
