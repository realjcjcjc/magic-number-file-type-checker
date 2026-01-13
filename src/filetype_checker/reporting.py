import json


def format_human_success(report: dict) -> str:
    """Convert a successful file_report dict into a human-readable line."""
    path = report["path"]
    file_type = report["file_type"]
    size = report["size_bytes"]
    magic = report["magic"]
    matched = "yes" if magic["matched"] else "no"
    offset = magic["offset"] if magic["offset"] is not None else "N/A"
    signature = magic["signature"] if magic["signature"] is not None else "N/A"

    base = (
        f"{path}: {file_type}, matched={matched}, size={size}, "
        f"offset={offset}, signature={signature}"
    )

    if report.get("mismatch"):
        base += f" (extension mismatch: {report.get('ext')})"

    return base


def format_human_error(path: str | None, code: str | None, message: str) -> str:
    """Convert a single error/problem into a human-readable line."""
    prefix = "ftcheck: error:"
    parts = [prefix]

    if code:
        parts.append(f"[{code}]")

    if path:
        parts.append(f"{path}")

    parts.append(message)

    return " ".join(parts)


def format_json(obj: dict) -> str:
    """Convert a dict into JSON text."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
