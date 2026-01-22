import json
import stat
import sys
from pathlib import Path

import pytest

from filetype_checker import cli


def get_result(doc: dict, path: Path) -> dict:
    for r in doc["results"]:
        if r.get("path") == str(path):
            return r
    raise AssertionError(f"Missing result for {path}")


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
    doc = json.loads(captured.out)
    output = get_result(doc, p)
    assert output["ok"] is True
    assert output["path"] == str(p)
    assert output["file_type"] == "PNG Image"
    assert output["size_bytes"] == len(payload)

    assert output["magic"]["matched"] is True
    assert output["magic"]["offset"] == 0
    assert output["magic"]["signature"] == "89504E470D0A1A0A"
    assert output["ext"] == ".png"
    assert output["mismatch"] is False

    assert doc["ok"] is True
    assert doc["summary"]["inputs"] == 1
    assert doc["summary"]["files_scanned"] == 1
    assert doc["summary"]["matched"] == 1
    assert doc["summary"]["unknown"] == 0
    assert doc["summary"]["errors"] == 0
    assert len(doc["results"]) == 1


def test_json_success_unknown(tmp_path: Path, capsys) -> None:
    # Create a temporary file with unknown magic number
    unknown_magic = b"\x00\x11\x22\x33\x44\x55"
    p = tmp_path / "unknown_file.bin"
    p.write_bytes(unknown_magic)

    # Run the CLI with JSON output
    exit_code = cli.main([str(p), "--json"])

    # Capture the output
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.err == ""

    # Validate the JSON output
    doc = json.loads(captured.out)
    output = get_result(doc, p)
    assert output["ok"] is True
    assert output["path"] == str(p)
    assert output["file_type"] == "Unknown File Type"
    assert output["size_bytes"] == len(unknown_magic)

    assert output["magic"]["matched"] is False
    assert output["magic"]["offset"] is None
    assert output["magic"]["signature"] is None
    assert output["ext"] == ".bin"
    assert output["mismatch"] is False

    assert doc["ok"] is True
    assert doc["summary"]["inputs"] == 1
    assert doc["summary"]["files_scanned"] == 1
    assert doc["summary"]["matched"] == 0
    assert doc["summary"]["unknown"] == 1
    assert doc["summary"]["errors"] == 0
    assert len(doc["results"]) == 1


def test_json_error_no_path(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "non_existent_file.bin"

    exit_code = cli.main([str(missing), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.err == ""

    doc = json.loads(captured.out)
    output = get_result(doc, missing)

    assert output["ok"] is False
    assert output["path"] == str(missing)
    assert output["error"]["code"] == "ENOENT"
    assert "message" in output["error"]

    assert doc["ok"] is False
    assert doc["summary"]["files_scanned"] == 0
    assert doc["summary"]["errors"] == 1


def test_json_mismatch_true_when_extension_does_not_match(tmp_path: Path, capsys) -> None:
    jpeg_magic_number = b"\xff\xd8\xff"
    payload = jpeg_magic_number + b"\x00" * 10
    path = tmp_path / "fake.png"
    path.write_bytes(payload)

    exit_code = cli.main([str(path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    doc = json.loads(captured.out)
    output = get_result(doc, path)
    assert output["ok"] is True
    assert output["file_type"] == "JPEG Image"
    assert output["magic"]["matched"] is True
    assert output["ext"] == ".png"
    assert output["mismatch"] is True

    assert doc["ok"] is True
    assert doc["summary"]["matched"] == 1
    assert doc["summary"]["unknown"] == 0
    assert doc["summary"]["errors"] == 0


def test_json_mismatch_false_when_extension_matches(tmp_path: Path, capsys) -> None:
    jpeg_magic_number = b"\xff\xd8\xff"
    payload = jpeg_magic_number + b"\x00" * 10
    path = tmp_path / "photo.jpg"
    path.write_bytes(payload)

    exit_code = cli.main([str(path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    doc = json.loads(captured.out)
    output = get_result(doc, path)
    assert output["ok"] is True
    assert output["file_type"] == "JPEG Image"
    assert output["magic"]["matched"] is True
    assert output["ext"] == ".jpg"
    assert output["mismatch"] is False

    assert doc["ok"] is True
    assert doc["summary"]["matched"] == 1
    assert doc["summary"]["unknown"] == 0
    assert doc["summary"]["errors"] == 0


def test_json_no_extension_never_mismatch(tmp_path: Path, capsys) -> None:
    jpeg_magic_number = b"\xff\xd8\xff"
    payload = jpeg_magic_number + b"\x00" * 10
    path = tmp_path / "Photo"
    path.write_bytes(payload)

    exit_code = cli.main([str(path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    doc = json.loads(captured.out)
    output = get_result(doc, path)
    assert output["ok"] is True
    assert output["file_type"] == "JPEG Image"
    assert output["magic"]["matched"] is True
    assert output["ext"] == ""
    assert output["mismatch"] is False

    assert doc["ok"] is True
    assert doc["summary"]["matched"] == 1
    assert doc["summary"]["unknown"] == 0
    assert doc["summary"]["errors"] == 0


def test_json_unknown_type_never_mismatch(tmp_path: Path, capsys) -> None:
    payload = b"\x00\x11\x22\x33\x44\x55"
    path = tmp_path / "unknown.png"
    path.write_bytes(payload)

    exit_code = cli.main([str(path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.err == ""

    doc = json.loads(captured.out)
    output = get_result(doc, path)
    assert output["ok"] is True
    assert output["file_type"] == "Unknown File Type"
    assert output["magic"]["matched"] is False
    assert output["ext"] == ".png"
    assert output["mismatch"] is False

    assert doc["ok"] is True
    assert doc["summary"]["files_scanned"] == 1
    assert doc["summary"]["matched"] == 0
    assert doc["summary"]["unknown"] == 1
    assert doc["summary"]["errors"] == 0


def test_json_directory_non_recursive_scans_files(tmp_path: Path, capsys) -> None:
    d = tmp_path / "d"
    d.mkdir()
    (d / "a.png").write_bytes(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a" + b"\x00" * 5)
    (d / "b.bin").write_bytes(b"\x00\x01\x02")

    exit_code = cli.main([str(d), "--json"])
    captured = capsys.readouterr()

    doc = json.loads(captured.out)
    assert captured.err == ""
    assert doc["summary"]["inputs"] == 1
    assert doc["summary"]["files_scanned"] == 2
    assert doc["summary"]["matched"] == 1
    assert doc["summary"]["unknown"] == 1
    assert doc["summary"]["errors"] == 0
    assert exit_code == 1  # because unknown exists


def test_json_directory_recursive_finds_nested_files(tmp_path: Path, capsys) -> None:
    d = tmp_path / "d"
    (d / "sub").mkdir(parents=True)
    (d / "sub" / "a.png").write_bytes(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a" + b"\x00")

    exit_code = cli.main([str(d), "--json", "-r"])
    captured = capsys.readouterr()
    doc = json.loads(captured.out)

    assert captured.err == ""
    assert doc["summary"]["files_scanned"] == 1
    assert doc["summary"]["matched"] == 1
    assert doc["summary"]["errors"] == 0
    assert exit_code == 0


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="chmod permission tests unreliable on Windows"
)
def test_json_permission_denied_file(tmp_path: Path, capsys) -> None:
    p = tmp_path / "secret.bin"
    p.write_bytes(b"\x00\x01\x02")
    p.chmod(0)  # remove permissions

    try:
        exit_code = cli.main([str(p), "--json"])
        captured = capsys.readouterr()
        doc = json.loads(captured.out)

        assert exit_code == 2  # because errors > 0
        out = get_result(doc, p)
        assert out["ok"] is False
        assert out["error"]["code"] == "EACCES"
    finally:
        p.chmod(stat.S_IRUSR | stat.S_IWUSR)
