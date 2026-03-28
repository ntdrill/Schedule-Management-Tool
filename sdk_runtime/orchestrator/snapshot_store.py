from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
import json

from sdk_runtime.runtime_paths import sdk_runtime_dir
from sdk_runtime.watchers.base import Snapshot


@dataclass(frozen=True)
class StoredSnapshot:
    files: Dict[str, float]

    def to_snapshot(self) -> Snapshot:
        return Snapshot(files=self.files)


def snapshots_dir() -> Path:
    return sdk_runtime_dir() / "state"


def _snapshot_path(name: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in name)
    if not safe:
        safe = "_"
    return snapshots_dir() / f"{safe}.json"


def load_snapshot(name: str) -> Optional[Snapshot]:
    path = _snapshot_path(name)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    files = data.get("files", {})
    if not isinstance(files, dict):
        return None
    return Snapshot(files={str(k): float(v) for k, v in files.items()})


def save_snapshot(name: str, snapshot: Snapshot) -> None:
    path = _snapshot_path(name)
    from sdk_runtime.orchestrator.permissions import DEFAULT_ROLE, ensure_write

    if not ensure_write(path, DEFAULT_ROLE, "snapshot_save"):
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"files": snapshot.files}
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
