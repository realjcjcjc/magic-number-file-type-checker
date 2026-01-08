# Import necessary modules
import argparse

# Define MAX_MAGIC_BYTES constant
MAX_MAGIC_BYTES = 16

def identify_file_type(magic_number: bytes) -> str:
    magic_db = {
        b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "PNG Image",
        b"\xFF\xD8\xFF": "JPEG Image",
        b"GIF87a": "GIF Image",
        b"GIF89a": "GIF Image",
        b"%PDF-": "PDF Document",
        b"\x50\x4B\x03\x04": "ZIP Archive",
        b"\x50\x4B\x05\x06": "ZIP Archive",
        b"\x50\x4B\x07\x08": "ZIP Archive",
    }

    for magic, label in magic_db.items():
        if magic_number.startswith(magic):
            return label
        
    return "Unknown File Type"
    
def main() -> int: 
    parser = argparse.ArgumentParser(
        prog="ftcheck",
        description="Detect file type using magic numbers (scaffold).",
    )

    parser.add_argument("path", nargs="?", help="Path to the file to check.")
    args = parser.parse_args()

    if not args.path:
        print("ftcheck-ERROR: no file path provided.")
        return 0

    try:
        with open(args.path, "rb") as f:
            magic_number = f.read(MAX_MAGIC_BYTES)
            file_type = identify_file_type(magic_number)
            print(f"File Type: {file_type}")
            return 0
    except FileNotFoundError:
        print("ftcheck-ERROR: file not found.")
        return 1
    except Exception as e:
        print(f"ftcheck-ERROR: an error occurred: {e}")
        return 1
    
    return 1

if __name__ == "__main__":
    raise SystemExit(main())

