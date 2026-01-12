# Import necessary modules
import argparse
import json
import sys

from filetype_checker import detector, scanner
from filetype_checker.error import FtcheckError


# Main function for CLI
def main(argv=None) -> int:
    # Set up argument parser
    parser = argparse.ArgumentParser(
        prog="ftcheck",
        description="Detect file type using magic numbers.",
    )

    # Add arguments
    parser.add_argument("paths", nargs="+", help="paths to the file to check.")
    parser.add_argument("--json", action="store_true", help="output result in JSON format.")
    parser.add_argument("-r", "--recursive", action="store_true", 
                        help="recursively check files in directories.")
    args = parser.parse_args(argv)

    files, problems = scanner.expand_paths(args.paths, args.recursive)
    problem_occurred = bool(problems)

    # Print Errors encountered during path expansion
    for problem in problems:
        if args.json:
            payload = {
                "ok": False,
                "path": problem["details"]["path"],
                "error": {
                    "code": problem["code"],
                    "message": problem["message"],
                    "details": problem.get("details", None),
                }
            }
            print(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
        else:
            print(f"ftcheck: error: {problem['message']}", file=sys.stderr)

    # Perform detection
    try:
        for file in files:
            try: 
                file_report = detector.detect(file)

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
            except FtcheckError as e:
                if args.json:
                    payload = {
                        "ok": False,
                        "path": file,
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
                continue      
    except BrokenPipeError:
        return 0
    
    return 2 if problem_occurred else 0

if __name__ == "__main__":
    raise SystemExit(main())