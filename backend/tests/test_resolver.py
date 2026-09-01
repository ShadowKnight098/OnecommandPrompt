"""Tests for requirements parsing and package mapping."""
from pathlib import Path
from app.resolver.requirements import RequirementsParser
from app.resolver.package_map import get_package_for_import
from app.resolver.resolver import DependencyResolver


def test_package_map_translations():
    assert get_package_for_import("cv2") == "opencv-python"
    assert get_package_for_import("PIL") == "Pillow"
    assert get_package_for_import("sklearn") == "scikit-learn"
    assert get_package_for_import("yaml") == "PyYAML"
    assert get_package_for_import("bs4") == "beautifulsoup4"
    assert get_package_for_import("dotenv") == "python-dotenv"
    assert get_package_for_import("requests") == "requests"


def test_requirements_txt_parser(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("""
# Core dependencies
fastapi>=0.100.0
uvicorn[standard]==0.24.0 # For ASGI
pydantic>=2.0
-r other.txt
--extra-index-url https://example.com
numpy
""", encoding="utf-8")

    items = RequirementsParser.parse_requirements_txt(req_file)
    names = [item.name for item in items]

    assert "fastapi" in names
    assert "pydantic" in names
    assert "numpy" in names
    assert len(items) >= 3


def test_resolver_inferred_fallback(tmp_path):
    app_py = tmp_path / "app.py"
    app_py.write_text("""
import cv2
import numpy as np
from PIL import Image
""", encoding="utf-8")

    deps, source, warnings = DependencyResolver.resolve_dependencies(tmp_path)
    assert source == "inferred_imports"
    names = [d.name for d in deps]
    assert "opencv-python" in names
    assert "Pillow" in names
    assert "numpy" in names
