from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
import json

from sdk_runtime.orchestrator.events import WatchEvent
from sdk_runtime.runtime_paths import path_in_repo


@dataclass(frozen=True)
class AgentRoute:
    agent_id: str
    task_inbox: Path
    subscriptions: List[str]


def load_routes(config: Dict[str, Any], roles: Dict[str, Any] | None = None) -> List[AgentRoute]:
    routes: List[AgentRoute] = []
    entries = config.get("agents", [])
    if not isinstance(entries, list):
        return routes
    role_map = roles if isinstance(roles, dict) else {}

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        agent_id = str(entry.get("id", "")).strip()
        task_inbox_value = str(entry.get("task_inbox", "")).strip()
        permissions_key = str(entry.get("permissions", "")).strip()
        if not agent_id or not task_inbox_value:
            continue
        if permissions_key and role_map and permissions_key not in role_map:
            continue

        task_inbox = Path(task_inbox_value)
        if not task_inbox.is_absolute():
            task_inbox = path_in_repo(task_inbox_value)

        subscriptions = _normalize_subscriptions(entry.get("subscriptions", []))
        routes.append(
            AgentRoute(
                agent_id=agent_id,
                task_inbox=task_inbox,
                subscriptions=subscriptions,
            )
        )

    return routes


def dispatch_events(events: Iterable[WatchEvent], routes: List[AgentRoute]) -> int:
    dispatched = 0
    for event in events:
        for route in routes:
            if not _should_dispatch(event, route):
                continue
            _write_inbox_event(event, route)
            dispatched += 1
    return dispatched


def _should_dispatch(event: WatchEvent, route: AgentRoute) -> bool:
    if not route.subscriptions:
        return False
    return _source_matches_any(event.source, route.subscriptions)


def _write_inbox_event(event: WatchEvent, route: AgentRoute) -> None:
    from sdk_runtime.orchestrator.permissions import DEFAULT_ROLE, ensure_write

    route.task_inbox.mkdir(parents=True, exist_ok=True)
    envelope = build_task_envelope(
        task_type="watch_event",
        source="orchestrator",
        payload={
            "watcher": event.source,
            "event_id": event.event_id,
            "created_at": event.created_at,
            "added": event.added,
            "removed": event.removed,
            "modified": event.modified,
        },
    )
    path = route.task_inbox / f"task_{event.event_id}.json"
    if not ensure_write(path, DEFAULT_ROLE, "task_inbox_write"):
        return
    path.write_text(json.dumps(envelope, ensure_ascii=True, indent=2), encoding="utf-8")


def _normalize_subscriptions(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return []


def _source_matches_any(source: str, patterns: List[str]) -> bool:
    return any(_source_matches(source, pattern) for pattern in patterns)


def _source_matches(source: str, pattern: str) -> bool:
    if pattern in ("*", "all"):
        return True
    if pattern == "inbox":
        return source.startswith("inbox:")
    if pattern.endswith("*"):
        return source.startswith(pattern[:-1])
    if pattern.endswith(":"):
        return source.startswith(pattern)
    return source == pattern


def build_task_envelope(task_type: str, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": f"task_{payload.get('event_id', now)}",
        "type": task_type,
        "created_at": now,
        "source": source,
        "payload": payload,
    }
