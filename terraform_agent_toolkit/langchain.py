from typing import List

from langchain.tools import Tool

from .toolkit import TerraformAgentToolkit


TOOL_METHODS = [
    "plan_infrastructure",
    "apply_infrastructure",
    "validate_config",
    "read_state",
    "detect_drift",
    "enforce_policy",
]


def get_langchain_tools(toolkit: TerraformAgentToolkit) -> List[Tool]:
    """Return LangChain Tool objects wrapping the toolkit methods."""
    tools = []
    for name in TOOL_METHODS:
        method = getattr(toolkit, name)
        tools.append(
            Tool(
                name=name,
                func=method,
                description=name.replace("_", " "),
            )
        )
    return tools
