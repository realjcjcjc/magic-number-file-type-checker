import pytest

from filetype_checker import detector


def write_bytes(path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


@pytest.mark.parametrize(
    "magic_number, expected",
    [
        (b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a", "PNG Image"),
        (b"\xff\xd8\xff", "JPEG Image"),
        (b"GIF87a", "GIF Image"),
        (b"GIF89a", "GIF Image"),
        (b"%PDF-", "PDF Document"),
        (b"\x50\x4b\x03\x04", "ZIP Archive"),
        (b"\x50\x4b\x05\x06", "ZIP Archive"),
        (b"\x50\x4b\x07\x08", "ZIP Archive"),
    ],
)

def test_detect_known_file_types(tmp_path, magic_number, expected):
    file_path = tmp_path / f"testfile_{expected}"
    write_bytes(file_path, magic_number)
    result = detector.detect(str(file_path))
    assert result == expected


def test_detect_unknown_file_type(tmp_path):
    file_path = tmp_path / "unknown_file"
    write_bytes(file_path, b"\x00\x11\x22\x33\x44\x55")
    result = detector.detect(str(file_path))
    assert result == "Unknown File Type"


def test_path_with_spaces(tmp_path):
    file_path = tmp_path / "file with spaces.pdf"
    write_bytes(file_path, b"%PDF-1.4")
    result = detector.detect(str(file_path))
    assert result == "PDF Document"


def test_missing_file(tmp_path):
    file_path = tmp_path / "non_existent_file"
    result = detector.detect(str(file_path))
    assert result == "ftcheck-ERROR: File not found"
