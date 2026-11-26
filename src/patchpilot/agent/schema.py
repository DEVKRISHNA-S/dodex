from patchpilot.tools.registry import ToolRegistry


def build_groq_tools(registry: ToolRegistry) -> list[dict]:
    """
    Convert every registered tool's schema into Groq's (OpenAI-compatible)
    function-calling format:

    {
        "type": "function",
        "function": {
            "name": "...",
            "description": "...",
            "parameters": {
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        }
    }
    """
    groq_tools = []

    for schema in registry.get_schemas():
        if "name" not in schema or "parameters" not in schema:
            raise ValueError(
                f"Tool schema missing required keys: {schema}"
            )

        groq_tools.append({
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema.get("description", ""),
                "parameters": schema["parameters"],
            },
        })

    return groq_tools