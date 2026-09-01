"""Security limits and constraints configuration and checks."""
from app.config import (
    MAX_UPLOAD_SIZE_BYTES,
    MAX_EXTRACTED_SIZE_BYTES,
    MAX_FILE_COUNT,
    MAX_PATH_DEPTH,
)


class SecurityLimitsException(Exception):
    """Raised when an upload or extracted archive violates security limits."""
    pass


class SecurityLimits:
    MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE_BYTES
    MAX_EXTRACTED_SIZE = MAX_EXTRACTED_SIZE_BYTES
    MAX_FILE_COUNT = MAX_FILE_COUNT
    MAX_PATH_DEPTH = MAX_PATH_DEPTH

    # Forbidden file extensions in ZIP archives
    FORBIDDEN_EXTENSIONS = {
        ".exe",
        ".bat",
        ".cmd",
        ".msi",
        ".vbs",
        ".scr",
        ".pif",
        ".com",
        ".dll",
        ".so",
        ".dylib",
    }

    # Ignored directories / files during scanning
    IGNORED_DIRS = {
        ".git",
        ".svn",
        ".hg",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv",
        "env",
        "node_modules",
        ".idea",
        ".vscode",
    }

    @classmethod
    def check_upload_size(cls, size_bytes: int):
        if size_bytes > cls.MAX_UPLOAD_SIZE:
            mb = cls.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise SecurityLimitsException(
                f"File size ({size_bytes / (1024 * 1024):.1f} MB) exceeds maximum allowed upload limit of {mb:.0f} MB."
            )
