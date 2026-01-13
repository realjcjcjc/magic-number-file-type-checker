# Import necessary modules
import argparse
import sys

from filetype_checker import detector, reporting, scanner
from filetype_checker.error import FtcheckError
from filetype_checker.extensions import get_ext_and_mismatch


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
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="recursively check files in directories."
    )
    args = parser.parse_args(argv)

    files, problems = scanner.expand_paths(args.paths, args.recursive)
    problem_occurred = bool(problems)
    detect_error_occurred = False

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
                },
            }
            print(reporting.format_json(payload))
        else:
            print(
                reporting.format_human_error(
                    problem["details"]["path"],
                    problem["code"],
                    problem["message"],
                ),
                file=sys.stderr,
            )

    # Perform detection
    try:
        for file in files:
            try:
                file_report = detector.detect(file)
                ext, mismatch = get_ext_and_mismatch(
                    file_report["path"], 
                    file_report["file_type"], 
                    file_report["magic"]["matched"]
                )
                file_report["ext"] = ext
                file_report["mismatch"] = mismatch

                if args.json:
                    print(reporting.format_json(file_report))
                else:
                    print(reporting.format_human_success(file_report))
            except FtcheckError as e:
                detect_error_occurred = True
                if args.json:
                    payload = {
                        "ok": False,
                        "path": file,
                        "error": {
                            "code": e.code,
                            "message": str(e),
                        },
                    }
                    if getattr(e, "details", None):
                        payload["error"]["details"] = e.details
                    print(reporting.format_json(payload))
                else:
                    print(reporting.format_human_error(file, e.code, str(e)), file=sys.stderr)
                continue
    except BrokenPipeError:
        return 0

    return 2 if (problem_occurred or detect_error_occurred) else 0


if __name__ == "__main__":
    raise SystemExit(main())
