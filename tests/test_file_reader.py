
import pytest

from patchpilot.tools.file_reader import FileReader


def test_read_file(tmp_path):
    file = tmp_path / "example.py"
    file.write_text("print('Hello PatchPilot')", encoding="utf-8")

    reader = FileReader(tmp_path)

    result = reader.read_file("example.py")

    assert result == "print('Hello PatchPilot')"


def test_list_files(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "utils.py").write_text("def add(): pass")

    reader = FileReader(tmp_path)

    result = reader.list_files()

    assert "main.py" in result
    assert "utils.py" in result


def test_prevent_directory_traversal(tmp_path):
    reader = FileReader(tmp_path)

    with pytest.raises(PermissionError):
        reader.read_file("../secret.txt")


def test_file_not_found(tmp_path):
    reader = FileReader(tmp_path)

    with pytest.raises(FileNotFoundError):
        reader.read_file("missing.py")


def test_file_size_limit(tmp_path):
    file = tmp_path / "large.txt"
    file.write_text("A" * 100, encoding="utf-8")

    reader = FileReader(tmp_path)

    with pytest.raises(ValueError):
        reader.read_file("large.txt", max_size=50)
