"""Safe ZIP extraction with path traversal and zip bomb defenses."""
import os
import zipfile
from pathlib import Path
from typing import List, Tuple
from app.security.limits import SecurityLimits, SecurityLimitsException


class ZipValidationError(Exception):
    """Raised when a zip archive contains invalid or malicious contents."""
    pass


class SafeZipExtractor:
    """Safely extracts ZIP archives, guarding against Zip Slip (traversal) and Zip bombs."""

    @staticmethod
    def inspect_and_validate_zip(zip_path: Path) -> Tuple[int, int, List[str]]:
        """
        Inspects zip members without extracting to check:
        1. Directory traversal attacks
        2. Total uncompressed size
        3. Total file count
        4. Suspicious executable binaries
        Returns: (file_count, total_uncompressed_size, warnings)
        """
        if not zip_path.exists():
            raise ZipValidationError(f"Archive file not found: {zip_path}")

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                infolist = zf.infolist()
                file_count = len(infolist)
                total_uncompressed_size = 0
                warnings: List[str] = []

                if file_count > SecurityLimits.MAX_FILE_COUNT:
                    raise SecurityLimitsException(
                        f"Archive contains {file_count} entries, exceeding limit of {SecurityLimits.MAX_FILE_COUNT}."
                    )

                for info in infolist:
                    filename = info.filename
                    # Check for path traversal attempts
                    normalized_parts = Path(filename).parts
                    if ".." in normalized_parts:
                        raise ZipValidationError(
                            f"Path traversal detected in archive entry: {filename}"
                        )
                    if os.path.isabs(filename) or filename.startswith(("/", "\\")):
                        raise ZipValidationError(
                            f"Absolute path entry detected in archive: {filename}"
                        )

                    total_uncompressed_size += info.file_size
                    if total_uncompressed_size > SecurityLimits.MAX_EXTRACTED_SIZE:
                        raise SecurityLimitsException(
                            f"Extracted size exceeds safety limit of {SecurityLimits.MAX_EXTRACTED_SIZE / (1024*1024):.0f} MB."
                        )

                    # Check forbidden extensions
                    ext = Path(filename).suffix.lower()
                    if ext in SecurityLimits.FORBIDDEN_EXTENSIONS:
                        warnings.append(
                            f"Archive contains executable or binary file: {filename}"
                        )

                return file_count, total_uncompressed_size, warnings
        except zipfile.BadZipFile as e:
            raise ZipValidationError(f"Invalid or corrupted ZIP archive: {str(e)}")

    @classmethod
    def extract_safely(cls, zip_path: Path, target_dir: Path) -> List[Path]:
        """
        Safely extracts archive to target_dir.
        Ensures all resolved extracted paths are strictly under target_dir.
        """
        cls.inspect_and_validate_zip(zip_path)

        target_dir = target_dir.resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        extracted_files: List[Path] = []

        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.infolist():
                # Clean up filename
                member_path = member.filename.replace("\\", "/").lstrip("/")
                if not member_path:
                    continue

                dest_path = (target_dir / member_path).resolve()

                # Verify destination path is strictly within target_dir
                try:
                    dest_path.relative_to(target_dir)
                except ValueError:
                    raise ZipValidationError(
                        f"Security violation: archive entry '{member.filename}' extracts outside target directory."
                    )

                if member.is_dir():
                    dest_path.mkdir(parents=True, exist_ok=True)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as source, open(dest_path, "wb") as target:
                        target.write(source.read())
                    extracted_files.append(dest_path)

        return extracted_files
