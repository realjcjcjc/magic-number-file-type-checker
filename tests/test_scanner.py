
from filetype_checker import scanner


def write_bytes(path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def test_expand_path_file_returns_that_file(tmp_path):
    file_path = tmp_path / "testfile.bin"
    write_bytes(file_path, b"\x00\x11\x22\x33\x44\x55")

    files, problems = scanner.expand_paths([str(file_path)], recursive=False)

    assert problems == []
    assert files == [str(file_path)]

def test_expand_path_dir_non_recursive_only_top_level_files(tmp_path):
    dir_path = tmp_path / "testdir"
    file1 = dir_path / "file1.bin"
    file2 = dir_path / "file2.bin"
    nested = dir_path / "nested"
    inner = nested / "innerfile.bin"

    write_bytes(file1, b"top")
    write_bytes(file2, b"toptwo")
    write_bytes(inner, b"inner")

    files, problems = scanner.expand_paths([str(dir_path)], recursive=False)

    assert problems == []
    assert files == [str(file1), str(file2)]

def test_expand_path_dir_recursive_all_files(tmp_path):
    dir_path = tmp_path / "testdir"
    file1 = dir_path / "file1.bin"
    file2 = dir_path / "file2.bin"
    nested = dir_path / "nested"
    inner = nested / "innerfile.bin"

    write_bytes(file1, b"top")
    write_bytes(file2, b"toptwo")
    write_bytes(inner, b"inner")

    files, problems = scanner.expand_paths([str(dir_path)], recursive=True)

    assert problems == []
    assert set(files) == {str(file1), str(file2), str(inner)}

def test_expand_paths_dedupes_and_sorts(tmp_path):
    dir_path = tmp_path / "testdir"
    file1 = dir_path / "file1.bin"
    file2 = dir_path / "file2.bin"

    write_bytes(file1, b"file1")
    write_bytes(file2, b"file2")

    files, problems = scanner.expand_paths([str(dir_path), str(file1)], recursive=False)

    assert problems == []
    assert files == [str(file1), str(file2)]

def test_expand_path_missing_returns_problem(tmp_path):
    missing_path = tmp_path / "non_existent.bin"

    files, problems = scanner.expand_paths([str(missing_path)], recursive=False)

    assert files == []
    assert len(problems) == 1
    assert problems[0]["code"] == "ENOENT"
    assert problems[0]["details"]["path"] == str(missing_path)