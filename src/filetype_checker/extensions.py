# define which extensions are "expected" for each file type
# provide one helper function to compure (ext, mismatch) from a path and detection
# must be case insensitive

from pathlib import Path

EXTENSION_DB: dict[str, set[str]] = {
    "JPEG Image": {".jpg", ".jpeg", ".jpe"},
    "PNG Image": {".png"},
    "GIF Image": {".gif"},
    "PDF Document": {".pdf"},
    "ZIP Archive": {".zip", ".jar", ".war", ".ear"},
}


def get_ext_and_mismatch(path: str, file_type: str | None, matched: bool) -> tuple[str, bool]:
    ext = Path(path).suffix.lower()

    if ext == "":
        return ext, False

    if not matched:
        return ext, False  # Only report mismatch when magic matched

    key = file_type.strip() if file_type else None
    expected_exts = EXTENSION_DB.get(key) if key else None
    if expected_exts is None:
        return ext, False  # No expected extensions for unknown file types

    mismatch = ext not in expected_exts
    return ext, mismatch
