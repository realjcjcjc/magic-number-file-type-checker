# Helper module to detect file types based on magic numbers
import os

from filetype_checker.error import (
    FileReadError,
    PathIsDirectoryError,
    PathNotFoundError,
    PermissionDeniedError,
)

# Define a simple magic number database
MAGIC_DB = [
    (0, b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a", "PNG Image"),
    (0, b"\xff\xd8\xff", "JPEG Image"),
    (0, b"GIF87a", "GIF Image"),
    (0, b"GIF89a", "GIF Image"),
    (0, b"%PDF-", "PDF Document"),
    (0, b"\x50\x4b\x03\x04", "ZIP Archive"),
    (0, b"\x50\x4b\x05\x06", "ZIP Archive"),
    (0, b"\x50\x4b\x07\x08", "ZIP Archive"),
]

# Define the maximum number of bytes to read for magic number detection
MAX_MAGIC_BYTES = max(offset + len(magic) for offset, magic, _ in MAGIC_DB)

# Match the magic number against the database
def match_magic(magic_number: bytes) -> dict:
    for offset, magic, label in MAGIC_DB:
        end = offset + len(magic)
        if len(magic_number) >= end and magic_number[offset:end] == magic:
            return {
                "file_type": label,
                "matched": True,
                "offset": offset,
                "signature": magic.hex().upper(),
            }
        
    return {
        "file_type": "Unknown File Type",
        "matched": False,
        "offset": None,
        "signature": None,
    }

def detect(path: str) -> dict:
    file_report = {
        "ok": False,
        "path": path,
        "file_type": None,
        "size_bytes": None,
        "magic": {
            "matched": False,
            "offset": None,
            "signature": None,
        },
    }

    try:
        size_bytes = os.stat(path).st_size 
        with open(path, "rb") as f: 
            magic_number = f.read(MAX_MAGIC_BYTES)
    except FileNotFoundError as e:
        raise PathNotFoundError(path) from e
    except IsADirectoryError as e:
        raise PathIsDirectoryError(path) from e
    except PermissionError as e:
        raise PermissionDeniedError(path) from e
    except OSError as e:
        raise FileReadError(path, os_error=str(e)) from e

    magic_report = match_magic(magic_number)
    
    file_report["ok"] = True
    file_report["file_type"] = magic_report["file_type"]
    file_report["size_bytes"] = size_bytes
    file_report["magic"]["matched"] = magic_report["matched"]
    file_report["magic"]["offset"] = magic_report["offset"]
    file_report["magic"]["signature"] = magic_report["signature"]

    return file_report