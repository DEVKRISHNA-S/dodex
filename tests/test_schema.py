import pytest

from patchpilot.tools.base import Tool, ToolResult
from patchpilot.tools.registry import ToolRegistry
from patchpilot.agent.schema import build_groq_tools


class DummyTool(Tool):
    name = "dummy_tool"
    description = "A tool for testing schema conversion"

    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "search text"}
                },
                "required": ["query"],
            },
        }

    def run(self, **kwargs):
        return ToolResult(success=True, output="ok")


def test_build_groq_tools_shape():
    registry = ToolRegistry()
    registry.register(DummyTool())

    tools = build_groq_tools(registry)

    assert len(tools) == 1
    tool = tools[0]
    assert tool["type"] == "function"
    assert tool["function"]["name"] == "dummy_tool"
    assert tool["function"]["parameters"]["required"] == ["query"]


def test_build_groq_tools_empty_registry():
    registry = ToolRegistry()
    assert build_groq_tools(registry) == []


def test_build_groq_tools_rejects_malformed_schema():
    class BrokenTool(Tool):
        name = "broken"
        description = "missing parameters key"

        def get_schema(self):
            return {"name": self.name}  # no "parameters"

        def run(self, **kwargs):
            return ToolResult(success=True)

    registry = ToolRegistry()
    registry.register(BrokenTool())

    with pytest.raises(ValueError):
        build_groq_tools(registry)