"""Unified dependency resolution engine."""
from pathlib import Path
from typing import List, Tuple
from app.models.project import DependencyItem
from app.resolver.requirements import RequirementsParser
from app.resolver.package_map import get_package_for_import
from app.analyzer.imports import ASTImportExtractor


class DependencyResolver:
    """Resolves dependencies from requirements files or infers them from AST import analysis."""

    @classmethod
    def resolve_dependencies(cls, project_root: Path) -> Tuple[List[DependencyItem], str, List[str]]:
        """
        Returns:
            (dependencies, dependency_source, warnings)
        """
        warnings: List[str] = []

        # 1. Check requirements.txt
        req_file = RequirementsParser.find_requirements_file(project_root)
        if req_file:
            deps = RequirementsParser.parse_requirements_txt(req_file)
            if deps:
                return deps, "requirements.txt", warnings

        # 2. Check pyproject.toml
        pyproject_file = project_root / "pyproject.toml"
        if pyproject_file.exists():
            deps = RequirementsParser.parse_pyproject_toml(pyproject_file)
            if deps:
                return deps, "pyproject.toml", warnings

        # 3. Fallback: AST Import Scanning
        third_party_imports, local_modules = ASTImportExtractor.scan_project_imports(project_root)

        if not third_party_imports:
            warnings.append("No external package dependencies detected in the project.")
            return [], "none", warnings

        warnings.append(
            "requirements.txt was not found. Dependencies were automatically inferred from Python imports. Please review the detected packages."
        )

        inferred_deps: List[DependencyItem] = []
        seen_packages = set()

        for imp in sorted(third_party_imports):
            package_name = get_package_for_import(imp)
            pkg_lower = package_name.lower()
            if pkg_lower in seen_packages:
                continue
            seen_packages.add(pkg_lower)

            mapped_from = imp if imp.lower() != package_name.lower() else None

            inferred_deps.append(
                DependencyItem(
                    name=package_name,
                    version_specifier="",
                    source="inferred_imports",
                    mapped_from=mapped_from,
                    enabled=True,
                    confidence=0.85 if mapped_from else 0.9,
                )
            )

        return inferred_deps, "inferred_imports", warnings
