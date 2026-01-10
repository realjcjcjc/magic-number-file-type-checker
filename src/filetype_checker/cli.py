# Import necessary modules
import argparse
import json
import sys

from filetype_checker import detector
from filetype_checker.error import FtcheckError


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="ftcheck",
        description="Detect file type using magic numbers.",
    )

    parser.add_argument("path", nargs="?", help="path to the file to check.")
    parser.add_argument("--json", action="store_true", help="output result in JSON format.")
    args = parser.parse_args(argv)

    if not args.path:
        if args.json:
            payload = {
                "ok": False,
                "path": None,
                "error": {
                    "code": "USAGE",
                    "message": "No file path provided.",
                }
            }
            print(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
        else:                  
            print("ftcheck: error: no file path provided.", file=sys.stderr)
        return 2

    try:
        file_report = detector.detect(args.path)

        if args.json:
            print(json.dumps(file_report, ensure_ascii=False, separators=(',', ':')))
        else:
            path = file_report["path"]
            file_type = file_report["file_type"]
            size = file_report["size_bytes"]
            magic = file_report["magic"]
            matched = "yes" if magic["matched"] else "no"
            offset = magic["offset"] if magic["offset"] is not None else "N/A"
            signature = magic["signature"] if magic["signature"] is not None else "N/A"

            print(f"{path}: {file_type}, matched={matched}, size={size}, "
                  f"offset={offset}, signature={signature}")
        return 0
    except BrokenPipeError:
        return 0
    except FtcheckError as e:
        if args.json:
            payload = {
                "ok": False,
                "path": args.path,
                "error": {
                    "code": e.code,
                    "message": str(e),
                }
            }
            if getattr(e, "details", None):
                payload["error"]["details"] = e.details
            print(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
        else:
            print(f"ftcheck: error: {str(e)}", file=sys.stderr)

        return e.exit_code

if __name__ == "__main__":
    raise SystemExit(main())