# Terraform Agent Toolkit

Minimal SDK inspired by Stripe's agent-toolkit for managing Terraform operations.

## Installation

```bash
pip install terraform_agent_toolkit
```

## Quick Start

```python
from terraform_agent_toolkit import TerraformAgentToolkit

allowed = [
    "plan_infrastructure",
    "apply_infrastructure",
]

tk = TerraformAgentToolkit(working_dir="./infra", allowed_actions=allowed)
plan = tk.plan_infrastructure()
print(plan["summary"])

apply = tk.apply_infrastructure(confirm=True)
print(apply["summary"])
```

## Using with OpenAI Agent SDK

```python
from terraform_agent_toolkit import TerraformAgentToolkit, get_openai_tools
from agents import Agent

tk = TerraformAgentToolkit(working_dir="./infra", allowed_actions=allowed)
agent = Agent(name="tf", instructions="manage infra", tools=get_openai_tools(tk))
```

## Safety

- Actions are whitelisted via `allowed_actions`.
- Applying infrastructure requires explicit confirmation unless disabled.
