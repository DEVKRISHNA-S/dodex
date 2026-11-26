
import os
from pathlib import Path


class CodeSearch:

    IGNORED_DIRS = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        "dist",
        "build",
    }

    def __init__(self, workspace_root, max_file_size=500_000):
        self.workspace_root = Path(workspace_root).resolve()
        self.max_file_size = max_file_size

        if not self.workspace_root.is_dir():
            raise ValueError("Workspace root must be an existing directory")

    def _resolve_path(self, relative_path):
        target = (self.workspace_root / relative_path).resolve()

        if not target.is_relative_to(self.workspace_root):
            raise PermissionError(
                "Access outside workspace is not allowed"
            )

        return target

    def search_text(
        self,
        query,
        directory=".",
        case_sensitive=True,
        file_extensions=None,
        max_results=100,
    ):

        if not query:
            raise ValueError("Search query cannot be empty")

        if max_results < 1:
            raise ValueError("max_results must be greater than zero")

        search_root = self._resolve_path(directory)

        if not search_root.is_dir():
            raise NotADirectoryError(directory)

        if file_extensions:
            file_extensions = {
                ext.lower() if ext.startswith(".") else f".{ext.lower()}"
                for ext in file_extensions
            }

        search_query = query if case_sensitive else query.lower()

        results = []

        for current_dir, dirs, files in os.walk(search_root):

            # Prevent os.walk from entering ignored directories.
            dirs[:] = [
                d for d in dirs
                if d not in self.IGNORED_DIRS
            ]

            for filename in files:

                file_path = Path(current_dir) / filename

                if file_extensions and file_path.suffix.lower() not in file_extensions:
                    continue

                try:
                    if file_path.stat().st_size > self.max_file_size:
                        continue

                    content = file_path.read_text(encoding="utf-8")

                except (UnicodeDecodeError, OSError):
                    continue

                for line_number, line in enumerate(
                    content.splitlines(), start=1
                ):

                    searchable_line = (
                        line if case_sensitive else line.lower()
                    )

                    if search_query in searchable_line:

                        results.append({
                            "file": str(
                                file_path.relative_to(self.workspace_root)
                            ),
                            "line": line_number,
                            "content": line.strip(),
                        })

                        if len(results) >= max_results:
                            return results

        return results
