
from pathlib import Path


class FileReader:

    IGNORED_DIRS = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
    }

    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root).resolve()

        if not self.workspace_root.is_dir():
            raise ValueError("Workspace root must be an existing directory")

    def _resolve_path(self, relative_path):
        target = (self.workspace_root / relative_path).resolve()

        if not target.is_relative_to(self.workspace_root):
            raise PermissionError("Access outside workspace is not allowed")

        return target

    def list_files(self, directory="."):
        target = self._resolve_path(directory)

        if not target.is_dir():
            raise NotADirectoryError(directory)

        files = []

        for path in target.rglob("*"):
            if any(part in self.IGNORED_DIRS for part in path.parts):
                continue

            if path.is_file():
                files.append(
                    str(path.relative_to(self.workspace_root))
                )

        return files

    def read_file(self, file_path, max_size=100_000):
        target = self._resolve_path(file_path)

        if not target.is_file():
            raise FileNotFoundError(file_path)

        if target.stat().st_size > max_size:
            raise ValueError("File exceeds maximum allowed size")

        try:
            return target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ValueError("File is not valid UTF-8 text")
