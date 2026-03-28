from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sdk_runtime.runtime_paths import sdk_runtime_dir


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeConfig:
    agents: Dict[str, Any]
    permissions: Dict[str, Any]
    tools_registry: Dict[str, Any]
    thresholds: Dict[str, Any]
    cache_manifest: Dict[str, Any]


def load_config(config_dir: Optional[Path] = None) -> RuntimeConfig:
    config_root = config_dir or sdk_runtime_dir() / "config"
    return RuntimeConfig(
        agents=load_yaml_like(config_root / "agents.yaml"),
        permissions=load_yaml_like(config_root / "permissions.yaml"),
        tools_registry=load_yaml_like(config_root / "tools_registry.yaml"),
        thresholds=load_yaml_like(config_root / "thresholds.yaml"),
        cache_manifest=load_yaml_like(config_root / "cache_manifest.yaml"),
    )


def validate_config(config: RuntimeConfig) -> List[str]:
    warnings: List[str] = []

    agents = config.agents.get("agents", [])
    if not isinstance(agents, list):
        warnings.append("agents: not a list")
        return warnings

    roles = config.permissions.get("roles", {})
    if not isinstance(roles, dict):
        warnings.append("permissions.roles: not a map")
        roles = {}
    if not roles:
        warnings.append("permissions.roles: empty")

    required_fields = ["id", "role", "permissions", "task_inbox"]
    for index, agent in enumerate(agents):
        if not isinstance(agent, dict):
            warnings.append(f"agents[{index}]: not a map")
            continue
        for field in required_fields:
            value = str(agent.get(field, "")).strip()
            if not value:
                warnings.append(f"agents[{index}]: missing {field}")
        permission_key = str(agent.get("permissions", "")).strip()
        if permission_key and permission_key not in roles:
            warnings.append(f"agents[{index}]: permissions not found: {permission_key}")

    return warnings


def load_yaml_like(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config not found: {path}")
    text = path.read_text(encoding="utf-8")
    return parse_simple_yaml(text)


def parse_simple_yaml(text: str) -> Dict[str, Any]:
    """
    Minimal YAML-like parser for draft configs.
    Supports:
    - top-level key: value
    - top-level key: (nested mapping or list with 2-space indent)
    - list items: "- key: value" under a top-level key
    - list item fields with 4-space indent
    - simple scalars: null, true/false, numbers, strings
    - inline list: [a, b, c]
    - empty list [] and empty dict {}
    """
    result: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_map: Optional[Dict[str, Any]] = None
    current_submap: Optional[Dict[str, Any]] = None
    current_list: Optional[list] = None
    current_list_item: Optional[Dict[str, Any]] = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            key, value = split_key_value(stripped)
            current_key = key
            current_map = None
            current_submap = None
            current_list = None
            current_list_item = None
            if value is None:
                result[key] = {}
                current_map = result[key]
            else:
                result[key] = parse_scalar(value)
        elif indent == 2 and current_key is not None:
            current_submap = None
            if stripped.startswith("- "):
                if current_list is None:
                    current_list = []
                    result[current_key] = current_list
                    current_map = None
                item_line = stripped[2:].strip()
                current_list_item = {}
                current_list.append(current_list_item)
                if item_line:
                    key, value = split_key_value(item_line)
                    current_list_item[key] = parse_scalar(value) if value is not None else {}
            else:
                if current_list is not None:
                    continue
                if current_map is None:
                    current_map = {}
                    result[current_key] = current_map
                key, value = split_key_value(stripped)
                if value is None:
                    current_map[key] = {}
                    current_submap = current_map[key]
                else:
                    current_map[key] = parse_scalar(value)
        elif indent == 4:
            if current_list_item is not None:
                key, value = split_key_value(stripped)
                current_list_item[key] = parse_scalar(value) if value is not None else {}
            elif current_submap is not None:
                key, value = split_key_value(stripped)
                current_submap[key] = parse_scalar(value) if value is not None else {}
        else:
            # Deeper nesting is not supported in this draft parser.
            continue

    return result


def split_key_value(line: str) -> Tuple[str, Optional[str]]:
    if ":" not in line:
        raise ConfigError(f"Invalid line (no key/value): {line}")
    key, raw_value = line.split(":", 1)
    key = key.strip()
    value = raw_value.strip()
    if value == "":
        return key, None
    return key, value


def parse_scalar(value: str) -> Any:
    value = _strip_quotes(value)
    lowered = value.lower()
    if lowered == "null":
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        items = [item.strip() for item in inner.split(",")]
        return [parse_scalar(item) for item in items]

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value
