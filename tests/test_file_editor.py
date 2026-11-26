
import pytest

from patchpilot.tools.file_editor import FileEditor


def test_create_file(tmp_path):
    editor = FileEditor(tmp_path)

    editor.create_file("example.py", "print('hello')")

    assert (tmp_path / "example.py").read_text() == "print('hello')"


def test_prevent_duplicate_creation(tmp_path):
    editor = FileEditor(tmp_path)

    editor.create_file("example.py", "hello")

    with pytest.raises(FileExistsError):
        editor.create_file("example.py", "world")


def test_write_requires_overwrite(tmp_path):
    editor = FileEditor(tmp_path)

    editor.create_file("example.py", "old")

    with pytest.raises(FileExistsError):
        editor.write_file("example.py", "new")


def test_write_with_overwrite(tmp_path):
    editor = FileEditor(tmp_path)

    editor.create_file("example.py", "old")
    editor.write_file("example.py", "new", overwrite=True)

    assert (tmp_path / "example.py").read_text() == "new"


def test_edit_file(tmp_path):
    editor = FileEditor(tmp_path)

    editor.create_file("example.py", "x = 10")

    editor.edit_file("example.py", "10", "20")

    assert (tmp_path / "example.py").read_text() == "x = 20"


def test_edit_ambiguous_text(tmp_path):
    editor = FileEditor(tmp_path)

    editor.create_file("example.py", "x = 10\nx = 10")

    with pytest.raises(ValueError):
        editor.edit_file("example.py", "10", "20")


def test_prevent_directory_traversal(tmp_path):
    editor = FileEditor(tmp_path)

    with pytest.raises(PermissionError):
        editor.create_file("../outside.txt", "hello")
