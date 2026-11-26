from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """Uniform result wrapper returned by every tool call."""
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }


class Tool(ABC):
    """Base class every tool (FileReader, Terminal, GitTools, ...) implements."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def get_schema(self) -> dict:
        """
        Return a JSON-schema-like dict describing this tool's parameters,
        in the same shape an LLM function-calling API expects:

        {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        }
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, **kwargs) -> ToolResult:
        """Execute the tool with validated kwargs and return a ToolResult."""
        raise NotImplementedError

    def safe_run(self, **kwargs) -> ToolResult:
        """
        Wraps run() so that any unexpected exception becomes a ToolResult
        instead of crashing the agent loop. Expected/validation errors
        (ValueError, PermissionError, RuntimeError) are caught here too,
        so individual tools don't each need their own try/except.
        """
        try:
            return self.run(**kwargs)
        except (ValueError, PermissionError, RuntimeError) as exc:
            return ToolResult(success=False, error=str(exc))
        except Exception as exc:  # last-resort guard
            return ToolResult(
                success=False,
                error=f"Unexpected error in tool '{self.name}': {exc}",
            )