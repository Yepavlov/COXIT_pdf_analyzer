from pathlib import Path

from fastapi import UploadFile

from src.app.config import get_settings
from src.app.utils.exceptions import FileTooLargeError, UnsupportedFileTypeError

settings = get_settings()


def validate_file_or_raise(file: UploadFile) -> None:
    """Validates file size and type, raising custom exceptions on failure."""
    if file.size > settings.max_file_size:
        raise FileTooLargeError(file.size, settings.max_file_size)

    suffix = Path(file.filename).suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise UnsupportedFileTypeError(suffix, settings.allowed_extensions)
