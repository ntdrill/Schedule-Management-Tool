from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from sdk_runtime.orchestrator.permissions import DEFAULT_ROLE, ensure_write
from sdk_runtime.runtime_paths import path_in_repo


def run(dry_run: bool = False) -> str:
    clock_dir = path_in_repo("Agent_workspace", "Agent_maneger", "クロック受付")
    state_path = path_in_repo("Agent_workspace", "Agent_maneger", "data", "clock_last_seen.txt")

    last_seen = _read_last_seen(state_path)
    files = _list_clock_files(clock_dir)
    new_files = [path for path in files if path.stat().st_mtime > last_seen]

    lines: List[str] = []
    lines.append("Clock Diff")
    lines.append("==========")
    if not new_files:
        lines.append("No new clock reports.")
    else:
        for path in new_files:
            ts = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y/%m/%d %H:%M")
            lines.append(f"- {path.name} ({ts})")

    if not dry_run and files:
        latest_ts = files[-1].stat().st_mtime
        if ensure_write(state_path, DEFAULT_ROLE, "clock_last_seen"):
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state_path.write_text(str(latest_ts), encoding="utf-8")

    return "\n".join(lines)


def _list_clock_files(clock_dir: Path) -> List[Path]:
    if not clock_dir.exists():
        return []
    files = list(clock_dir.glob("*.txt"))
    files.sort(key=lambda path: path.stat().st_mtime)
    return files


def _read_last_seen(path: Path) -> float:
    if not path.exists():
        return 0.0
    try:
        value = path.read_text(encoding="utf-8").strip()
        return float(value) if value else 0.0
    except (OSError, ValueError):
        return 0.0
