import pytest

from filetype_checker import detector
from filetype_checker.error import PathNotFoundError


def write_bytes(path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


@pytest.mark.parametrize(
    "magic_number, expected_label, expected_magic_num",
    [
        (b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a", "PNG Image", "89504E470D0A1A0A"),
        (b"\xff\xd8\xff", "JPEG Image", "FFD8FF"),
        (b"GIF87a", "GIF Image", "474946383761"),
        (b"GIF89a", "GIF Image", "474946383961"),
        (b"%PDF-", "PDF Document", "255044462D"),
        (b"\x50\x4b\x03\x04", "ZIP Archive", "504B0304"),
        (b"\x50\x4b\x05\x06", "ZIP Archive", "504B0506"),
        (b"\x50\x4b\x07\x08", "ZIP Archive", "504B0708"),
    ],
)

def test_detect_known_file_types(tmp_path, magic_number, expected_label, expected_magic_num):
    file_path = tmp_path / f"testfile_{expected_label.replace(' ', '_')}"
    write_bytes(file_path, magic_number + b"\x00" * 10)  # Add some padding bytes

    result = detector.detect(str(file_path))
    assert result["ok"] is True
    assert result["path"] == str(file_path)
    assert result["file_type"] == expected_label
    assert result["size_bytes"] == len(magic_number) + 10
    assert result["magic"]["matched"] is True
    assert result["magic"]["offset"] == 0
    assert result["magic"]["signature"] == expected_magic_num

def test_detect_unknown_file_type(tmp_path):
    file_path = tmp_path / "unknown_file"
    write_bytes(file_path, b"\x00\x11\x22\x33\x44\x55")

    result = detector.detect(str(file_path))
    assert result["ok"] is True
    assert result["path"] == str(file_path)
    assert result["file_type"] == "Unknown File Type"
    assert result["size_bytes"] == 6
    assert result["magic"]["matched"] is False
    assert result["magic"]["offset"] is None
    assert result["magic"]["signature"] is None

def test_path_with_spaces(tmp_path):
    file_path = tmp_path / "file with spaces.pdf"
    write_bytes(file_path, b"%PDF-1.4" + b"\x00" * 5)

    result = detector.detect(str(file_path))
    assert result["ok"] is True
    assert result["path"] == str(file_path)
    assert result["file_type"] == "PDF Document"
    assert result["size_bytes"] == len(b"%PDF-1.4") + 5
    assert result["magic"]["matched"] is True
    assert result["magic"]["offset"] == 0
    assert result["magic"]["signature"] == "255044462D"


def test_missing_file(tmp_path):
    file_path = tmp_path / "non_existent_file"
    
    with pytest.raises(PathNotFoundError):
        detector.detect(str(file_path))
