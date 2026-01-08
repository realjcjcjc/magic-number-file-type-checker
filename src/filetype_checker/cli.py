# Import necessary modules
import argparse

from filetype_checker import detector


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ftcheck",
        description="Detect file type using magic numbers (scaffold).",
    )

    parser.add_argument("path", nargs="?", help="Path to the file to check.")
    args = parser.parse_args()

    if not args.path:
        print("ftcheck-ERROR: no file path provided.")
        return 1

    try:
        result = detector.detect(args.path)
        print(result)
        return 0
    except FileNotFoundError:
        print("ftcheck-ERROR: File not found")
        return 1
    except IsADirectoryError:
        print("ftcheck-ERROR: Path is a directory")
        return 1
    except PermissionError:
        print("ftcheck-ERROR: Permission denied")
        return 1
    except Exception as e:
        print(f"ftcheck-ERROR: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())