"""
Custom exceptions for PDF Summary AI application.
"""


class PDFSummaryError(Exception):
    """Base exception for PDF Summary application."""

    def __init__(self, message: str, code: str = "GENERAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ValidationError(PDFSummaryError):
    """Exception raised during file validation."""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class PDFParsingError(PDFSummaryError):
    """Exception raised during PDF parsing."""

    def __init__(self, message: str):
        super().__init__(message, "PDF_PARSING_ERROR")


class OpenAIServiceError(PDFSummaryError):
    """Exception raised during OpenAI API calls."""

    def __init__(self, message: str):
        super().__init__(message, "OPENAI_SERVICE_ERROR")


class DocumentServiceError(PDFSummaryError):
    """Exception raised during document service operations."""

    def __init__(self, message: str):
        super().__init__(message, "DOCUMENT_SERVICE_ERROR")


class FileTooLargeError(ValidationError):
    """Exception raised when uploaded file is too large."""

    def __init__(self, file_size: int, max_size: int):
        message = f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        super().__init__(message)


class UnsupportedFileTypeError(ValidationError):
    """Exception raised when uploaded file type is not supported."""

    def __init__(self, file_extension: str, allowed_extensions: set):
        message = f"File type '{file_extension}' not supported. Allowed: {', '.join(allowed_extensions)}"
        super().__init__(message)
