from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MAX_BYTES = 10 * 1024 * 1024


def append_line(path: Path, line: str, max_bytes: int = DEFAULT_MAX_BYTES) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = line if line.endswith("\n") else f"{line}\n"
    _rotate_if_needed(path, max_bytes=max_bytes, incoming_size=len(data.encode("utf-8")))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(data)


def _rotate_if_needed(path: Path, max_bytes: int, incoming_size: int) -> None:
    if not path.exists():
        return
    try:
        size = path.stat().st_size
    except OSError:
        return
    if size + incoming_size < max_bytes:
        return
    rotated = path.with_name(f"{path.name}.{_timestamp()}")
    try:
        path.rename(rotated)
    except OSError:
        return


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
