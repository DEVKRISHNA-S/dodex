from patchpilot.tools.base import Tool, ToolResult


class ToolRegistry:
    """
    Central place where tools register themselves and the agent
    discovers/invokes them by name.
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if not tool.name:
            raise ValueError("Tool must define a non-empty 'name' attribute")

        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        del self._tools[name]

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        return self._tools[name]

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def get_schemas(self) -> list[dict]:
        """Schemas for every registered tool, ready to hand to an LLM."""
        return [tool.get_schema() for tool in self._tools.values()]

    def invoke(self, name: str, **kwargs) -> ToolResult:
        """Look up a tool by name and run it safely."""
        try:
            tool = self.get(name)
        except KeyError as exc:
            return ToolResult(success=False, error=str(exc))

        return tool.safe_run(**kwargs)