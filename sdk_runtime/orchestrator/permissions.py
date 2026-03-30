from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json

from sdk_runtime.orchestrator.config import load_yaml_like
from sdk_runtime.orchestrator.logging_utils import append_line
from sdk_runtime.runtime_paths import repo_root, sdk_runtime_dir

DEFAULT_ROLE = "manager"
DENY_LOG_PATH = sdk_runtime_dir() / "logs" / "denied.log"


def ensure_write(path: Path, role: str, reason: str) -> bool:
    if can_write(path, role):
        return True
    _log_denied(path, role, reason)
    return False


def can_write(path: Path, role: str) -> bool:
    roles = load_roles()
    profile = roles.get(role)
    if not isinstance(profile, dict):
        return False
    if profile.get("workspace") != "write":
        return False

    rel = _normalize_path(path)
    denied = _as_list(profile.get("denied_paths"))
    if _matches_any(rel, denied):
        return False

    allowed = _as_list(profile.get("allowed_paths"))
    if not allowed:
        return True
    return _matches_any(rel, allowed)


def load_roles(config_dir: Optional[Path] = None) -> Dict[str, Any]:
    config_root = config_dir or sdk_runtime_dir() / "config"
    data = load_yaml_like(config_root / "permissions.yaml")
    roles = data.get("roles", {})
    return roles if isinstance(roles, dict) else {}


def _log_denied(path: Path, role: str, reason: str) -> None:
    payload = {
        "role": role,
        "path": _normalize_path(path),
        "reason": reason,
    }
    try:
        append_line(DENY_LOG_PATH, json.dumps(payload, ensure_ascii=True))
    except OSError:
        return


def _normalize_path(path: Path) -> str:
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    root = repo_root()
    try:
        rel = resolved.relative_to(root)
        return rel.as_posix()
    except ValueError:
        return resolved.as_posix()


def _matches_any(target: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if not pattern:
            continue
        if target == pattern or target.startswith(f"{pattern}/"):
            return True
    return False


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        return [value] if value.strip() else []
    return []
