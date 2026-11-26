
from pathlib import Path


class FileEditor:

    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root).resolve()

        if not self.workspace_root.is_dir():
            raise ValueError("Workspace root must be an existing directory")

    def _resolve_path(self, relative_path):
        target = (self.workspace_root / relative_path).resolve()

        if not target.is_relative_to(self.workspace_root):
            raise PermissionError("Access outside workspace is not allowed")

        return target

    def create_file(self, file_path, content=""):
        target = self._resolve_path(file_path)

        if target.exists():
            raise FileExistsError(file_path)

        if not target.parent.is_dir():
            raise FileNotFoundError("Parent directory does not exist")

        with target.open("x", encoding="utf-8") as file:
            file.write(content)

        return f"Created {file_path}"

    def write_file(self, file_path, content, overwrite=False):
        target = self._resolve_path(file_path)

        if target.exists() and not overwrite:
            raise FileExistsError(
                "File already exists. Set overwrite=True explicitly."
            )

        if not target.parent.is_dir():
            raise FileNotFoundError("Parent directory does not exist")

        with target.open("w", encoding="utf-8") as file:
            file.write(content)

        return f"Written {file_path}"

    def edit_file(self, file_path, old_text, new_text):
        target = self._resolve_path(file_path)

        if not target.is_file():
            raise FileNotFoundError(file_path)

        content = target.read_text(encoding="utf-8")

        occurrences = content.count(old_text)

        if occurrences == 0:
            raise ValueError("Target text was not found")

        if occurrences > 1:
            raise ValueError(
                "Target text is ambiguous. It occurs multiple times."
            )

        updated_content = content.replace(old_text, new_text, 1)

        target.write_text(updated_content, encoding="utf-8")

        return f"Updated {file_path}"
