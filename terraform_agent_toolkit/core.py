import subprocess
from typing import List, Optional, Dict

MAX_OUTPUT_CHARS = 4000


def run_terraform_command(cmd: List[str], cwd: str, env: Optional[Dict[str, str]] = None) -> dict:
    """Run a Terraform CLI command and capture its output."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    combined = (stdout + "\n" + stderr).strip()
    summary = combined[:MAX_OUTPUT_CHARS]
    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": result.returncode,
        "success": result.returncode == 0,
        "summary": summary,
    }
