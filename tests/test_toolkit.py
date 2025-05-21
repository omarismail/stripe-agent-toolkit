import subprocess
from terraform_agent_toolkit.toolkit import TerraformAgentToolkit
from terraform_agent_toolkit.exceptions import ActionNotAllowedError


class DummyProcess:
    def __init__(self, returncode=0, stdout="ok", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def fake_run_factory(calls):
    def fake_run(cmd, cwd=None, env=None, capture_output=True, text=True):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="success", stderr="")
    return fake_run


def test_plan_apply_happy_path(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", fake_run_factory(calls))
    tk = TerraformAgentToolkit(
        working_dir="/tmp",
        allowed_actions=["plan_infrastructure", "apply_infrastructure"],
    )
    res_plan = tk.plan_infrastructure()
    assert res_plan["success"]
    res_apply = tk.apply_infrastructure(confirm=True)
    assert res_apply["success"]
    assert len(calls) == 4  # init+plan+init+apply


def test_confirmation_gate(monkeypatch):
    monkeypatch.setattr(subprocess, "run", fake_run_factory([]))
    tk = TerraformAgentToolkit(
        working_dir="/tmp",
        allowed_actions=["apply_infrastructure"],
        require_confirmation_for_apply=True,
    )
    res = tk.apply_infrastructure()
    assert not res["success"]
    assert res["error"] == "CONFIRMATION_REQUIRED"


def test_disallowed_action(monkeypatch):
    monkeypatch.setattr(subprocess, "run", fake_run_factory([]))
    tk = TerraformAgentToolkit(working_dir="/tmp", allowed_actions=[])
    try:
        tk.plan_infrastructure()
    except ActionNotAllowedError:
        pass
    else:
        assert False, "expected ActionNotAllowedError"
