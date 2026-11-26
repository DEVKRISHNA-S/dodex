
import pytest

from patchpilot.tools.terminal import Terminal


def test_terminal_runs_pytest(tmp_path):
    terminal = Terminal(tmp_path)

    result = terminal.execute(["pytest", "--version"])

    assert result["return_code"] == 0
    assert result["timed_out"] is False
    assert "pytest" in result["stdout"].lower()


def test_terminal_rejects_unauthorized_command(tmp_path):
    terminal = Terminal(tmp_path)

    with pytest.raises(PermissionError):
        terminal.execute(["cmd", "/c", "dir"])


def test_terminal_rejects_shell_string(tmp_path):
    terminal = Terminal(tmp_path)

    with pytest.raises(ValueError):
        terminal.execute("pytest --version")


def test_terminal_prevents_directory_traversal(tmp_path):
    terminal = Terminal(tmp_path)

    with pytest.raises(PermissionError):
        terminal.execute(
            ["pytest", "--version"],
            directory="../"
        )


def test_terminal_rejects_invalid_directory(tmp_path):
    terminal = Terminal(tmp_path)

    with pytest.raises(NotADirectoryError):
        terminal.execute(
            ["pytest", "--version"],
            directory="missing"
        )


def test_terminal_rejects_invalid_timeout(tmp_path):
    terminal = Terminal(tmp_path)

    with pytest.raises(ValueError):
        terminal.execute(
            ["pytest", "--version"],
            timeout=0
        )


def test_terminal_rejects_empty_command(tmp_path):
    terminal = Terminal(tmp_path)

    with pytest.raises(ValueError):
        terminal.execute([])


def test_terminal_rejects_invalid_arguments(tmp_path):
    terminal = Terminal(tmp_path)

    with pytest.raises(ValueError):
        terminal.execute(["pytest", ""])


def test_terminal_timeout(tmp_path):
    test_file = tmp_path / "slow_test.py"

    test_file.write_text(
        "import time\n"
        "def test_slow():\n"
        "    time.sleep(3)\n",
        encoding="utf-8"
    )

    terminal = Terminal(tmp_path)

    result = terminal.execute(
        ["pytest", "-q", "slow_test.py"],
        timeout=1
    )

    assert result["timed_out"] is True
    assert result["return_code"] is None


def test_terminal_output_limit(tmp_path):
    terminal = Terminal(tmp_path)

    result = terminal.execute(
        ["pytest", "--version"],
        max_output_chars=5
    )

    assert len(result["stdout"]) <= 5
