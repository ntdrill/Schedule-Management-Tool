from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


DEFAULT_IGNORE_DIRS = {
    ".git",
    ".cursor",
    "__pycache__",
    ".venv",
    "node_modules",
}


@dataclass(frozen=True)
class Snapshot:
    files: Dict[str, float]


@dataclass(frozen=True)
class Diff:
    added: List[str]
    removed: List[str]
    modified: List[str]


class FileSystemWatcher:
    def __init__(
        self,
        name: str,
        root: Path,
        ignore_dirs: Optional[Iterable[str]] = None,
        ignore_files: Optional[Iterable[str]] = None,
    ) -> None:
        self.name = name
        self.root = root
        self.ignore_dirs: Set[str] = set(ignore_dirs or DEFAULT_IGNORE_DIRS)
        self.ignore_files: Set[str] = set(ignore_files or [])
        self._snapshot = Snapshot(files={})

    def scan(self) -> Snapshot:
        files: Dict[str, float] = {}
        if not self.root.exists():
            return Snapshot(files={})

        for path in self._iter_files(self.root):
            try:
                files[str(path)] = path.stat().st_mtime
            except OSError:
                continue

        return Snapshot(files=files)

    def diff(self, new_snapshot: Snapshot) -> Diff:
        old_files = self._snapshot.files
        new_files = new_snapshot.files
        added = [path for path in new_files if path not in old_files]
        removed = [path for path in old_files if path not in new_files]
        modified = [
            path
            for path in new_files
            if path in old_files and new_files[path] != old_files[path]
        ]
        return Diff(added=added, removed=removed, modified=modified)

    def set_snapshot(self, snapshot: Snapshot) -> None:
        self._snapshot = snapshot

    def get_snapshot(self) -> Snapshot:
        return self._snapshot

    def poll_once(self) -> Tuple[Snapshot, Diff]:
        new_snapshot = self.scan()
        diff = self.diff(new_snapshot)
        self._snapshot = new_snapshot
        return new_snapshot, diff

    def _iter_files(self, root: Path) -> Iterable[Path]:
        for entry in root.iterdir():
            if entry.is_dir():
                if entry.name in self.ignore_dirs:
                    continue
                yield from self._iter_files(entry)
            elif entry.is_file():
                if entry.name in self.ignore_files:
                    continue
                yield entry
