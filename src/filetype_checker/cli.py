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
    parser.add_argument("paths", nargs="+", help="Files and/or directories to scan")
    parser.add_argument("--json", action="store_true", help="Emit a single JSON document to stdout")
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Recurse into directories."
    )
    args = parser.parse_args(argv)

    files, problems = scanner.expand_paths(args.paths, args.recursive)
    items = []

    # Print Errors encountered during path expansion
    for problem in problems:
        path = (problem.details or {}).get("path") or "<unknown>"

        payload = {
            "ok": False,
            "path": path,
            "error": {
                "code": problem.code,
                "message": str(problem),
            },
        }
        if problem.details is not None:
            payload["error"]["details"] = problem.details

        items.append(payload)

        if not args.json:
            print(
                reporting.format_human_error(
                    path,
                    payload["error"]["code"],
                    payload["error"]["message"],
                ),
                file=sys.stderr,
            )

    # Perform detection
    try:
        for file in files:
            try:
                file_report = detector.detect(file)
                ext, mismatch = get_ext_and_mismatch(
                    file_report["path"], file_report["file_type"], file_report["magic"]["matched"]
                )
                file_report["ext"] = ext
                file_report["mismatch"] = mismatch
                items.append(file_report)

                if not args.json:
                    print(reporting.format_human_success(file_report))
            except FtcheckError as e:
                err_path = (e.details or {}).get("path") or file
                payload = {
                    "ok": False,
                    "path": err_path,
                    "error": {
                        "code": e.code,
                        "message": str(e),
                    },
                }
                if e.details is not None:
                    payload["error"]["details"] = e.details

                items.append(payload)

                if not args.json:
                    print(reporting.format_human_error(err_path, e.code, str(e)), file=sys.stderr)
                continue
            except OSError as e:
                payload = {
                    "ok": False,
                    "path": file,
                    "error": {
                        "code": "EIO",
                        "message": f"Error reading file: {file}",
                        "details": {"path": file, "os_error": str(e)},
                    },
                }
                items.append(payload)
                if not args.json:
                    print(
                        reporting.format_human_error(file, "EIO", payload["error"]["message"]),
                        file=sys.stderr,
                    )
    except BrokenPipeError:
        return 0

    files_scanned = sum(1 for file in items if file.get("ok") is True)
    matched = sum(
        1
        for file in items
        if file.get("ok") is True and file.get("magic", {}).get("matched") is True
    )
    errors = sum(1 for er in items if not er.get("ok", False))
    unknown = sum(
        1 for er in items if er.get("ok") is True and er.get("magic", {}).get("matched") is False
    )

    if args.json:
        summary = {
            "inputs": len(args.paths),
            "files_scanned": files_scanned,
            "matched": matched,
            "unknown": unknown,
            "errors": errors,
        }
        final_doc = {
            "ok": errors == 0,
            "summary": summary,
            "results": items,
        }

        print(reporting.format_json(final_doc))
    else:
        print(
            f"Scanned: {files_scanned} files "
            f"(matched: {matched}, unknown: {unknown}, errors: {errors})",
            file=sys.stderr,
        )

    if errors > 0:
        exit_code = 2
    elif unknown > 0:
        exit_code = 1
    else:
        exit_code = 0

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
