from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


# Base exception for filetype checker errors
@dataclass
class FtcheckError(Exception):
    """Base exception for filetype checker errors."""
    code: str
    message: str
    exit_code: int = 1
    details: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

# Path related errors
class PathNotFoundError(FtcheckError):
    """Exception raised when the specified path is not found."""
    
    def __init__(self, path: str, message: Optional[str] = None) -> None:
        super().__init__(
            code = "ENOENT",
            message = message or f"File not found: {path}",
            exit_code = 3,
            details = {"path": path},
        )

class PermissionDeniedError(FtcheckError):
    """Exception raised when permission is denied for the specified path."""
    
    def __init__(self, path: str, message: Optional[str] = None) -> None:
        super().__init__(
            code = "EACCES",
            message = message or f"Permission denied: {path}",
            exit_code = 4,
            details = {"path": path},
        )

class PathIsDirectoryError(FtcheckError):
    """Exception raised when the specified path is a directory."""
    
    def __init__(self, path: str, message: Optional[str] = None) -> None:
        super().__init__(
            code = "EISDIR",
            message = message or f"Path is a directory: {path}",
            exit_code = 5,
            details = {"path": path},
        )

class NotARegularFileError(FtcheckError):
    """Exception raised when the specified path is not a regular file."""
    
    def __init__(self, path: str, message: Optional[str] = None) -> None:
        super().__init__(
            code = "ENOTFILE",
            message = message or f"Not a regular file: {path}",
            exit_code = 5,
            details = {"path": path},
        )

class FileReadError(FtcheckError):
    """Exception raised when there is an error reading the file."""
    
    def __init__(self, path:str, message: Optional[str] = None) -> None:
        super().__init__(
            code = "EIO",
            message = message or f"Error reading file: {path}",
            exit_code = 1,
            details = {"path": path},
        )

# CLI related errors
class CliUsageError(FtcheckError):
    """Exception raised for CLI usage errors."""
    
    def __init__(self, message: str = "Invalid CLI usage.") -> None:
        super().__init__(
            code = "USAGE",
            message = message, 
            exit_code = 2,
            details = None,
        )

class InvalidPathArgumentError(FtcheckError):
    """Exception raised for invalid path arguments in CLI."""
    
    def __init__(self, path: str, message: str = "Invalid path argument.") -> None:
        super().__init__(
            code = "BAD_PATH",
            message = message, 
            exit_code = 2,
            details = {"path": path},
        )

class SignatureDatabaseError(FtcheckError):
    """Exception raised for errors related to the signature database."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            code = "SIG_DB",
            message = message or "Signature database error",
            exit_code = 1,
            details = None,
        )

class SignatureParseError(FtcheckError):
    """Exception raised for errors parsing the signature database."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            code = "SIG_PARSE",
            message = message or "Signature parse error",
            exit_code = 1,
            details = None,
        )

class InternalDetectionError(FtcheckError):
    """Exception raised for internal errors during detection."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            code = "INTERNAL",
            message = message or "Internal detection error",
            exit_code = 1,
            details = None,
        )

class JsonSerializationError(FtcheckError):
    """Exception raised for JSON serialization/deserialization errors."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            code = "JSON_ENCODE",
            message = message or "JSON serialization error",
            exit_code = 1,
            details = None,
        )

class OutputWriteError(FtcheckError):
    """Exception raised for errors writing output."""
    
    def __init__(self, message: str = "Output write error.") -> None:
        super().__init__(
            code = "EPIPE",
            message = message,
            exit_code = 1,
            details = None,
        )

__all__ = [
    "FtcheckError",
    "PathNotFoundError",
    "PermissionDeniedError",
    "PathIsDirectoryError",
    "NotARegularFileError",
    "FileReadError",
    "CliUsageError",
    "InvalidPathArgumentError",
    "SignatureDatabaseError",
    "SignatureParseError",
    "InternalDetectionError",
    "JsonSerializationError",
    "OutputWriteError",
]

