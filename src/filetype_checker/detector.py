# Helper module to detect file types based on magic numbers

# Define MAX_MAGIC_BYTES constant
MAX_MAGIC_BYTES = 16


def get_file_type(magic_number: bytes) -> str:
    magic_db = {
        b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": "PNG Image",
        b"\xff\xd8\xff": "JPEG Image",
        b"GIF87a": "GIF Image",
        b"GIF89a": "GIF Image",
        b"%PDF-": "PDF Document",
        b"\x50\x4b\x03\x04": "ZIP Archive",
        b"\x50\x4b\x05\x06": "ZIP Archive",
        b"\x50\x4b\x07\x08": "ZIP Archive",
    }

    for magic, label in magic_db.items():
        if magic_number.startswith(magic):
            return label

    return "Unknown File Type"


def detect(path: str) -> str:
    try:
        with open(path, "rb") as f:
            magic_number = f.read(MAX_MAGIC_BYTES)
            return get_file_type(magic_number)
    except FileNotFoundError:
        return "ftcheck-ERROR: File not found"
    except IsADirectoryError:
        return "ftcheck-ERROR: Path is a directory"
    except PermissionError:
        return "ftcheck-ERROR: Permission denied"
    except Exception as e:
        return f"ftcheck-ERROR: {e}"