
import subprocess
from pathlib import Path


class Terminal:

    # Only explicitly approved command patterns are accepted.
    ALLOWED_PREFIXES = [
        ("pytest",),
        ("uv", "run", "pytest"),
        ("uv", "run", "python", "-m", "pytest"),
        ("python", "-m", "pytest"),
        ("git", "status"),
        ("git", "diff"),
        ("git", "log"),
        ("git", "show"),
        ("git", "branch", "--show-current"),
    ]

    def __init__(self, workspace_root, default_timeout=30):
        self.workspace_root = Path(workspace_root).resolve()
        self.default_timeout = default_timeout

        if not self.workspace_root.is_dir():
            raise ValueError("Workspace root must be an existing directory")

        if default_timeout <= 0:
            raise ValueError("Default timeout must be greater than zero")

    def _resolve_directory(self, directory):
        target = (self.workspace_root / directory).resolve()

        if not target.is_relative_to(self.workspace_root):
            raise PermissionError(
                "Access outside workspace is not allowed"
            )

        if not target.is_dir():
            raise NotADirectoryError(directory)

        return target

    def _is_allowed(self, command):
        normalized = tuple(
            Path(part).name.lower() if index == 0 else part.lower()
            for index, part in enumerate(command)
        )

        return any(
            normalized[:len(prefix)] == prefix
            for prefix in self.ALLOWED_PREFIXES
        )

    def execute(
        self,
        command,
        directory=".",
        timeout=None,
        max_output_chars=10_000,
    ):

        if not isinstance(command, (list, tuple)) or not command:
            raise ValueError("Command must be a non-empty list of strings")

        if not all(
            isinstance(part, str) and part.strip() and "\x00" not in part
            for part in command
        ):
            raise ValueError("Every command argument must be a valid string")

        command = list(command)

        if not self._is_allowed(command):
            raise PermissionError("This command is not allowed")

        working_directory = self._resolve_directory(directory)

        timeout = timeout if timeout is not None else self.default_timeout

        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero")

        if max_output_chars < 1:
            raise ValueError("max_output_chars must be greater than zero")

        try:
            result = subprocess.run(
                command,
                cwd=working_directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                shell=False,
                check=False,
            )

            return {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout[:max_output_chars],
                "stderr": result.stderr[:max_output_chars],
                "timed_out": False,
            }

        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or ""
            stderr = error.stderr or ""

            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")

            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")

            return {
                "command": command,
                "return_code": None,
                "stdout": stdout[:max_output_chars],
                "stderr": stderr[:max_output_chars],
                "timed_out": True,
            }
