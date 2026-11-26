
import subprocess

import pytest

from patchpilot.tools.git_tools import GitTools


def initialize_repository(path):
    subprocess.run(
        ["git", "init"],
        cwd=path,
        check=True,
        capture_output=True,
    )

    subprocess.run(
        ["git", "config", "user.name", "PatchPilot Test"],
        cwd=path,
        check=True,
    )

    subprocess.run(
        ["git", "config", "user.email", "test@patchpilot.local"],
        cwd=path,
        check=True,
    )


def create_commit(path, filename, content):
    file = path / filename
    file.write_text(content, encoding="utf-8")

    subprocess.run(
        ["git", "add", filename],
        cwd=path,
        check=True,
    )

    subprocess.run(
        ["git", "commit", "-m", f"Add {filename}"],
        cwd=path,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def git_repo(tmp_path):
    initialize_repository(tmp_path)

    create_commit(
        tmp_path,
        "main.py",
        "print('hello')"
    )

    return tmp_path


def test_git_status(git_repo):
    tools = GitTools(git_repo)

    status = tools.status()

    assert "main.py" in status


def test_git_diff(git_repo):
    tools = GitTools(git_repo)

    file = git_repo / "main.py"
    file.write_text("print('updated')", encoding="utf-8")

    result = tools.diff()

    assert "updated" in result
    assert "hello" in result


def test_git_staged_diff(git_repo):
    tools = GitTools(git_repo)

    file = git_repo / "main.py"
    file.write_text("print('staged')", encoding="utf-8")

    subprocess.run(
        ["git", "add", "main.py"],
        cwd=git_repo,
        check=True,
    )

    result = tools.diff(staged=True)

    assert "staged" in result


def test_git_log(git_repo):
    tools = GitTools(git_repo)

    result = tools.log()

    assert "Add main.py" in result


def test_current_branch(git_repo):
    tools = GitTools(git_repo)

    result = tools.current_branch()

    assert result != ""


def test_show_commit(git_repo):
    tools = GitTools(git_repo)

    commit_hash = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=git_repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    result = tools.show_commit(commit_hash)

    assert "main.py" in result


def test_log_rejects_invalid_limit(git_repo):
    tools = GitTools(git_repo)

    with pytest.raises(ValueError):
        tools.log(limit=0)


def test_show_commit_rejects_empty_hash(git_repo):
    tools = GitTools(git_repo)

    with pytest.raises(ValueError):
        tools.show_commit("")


def test_show_commit_rejects_option_injection(git_repo):
    tools = GitTools(git_repo)

    with pytest.raises(ValueError):
        tools.show_commit("--all")


def test_rejects_non_git_directory(tmp_path):
    with pytest.raises(RuntimeError):
        GitTools(tmp_path)
