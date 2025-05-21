from __future__ import annotations

import json
from typing import Any, List

from .toolkit import TerraformAgentToolkit

try:
    from agents import FunctionTool  # type: ignore
    from agents.run_context import RunContextWrapper  # type: ignore
except Exception:  # pragma: no cover - handled at runtime
    FunctionTool = None  # type: ignore
    RunContextWrapper = None  # type: ignore


def get_openai_tools(toolkit: TerraformAgentToolkit) -> List["FunctionTool"]:
    """Return OpenAI FunctionTool instances for toolkit methods."""
    if FunctionTool is None:
        raise ImportError("OpenAI Agent SDK is required for this feature")

    tools = []
    for spec in toolkit.get_tools():
        name = spec["name"]
        description = spec["description"]
        params_schema = spec.get("parameters", {"type": "object", "properties": {}})
        method = getattr(toolkit, name)

        async def on_invoke(
            ctx: RunContextWrapper[Any],
            input_str: str,
            _method=method,
        ) -> str:
            kwargs = json.loads(input_str or "{}")
            result = _method(**kwargs)
            return json.dumps(result)

        tools.append(
            FunctionTool(
                name=name,
                description=description,
                params_json_schema=params_schema,
                on_invoke_tool=on_invoke,
                strict_json_schema=False,
            )
        )
    return tools
