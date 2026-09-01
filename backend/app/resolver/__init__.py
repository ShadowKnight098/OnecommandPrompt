"""Resolver package."""
from .package_map import IMPORT_TO_PACKAGE_MAP, get_package_for_import
from .requirements import RequirementsParser
from .resolver import DependencyResolver

__all__ = [
    "IMPORT_TO_PACKAGE_MAP",
    "get_package_for_import",
    "RequirementsParser",
    "DependencyResolver",
]
