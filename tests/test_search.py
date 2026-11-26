
import pytest

from patchpilot.tools.search import CodeSearch


def test_search_text(tmp_path):
    file = tmp_path / "main.py"
    file.write_text(
        "def hello():\n    print('hello world')",
        encoding="utf-8"
    )

    search = CodeSearch(tmp_path)

    results = search.search_text("hello")

    assert len(results) == 2
    assert results[0]["line"] == 1
    assert results[1]["line"] == 2


def test_case_insensitive_search(tmp_path):
    file = tmp_path / "main.py"
    file.write_text("HELLO WORLD", encoding="utf-8")

    search = CodeSearch(tmp_path)

    results = search.search_text(
        "hello",
        case_sensitive=False
    )

    assert len(results) == 1


def test_case_sensitive_search(tmp_path):
    file = tmp_path / "main.py"
    file.write_text("HELLO WORLD", encoding="utf-8")

    search = CodeSearch(tmp_path)

    results = search.search_text(
        "hello",
        case_sensitive=True
    )

    assert len(results) == 0


def test_extension_filter(tmp_path):
    (tmp_path / "main.py").write_text("hello")
    (tmp_path / "notes.txt").write_text("hello")

    search = CodeSearch(tmp_path)

    results = search.search_text(
        "hello",
        file_extensions=[".py"]
    )

    assert len(results) == 1
    assert results[0]["file"].endswith(".py")


def test_max_results(tmp_path):
    for i in range(5):
        (tmp_path / f"file{i}.py").write_text("hello")

    search = CodeSearch(tmp_path)

    results = search.search_text(
        "hello",
        max_results=2
    )

    assert len(results) == 2


def test_ignore_directories(tmp_path):
    ignored = tmp_path / ".venv"
    ignored.mkdir()

    (ignored / "test.py").write_text("hello")

    search = CodeSearch(tmp_path)

    results = search.search_text("hello")

    assert len(results) == 0


def test_directory_traversal(tmp_path):
    search = CodeSearch(tmp_path)

    with pytest.raises(PermissionError):
        search.search_text("hello", directory="../")


def test_empty_query(tmp_path):
    search = CodeSearch(tmp_path)

    with pytest.raises(ValueError):
        search.search_text("")


def test_invalid_max_results(tmp_path):
    search = CodeSearch(tmp_path)

    with pytest.raises(ValueError):
        search.search_text("hello", max_results=0)
