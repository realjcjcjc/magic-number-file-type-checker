import json
from pathlib import Path

from filetype_checker import cli


def test_json_success_png(tmp_path: Path, capsys) -> None:
    # Create a temporary PNG file
    png_magic = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
    payload = png_magic + b"\x00" * 10  # Add some padding bytes
    p = tmp_path / "test_image.png"
    p.write_bytes(payload)

    # Run the CLI with JSON output
    exit_code = cli.main([str(p), "--json"])

    # Capture the output
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    # Validate the JSON output
    output = json.loads(captured.out)
    assert output["ok"] is True
    assert output["path"] == str(p)
    assert output["file_type"] == "PNG Image"
    assert output["size_bytes"] == len(payload)

    assert output["magic"]["matched"] is True
    assert output["magic"]["offset"] == 0
    assert output["magic"]["signature"] == "89504E470D0A1A0A"

def test_json_success_unknown(tmp_path: Path, capsys) -> None:
    # Create a temporary file with unknown magic number
    unknown_magic = b"\x00\x11\x22\x33\x44\x55"
    p = tmp_path / "unknown_file.bin"
    p.write_bytes(unknown_magic)

    # Run the CLI with JSON output
    exit_code = cli.main([str(p), "--json"])

    # Capture the output
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    # Validate the JSON output
    output = json.loads(captured.out)
    assert output["ok"] is True
    assert output["path"] == str(p)
    assert output["file_type"] == "Unknown File Type"
    assert output["size_bytes"] == len(unknown_magic)

    assert output["magic"]["matched"] is False
    assert output["magic"]["offset"] is None
    assert output["magic"]["signature"] is None

def test_json_error_no_path(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "non_existent_file.bin"

    exit_code = cli.main([str(missing), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 3
    assert captured.err == ""

    output = json.loads(captured.out)

    assert output["ok"] is False
    assert output["path"] == str(missing)
    assert output["error"]["code"] == "ENOENT"
    assert "message" in output["error"]