"""Tests for ZIP archive security and traversal protection."""
import io
import zipfile
import pytest
from pathlib import Path
from app.security.zip_validator import SafeZipExtractor, ZipValidationError
from app.security.limits import SecurityLimitsException, SecurityLimits


def test_safe_zip_extraction(tmp_path):
    """Verifies that legitimate files extract safely within the target directory."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("main.py", "print('hello world')")
        zf.writestr("subfolder/utils.py", "def add(a, b): return a + b")

    zip_file = tmp_path / "test.zip"
    zip_file.write_bytes(zip_buffer.getvalue())

    dest_dir = tmp_path / "extracted"
    extracted = SafeZipExtractor.extract_safely(zip_file, dest_dir)

    assert len(extracted) == 2
    assert (dest_dir / "main.py").exists()
    assert (dest_dir / "subfolder" / "utils.py").exists()
    assert (dest_dir / "main.py").read_text() == "print('hello world')"


def test_zip_slip_traversal_detection(tmp_path):
    """Verifies that Zip Slip directory traversal (e.g. ../../evil.py) is rejected."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # Create a malicious zip entry trying to escape
        zf.writestr("../../evil.py", "print('pwned')")

    zip_file = tmp_path / "malicious.zip"
    zip_file.write_bytes(zip_buffer.getvalue())

    dest_dir = tmp_path / "extracted"
    with pytest.raises(ZipValidationError) as excinfo:
        SafeZipExtractor.extract_safely(zip_file, dest_dir)

    assert "traversal" in str(excinfo.value).lower()


def test_absolute_path_zip_rejection(tmp_path):
    """Verifies that absolute path entries are rejected."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("/etc/passwd", "root:x:0:0")

    zip_file = tmp_path / "abs.zip"
    zip_file.write_bytes(zip_buffer.getvalue())

    dest_dir = tmp_path / "extracted"
    with pytest.raises(ZipValidationError):
        SafeZipExtractor.extract_safely(zip_file, dest_dir)
