"""Requirements and dependency configuration parser."""
from pathlib import Path
from typing import List, Optional, Tuple
import re
from app.models.project import DependencyItem


class RequirementsParser:
    """Parses requirements.txt, pyproject.toml, and Pipfile to extract explicit dependencies."""

    SPECIFIER_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)\s*([<>=!~].*)?$")

    @classmethod
    def find_requirements_file(cls, project_root: Path) -> Optional[Path]:
        """Finds primary requirements file in project."""
        candidates = [
            project_root / "requirements.txt",
            project_root / "requirements.in",
            project_root / "requirements" / "base.txt",
            project_root / "requirements" / "prod.txt",
            project_root / "requirements" / "common.txt",
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                return c

        # Any file named requirements*.txt in root
        for f in project_root.glob("requirements*.txt"):
            if f.is_file():
                return f
        return None

    @classmethod
    def parse_requirements_txt(cls, file_path: Path) -> List[DependencyItem]:
        items: List[DependencyItem] = []
        if not file_path.exists():
            return items

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for raw_line in content.splitlines():
                line = raw_line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                # Skip options / flags like -r, -i, --extra-index-url, -f
                if line.startswith("-") or line.startswith("--"):
                    continue

                # Strip inline comments
                if " #" in line:
                    line = line.split(" #", 1)[0].strip()

                # Separate environment markers (e.g. ; sys_platform == 'win32')
                marker = ""
                if ";" in line:
                    parts = line.split(";", 1)
                    line = parts[0].strip()
                    marker = parts[1].strip()

                # Parse package name and version specifier
                match = cls.SPECIFIER_REGEX.match(line)
                if match:
                    pkg_name = match.group(1).strip()
                    specifier = (match.group(2) or "").strip()
                    items.append(
                        DependencyItem(
                            name=pkg_name,
                            version_specifier=specifier,
                            source="requirements.txt",
                            enabled=True,
                            confidence=1.0,
                        )
                    )
        except Exception:
            pass

        return items

    @classmethod
    def parse_pyproject_toml(cls, file_path: Path) -> List[DependencyItem]:
        """Extracts dependencies from pyproject.toml [project.dependencies]."""
        items: List[DependencyItem] = []
        if not file_path.exists():
            return items

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            # Simple line parsing to avoid external toml dependency
            in_deps_section = False
            for raw_line in content.splitlines():
                line = raw_line.strip()
                if line.startswith("[project.dependencies]") or line.startswith("dependencies = ["):
                    in_deps_section = True
                    continue
                if in_deps_section:
                    if line.startswith("[") or line.startswith("]"):
                        if line.startswith("]"):
                            break
                        continue
                    # Match string in array: "requests>=2.28", 'numpy'
                    match_str = re.search(r"""['"]([a-zA-Z0-9_\-\.\s<>=!~]+)['"]""", line)
                    if match_str:
                        dep_str = match_str.group(1).strip()
                        match = cls.SPECIFIER_REGEX.match(dep_str)
                        if match:
                            pkg_name = match.group(1).strip()
                            specifier = (match.group(2) or "").strip()
                            items.append(
                                DependencyItem(
                                    name=pkg_name,
                                    version_specifier=specifier,
                                    source="pyproject.toml",
                                    enabled=True,
                                    confidence=1.0,
                                )
                            )
        except Exception:
            pass

        return items
