from __future__ import annotations

from typing import List, Dict, Optional

from .core import run_terraform_command
from .exceptions import ActionNotAllowedError


class TerraformAgentToolkit:
    def __init__(
        self,
        working_dir: str,
        allowed_actions: List[str],
        require_confirmation_for_apply: bool = True,
        tf_cloud: Optional[Dict[str, str]] = None,
    ) -> None:
        self.working_dir = working_dir
        self.allowed_actions = set(allowed_actions)
        self.require_confirmation_for_apply = require_confirmation_for_apply
        self.tf_cloud = tf_cloud or {}

    # --------------------- internal helpers ---------------------
    def _ensure_allowed(self, action: str) -> None:
        if action not in self.allowed_actions:
            raise ActionNotAllowedError(f"Action '{action}' is not allowed")

    def _env(self) -> Dict[str, str]:
        env = None
        if self.tf_cloud:
            env = {
                **{k: v for k, v in self.tf_cloud.items()},
            }
        return env

    # ------------------------- tools ---------------------------
    def plan_infrastructure(self) -> Dict[str, object]:
        self._ensure_allowed("plan_infrastructure")
        env = self._env()
        init_result = run_terraform_command(["terraform", "init", "-input=false"], self.working_dir, env)
        if not init_result["success"]:
            return {"success": False, "summary": init_result["summary"]}
        plan_result = run_terraform_command(["terraform", "plan", "-no-color"], self.working_dir, env)
        return {"success": plan_result["success"], "summary": plan_result["summary"]}

    def apply_infrastructure(self, *, confirm: bool = False) -> Dict[str, object]:
        self._ensure_allowed("apply_infrastructure")
        if self.require_confirmation_for_apply and not confirm:
            return {"success": False, "error": "CONFIRMATION_REQUIRED"}
        env = self._env()
        init_result = run_terraform_command(["terraform", "init", "-input=false"], self.working_dir, env)
        if not init_result["success"]:
            return {"success": False, "summary": init_result["summary"]}
        apply_result = run_terraform_command([
            "terraform",
            "apply",
            "-auto-approve",
            "-no-color",
        ], self.working_dir, env)
        return {"success": apply_result["success"], "summary": apply_result["summary"]}

    def validate_config(self) -> Dict[str, object]:
        self._ensure_allowed("validate_config")
        env = self._env()
        init_result = run_terraform_command(["terraform", "init", "-input=false"], self.working_dir, env)
        if not init_result["success"]:
            return {"success": False, "summary": init_result["summary"]}
        val_result = run_terraform_command(["terraform", "validate"], self.working_dir, env)
        return {"success": val_result["success"], "summary": val_result["summary"]}

    def read_state(self) -> Dict[str, object]:
        self._ensure_allowed("read_state")
        env = self._env()
        show_result = run_terraform_command(["terraform", "show", "-no-color"], self.working_dir, env)
        return {"success": show_result["success"], "summary": show_result["summary"]}

    def detect_drift(self) -> Dict[str, object]:
        self._ensure_allowed("detect_drift")
        env = self._env()
        init_result = run_terraform_command(["terraform", "init", "-input=false"], self.working_dir, env)
        if not init_result["success"]:
            return {"success": False, "summary": init_result["summary"]}
        drift_result = run_terraform_command(["terraform", "plan", "-detailed-exitcode", "-no-color"], self.working_dir, env)
        success = drift_result["returncode"] in (0, 2)
        return {"success": success, "summary": drift_result["summary"]}

    def enforce_policy(self) -> Dict[str, object]:
        self._ensure_allowed("enforce_policy")
        env = self._env()
        init_result = run_terraform_command(["terraform", "init", "-input=false"], self.working_dir, env)
        if not init_result["success"]:
            return {"success": False, "summary": init_result["summary"]}
        policy_result = run_terraform_command(["terraform", "validate"], self.working_dir, env)
        return {"success": policy_result["success"], "summary": policy_result["summary"]}

    # --------------------- openai interface --------------------
    def get_tools(self) -> List[Dict[str, object]]:
        """Return OpenAI function specs for all tools."""
        tools = [
            {
                "name": "plan_infrastructure",
                "description": "Generate a Terraform plan",
                "parameters": {},
            },
            {
                "name": "apply_infrastructure",
                "description": "Apply Terraform changes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "confirm": {"type": "boolean"},
                    },
                    "required": [],
                },
            },
            {
                "name": "validate_config",
                "description": "Validate Terraform configuration",
                "parameters": {},
            },
            {
                "name": "read_state",
                "description": "Read Terraform state",
                "parameters": {},
            },
            {
                "name": "detect_drift",
                "description": "Detect infrastructure drift",
                "parameters": {},
            },
            {
                "name": "enforce_policy",
                "description": "Enforce policy on Terraform configuration",
                "parameters": {},
            },
        ]
        return tools
