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
    (0, b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a", "PNG Image", 100),
    (0, b"\xff\xd8\xff", "JPEG Image", 80),
    (0, b"GIF87a", "GIF Image", 70),
    (0, b"GIF89a", "GIF Image", 70),
    (0, b"%PDF-", "PDF Document", 90),
    (0, b"\x50\x4b\x03\x04", "ZIP Archive", 60),
    (0, b"\x50\x4b\x05\x06", "ZIP Archive", 60),
    (0, b"\x50\x4b\x07\x08", "ZIP Archive", 60),
]

# Define the maximum number of bytes to read for magic number detection
MAX_MAGIC_BYTES = max(offset + len(magic) for offset, magic, _, _priority in MAGIC_DB)


# Match the magic number against the database
def match_magic(magic_number: bytes) -> dict:
    best = None

    for index, (offset, magic, label, priority) in enumerate(MAGIC_DB):
        end = offset + len(magic)
        if len(magic_number) >= end and magic_number[offset:end] == magic:
            candidate = (priority, len(magic), -index, offset, magic, label)
            if best is None or candidate > best:
                best = candidate

    if best is None:
        return {
            "file_type": "Unknown File Type",
            "matched": False,
            "offset": None,
            "signature": None,
        }

    _, _, _, offset, magic, label = best
    return {
        "file_type": label,
        "matched": True,
        "offset": offset,
        "signature": magic.hex().upper(),
        "rule": {
            "priority": best[0],
            "length": best[1],
        },
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
        with open(path, "rb") as f:
            size_bytes = os.fstat(f.fileno()).st_size
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
