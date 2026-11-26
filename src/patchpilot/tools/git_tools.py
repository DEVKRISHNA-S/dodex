
import subprocess
from pathlib import Path


class GitTools:

    def __init__(self, workspace_root, default_timeout=15):
        self.workspace_root = Path(workspace_root).resolve()
        self.default_timeout = default_timeout

        if not self.workspace_root.is_dir():
            raise ValueError("Workspace root must be an existing directory")

        if default_timeout <= 0:
            raise ValueError("Default timeout must be greater than zero")

        self._run_git(["rev-parse", "--is-inside-work-tree"])

    def _run_git(self, arguments):
        command = ["git", *arguments]

        try:
            result = subprocess.run(
                command,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.default_timeout,
                shell=False,
                check=False,
            )

        except subprocess.TimeoutExpired:
            raise TimeoutError("Git command exceeded the time limit")

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or "Git command failed"
            )

        return result.stdout.strip()

    def status(self):
        return self._run_git([
            "status",
            "--short",
            "--branch"
        ])

    def diff(self, staged=False):
        arguments = ["diff"]

        if staged:
            arguments.append("--cached")

        return self._run_git(arguments)

    def log(self, limit=5):
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("Limit must be a positive integer")

        return self._run_git([
            "log",
            f"-{limit}",
            "--oneline",
        ])

    def current_branch(self):
        return self._run_git([
            "branch",
            "--show-current"
        ])

    def show_commit(self, commit_hash):
        if not isinstance(commit_hash, str) or not commit_hash.strip():
            raise ValueError("Commit hash cannot be empty")

        if commit_hash.startswith("-"):
            raise ValueError("Invalid commit identifier")

        return self._run_git([
            "show",
            "--no-ext-diff",
            "--format=fuller",
            "--stat",
            commit_hash,
        ])
