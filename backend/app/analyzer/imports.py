"""AST-based Python import extraction and project-local module detection."""
import ast
from pathlib import Path
from typing import Set, Dict, List, Tuple
from app.analyzer.standard_library import is_standard_library
from app.security.limits import SecurityLimits


class ASTImportExtractor:
    """Extracts top-level third-party imports by parsing AST and filtering stdlib and local modules."""

    @classmethod
    def get_local_modules(cls, project_root: Path) -> Set[str]:
        """
        Discovers all Python modules and packages defined inside the project.
        Examples:
        - `utils.py` -> "utils"
        - `helpers/__init__.py` -> "helpers"
        - `helpers/config.py` -> "helpers", "helpers.config"
        """
        local_modules: Set[str] = set()

        for py_path in project_root.rglob("*.py"):
            # Skip ignored directories
            if any(part in SecurityLimits.IGNORED_DIRS for part in py_path.parts):
                continue

            rel_path = py_path.relative_to(project_root)
            parts = list(rel_path.parts)

            # File stem as module name
            stem = py_path.stem
            if stem != "__init__":
                local_modules.add(stem)

            # Top-level directory packages
            if len(parts) > 1:
                local_modules.add(parts[0])

            # Full dotted module path relative to root
            dotted_parts = parts[:-1]
            if stem != "__init__":
                dotted_parts.append(stem)
            if dotted_parts:
                local_modules.add(".".join(dotted_parts))

        return local_modules

    @classmethod
    def extract_imports_from_file(cls, file_path: Path) -> Set[str]:
        """Extracts top-level imported module names from a single Python file using AST."""
        imported_modules: Set[str] = set()

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, ValueError, Exception):
            # If ast.parse fails due to syntax or encoding, fallback to basic regex parsing
            return cls._fallback_regex_imports(file_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # e.g., 'import numpy as np' -> 'numpy'
                    top_name = alias.name.split(".")[0].strip()
                    if top_name:
                        imported_modules.add(top_name)

            elif isinstance(node, ast.ImportFrom):
                # Ignore relative imports (e.g., 'from .utils import helper')
                if node.level and node.level > 0:
                    continue
                if node.module:
                    top_name = node.module.split(".")[0].strip()
                    if top_name:
                        imported_modules.add(top_name)

        return imported_modules

    @classmethod
    def _fallback_regex_imports(cls, file_path: Path) -> Set[str]:
        """Simple regex fallback when AST parsing fails."""
        import re
        imported = set()
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("#"):
                    continue
                match_import = re.match(r"^import\s+([a-zA-Z0-9_]+)", line)
                if match_import:
                    imported.add(match_import.group(1))
                match_from = re.match(r"^from\s+([a-zA-Z0-9_]+)", line)
                if match_from:
                    imported.add(match_from.group(1))
        except Exception:
            pass
        return imported

    @classmethod
    def scan_project_imports(cls, project_root: Path) -> Tuple[Set[str], Set[str]]:
        """
        Scans all Python files in project_root.
        Returns:
            (third_party_imports, local_modules)
        """
        local_modules = cls.get_local_modules(project_root)
        all_raw_imports: Set[str] = set()

        for py_file in project_root.rglob("*.py"):
            if any(part in SecurityLimits.IGNORED_DIRS for part in py_file.parts):
                continue
            imports = cls.extract_imports_from_file(py_file)
            all_raw_imports.update(imports)

        # Filter out stdlib and project-local modules
        third_party_imports: Set[str] = set()
        for imp in all_raw_imports:
            if is_standard_library(imp):
                continue
            if imp in local_modules:
                continue
            third_party_imports.add(imp)

        return third_party_imports, local_modules
