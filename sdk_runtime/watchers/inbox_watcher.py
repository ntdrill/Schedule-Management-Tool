from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from sdk_runtime.runtime_paths import path_in_repo
from sdk_runtime.watchers.base import FileSystemWatcher


AGENTS_ROOT = path_in_repo("Agent_workspace")


def find_inboxes() -> List[Path]:
    if not AGENTS_ROOT.exists():
        return []
    return [path for path in AGENTS_ROOT.rglob("Task_Inbox") if path.is_dir()]


def build_watchers() -> List[FileSystemWatcher]:
    return [
        FileSystemWatcher(name=f"inbox:{path.parent.name}", root=path)
        for path in find_inboxes()
    ]


def scan_existing() -> Dict[str, object]:
    watchers = build_watchers()
    results = []
    for watcher in watchers:
        snapshot = watcher.scan()
        results.append(
            {
                "name": watcher.name,
                "root": str(watcher.root),
                "total_files": len(snapshot.files),
            }
        )
    return {"inboxes": results, "count": len(results)}


def main() -> int:
    result = scan_existing()
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
