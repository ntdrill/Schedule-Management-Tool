from __future__ import annotations

from typing import Dict

from sdk_runtime.runtime_paths import path_in_repo
from sdk_runtime.watchers.base import FileSystemWatcher


CLOCK_ROOT = path_in_repo("Agent_workspace", "Agent_maneger", "クロック受付")


def build_watcher() -> FileSystemWatcher:
    return FileSystemWatcher(name="clock", root=CLOCK_ROOT)


def scan_existing() -> Dict[str, object]:
    watcher = build_watcher()
    snapshot = watcher.scan()
    return {
        "name": watcher.name,
        "root": str(watcher.root),
        "total_files": len(snapshot.files),
    }


def main() -> int:
    result = scan_existing()
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
