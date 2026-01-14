import json
import subprocess
import sys
from pathlib import Path


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def run_ftcheck(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "filetype_checker.cli", *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)

def test_cli_json_known_file_exit_0(tmp_path: Path) -> None:
    png_magic = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
    payload = png_magic + b"\x00" * 10
    path = tmp_path / "a.png"
    write_bytes(path, payload)

    proc = run_ftcheck(str(path), "--json")

    assert proc.returncode == 0
    assert proc.stderr == ""

    doc = json.loads(proc.stdout)
    assert doc["ok"] is True
    assert doc["summary"]["inputs"] == 1
    assert doc["summary"]["files_scanned"] == 1
    assert doc["summary"]["matched"] == 1
    assert doc["summary"]["unknown"] == 0
    assert doc["summary"]["errors"] == 0
    assert len(doc["results"]) == 1

    result = doc["results"][0]
    assert result["ok"] is True
    assert result["file_type"] == "PNG Image"
    assert result["magic"]["matched"] is True

def test_cli_json_unknown_file_exit_1(tmp_path: Path) -> None:
    p = tmp_path / "unknown.bin"
    write_bytes(p, b"\x00\x11\x22\x33\x44\x55")

    proc = run_ftcheck(str(p), "--json")

    assert proc.returncode == 1
    assert proc.stderr == ""

    doc = json.loads(proc.stdout)
    assert doc["ok"] is True
    assert doc["summary"]["files_scanned"] == 1
    assert doc["summary"]["matched"] == 0
    assert doc["summary"]["unknown"] == 1
    assert doc["summary"]["errors"] == 0

    result = doc["results"][0]
    assert result["ok"] is True
    assert result["file_type"] == "Unknown File Type"
    assert result["magic"]["matched"] is False


def test_cli_json_missing_path_exit_2(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.bin"

    proc = run_ftcheck(str(missing), "--json")

    assert proc.returncode == 2
    assert proc.stderr == ""

    doc = json.loads(proc.stdout)
    assert doc["ok"] is False
    assert doc["summary"]["inputs"] == 1
    assert doc["summary"]["files_scanned"] == 0
    assert doc["summary"]["errors"] == 1
    assert len(doc["results"]) == 1

    err = doc["results"][0]
    assert err["ok"] is False
    assert err["path"] == str(missing)
    assert err["error"]["code"] == "ENOENT"


def test_cli_json_recursive_dir_mixed_known_unknown_exit_1(tmp_path: Path) -> None:
    d = tmp_path / "dir"
    known = d / "photo.jpg"
    unknown = d / "nested" / "mystery.bin"

    write_bytes(known, b"\xff\xd8\xff" + b"\x00" * 10)   # JPEG
    write_bytes(unknown, b"\x00\x11\x22\x33\x44\x55")    # Unknown

    proc = run_ftcheck("-r", str(d), "--json")

    assert proc.returncode == 1
    assert proc.stderr == ""

    doc = json.loads(proc.stdout)
    assert doc["ok"] is True
    assert doc["summary"]["inputs"] == 1
    assert doc["summary"]["files_scanned"] == 2
    assert doc["summary"]["matched"] == 1
    assert doc["summary"]["unknown"] == 1
    assert doc["summary"]["errors"] == 0
    assert len(doc["results"]) == 2