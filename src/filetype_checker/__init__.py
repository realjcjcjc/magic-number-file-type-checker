from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("file-type-checker")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .error import (
    CliUsageError,
    FileReadError,
    FtcheckError,
    InternalDetectionError,
    InvalidPathArgumentError,
    JsonSerializationError,
    NotARegularFileError,
    OutputWriteError,
    PathIsDirectoryError,
    PathNotFoundError,
    PermissionDeniedError,
    SignatureDatabaseError,
    SignatureParseError,
)

__all__ = [
    "__version__",
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