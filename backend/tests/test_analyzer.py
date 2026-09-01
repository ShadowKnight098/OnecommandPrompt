"""Tests for AST import extractor, stdlib filter, and python version detector."""
from pathlib import Path
import pytest
from app.analyzer.standard_library import is_standard_library
from app.analyzer.imports import ASTImportExtractor
from app.analyzer.python import PythonVersionDetector


def test_standard_library_detection():
    assert is_standard_library("os") is True
    assert is_standard_library("sys") is True
    assert is_standard_library("json") is True
    assert is_standard_library("asyncio") is True
    assert is_standard_library("pathlib") is True
    assert is_standard_library("numpy") is False
    assert is_standard_library("flask") is False
    assert is_standard_library("cv2") is False


def test_ast_import_extraction(tmp_path):
    # Setup sample project with python files
    main_py = tmp_path / "main.py"
    main_py.write_text("""
import os
import sys
import numpy as np
import pandas as pd
from PIL import Image
from .local_rel import something
from helpers.config import Config

print('Running app')
""", encoding="utf-8")

    helpers_dir = tmp_path / "helpers"
    helpers_dir.mkdir()
    config_py = helpers_dir / "config.py"
    config_py.write_text("class Config: pass", encoding="utf-8")

    third_party, local_mods = ASTImportExtractor.scan_project_imports(tmp_path)

    # numpy, pandas, PIL are third-party
    assert "numpy" in third_party
    assert "pandas" in third_party
    assert "PIL" in third_party

    # os and sys should be filtered out because they are in stdlib
    assert "os" not in third_party
    assert "sys" not in third_party

    # helpers and helpers.config should be detected as local
    assert "helpers" in local_mods or "helpers.config" in local_mods
    assert "helpers" not in third_party


def test_python_version_detection(tmp_path):
    # Test pyproject.toml
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "demo"
requires-python = ">=3.11"
""", encoding="utf-8")

    req = PythonVersionDetector.detect_version_requirement(tmp_path)
    assert req == ">=3.11"
