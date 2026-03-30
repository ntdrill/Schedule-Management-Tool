from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List
import json
import uuid


@dataclass(frozen=True)
class WatchEvent:
    event_id: str
    source: str
    created_at: str
    added: List[str]
    removed: List[str]
    modified: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "event_id": self.event_id,
            "source": self.source,
            "created_at": self.created_at,
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
        }


def build_event(source: str, added: List[str], removed: List[str], modified: List[str]) -> WatchEvent:
    now = datetime.now(timezone.utc).isoformat()
    return WatchEvent(
        event_id=str(uuid.uuid4()),
        source=source,
        created_at=now,
        added=added,
        removed=removed,
        modified=modified,
    )


def write_events(events: Iterable[WatchEvent], path: Path) -> None:
    if not events:
        return
    from sdk_runtime.orchestrator.logging_utils import append_line
    from sdk_runtime.orchestrator.permissions import DEFAULT_ROLE, ensure_write

    if not ensure_write(path, DEFAULT_ROLE, "events_log"):
        return
    for event in events:
        append_line(path, json.dumps(event.to_dict(), ensure_ascii=True))
