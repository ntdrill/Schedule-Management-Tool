from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from sdk_runtime.orchestrator.config import load_config, validate_config
from sdk_runtime.orchestrator.permissions import can_write
from sdk_runtime.runtime_paths import path_in_repo, sdk_runtime_dir


def run_health_check() -> Dict[str, Any]:
    result: Dict[str, Any] = {"ok": True, "checks": {}, "warnings": []}
    try:
        config = load_config()
    except Exception as exc:
        result["ok"] = False
        result["checks"]["config_loaded"] = False
        result["warnings"].append(f"config_load_failed: {exc}")
        return result

    result["checks"]["config_loaded"] = True
    warnings = validate_config(config)
    if warnings:
        result["warnings"].extend(warnings)

    result["checks"]["logs_write_allowed"] = can_write(_logs_probe(), "manager")
    result["checks"]["state_write_allowed"] = can_write(_state_probe(), "manager")

    inbox_checks: List[Dict[str, Any]] = []
    agents = config.agents.get("agents", [])
    if isinstance(agents, list):
        for agent in agents:
            if not isinstance(agent, dict):
                continue
            agent_id = str(agent.get("id", ""))
            task_inbox = _resolve_inbox(agent.get("task_inbox"))
            permission_role = str(agent.get("permissions", ""))
            exists = task_inbox.exists()
            is_dir = task_inbox.is_dir()
            inbox_checks.append(
                {
                    "id": agent_id,
                    "path": str(task_inbox),
                    "exists": exists,
                    "is_dir": is_dir,
                    "write_allowed": can_write(task_inbox / ".health", permission_role),
                }
            )

    result["checks"]["task_inbox"] = inbox_checks
    result["ok"] = result["ok"] and _all_ok(inbox_checks, result["checks"])
    return result


def _resolve_inbox(value: Any) -> Path:
    if isinstance(value, Path):
        return value
    if isinstance(value, str):
        path = Path(value)
        if path.is_absolute():
            return path
        return path_in_repo(value)
    return path_in_repo("Agent_workspace")


def _logs_probe() -> Path:
    return sdk_runtime_dir() / "logs" / "health_probe.log"


def _state_probe() -> Path:
    return sdk_runtime_dir() / "state" / "health_probe.json"


def _all_ok(inbox_checks: List[Dict[str, Any]], checks: Dict[str, Any]) -> bool:
    if not checks.get("config_loaded"):
        return False
    if not checks.get("logs_write_allowed"):
        return False
    if not checks.get("state_write_allowed"):
        return False
    for item in inbox_checks:
        if not item.get("exists") or not item.get("is_dir"):
            return False
    return True
