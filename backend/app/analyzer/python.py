"""Python runtime requirement and version detector."""
import re
from pathlib import Path
from typing import Optional


class PythonVersionDetector:
    """Detects Python version requirements from project configuration files."""

    DEFAULT_REQUIREMENT = ">=3.10"

    @classmethod
    def detect_version_requirement(cls, project_root: Path) -> str:
        # 1. Check runtime.txt (e.g., python-3.11.5)
        runtime_txt = project_root / "runtime.txt"
        if runtime_txt.exists():
            try:
                content = runtime_txt.read_text(encoding="utf-8").strip()
                match = re.search(r"python-(\d+\.\d+)", content, re.IGNORECASE)
                if match:
                    return f">={match.group(1)}"
            except Exception:
                pass

        # 2. Check pyproject.toml (e.g., requires-python = ">=3.11")
        pyproject_toml = project_root / "pyproject.toml"
        if pyproject_toml.exists():
            try:
                content = pyproject_toml.read_text(encoding="utf-8")
                match = re.search(r"""requires-python\s*=\s*['"]([^'"]+)['"]""", content, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            except Exception:
                pass

        # 3. Check setup.py or setup.cfg
        setup_py = project_root / "setup.py"
        if setup_py.exists():
            try:
                content = setup_py.read_text(encoding="utf-8")
                match = re.search(r"""python_requires\s*=\s*['"]([^'"]+)['"]""", content, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            except Exception:
                pass

        # 4. Check Pipfile
        pipfile = project_root / "Pipfile"
        if pipfile.exists():
            try:
                content = pipfile.read_text(encoding="utf-8")
                match = re.search(r"""python_version\s*=\s*['"]([^'"]+)['"]""", content, re.IGNORECASE)
                if match:
                    return f">={match.group(1).strip()}"
            except Exception:
                pass

        # Default fallback
        return cls.DEFAULT_REQUIREMENT
