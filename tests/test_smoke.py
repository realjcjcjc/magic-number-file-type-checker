from filetype_checker.cli import main


def test_cli_imports():
    assert callable(main)