from __future__ import annotations

from pathlib import Path
from typing import List
import shutil

from sdk_runtime.orchestrator.permissions import DEFAULT_ROLE, ensure_write
from sdk_runtime.runtime_paths import path_in_repo


def run(apply: bool = False) -> str:
    task_mgmt_dir = path_in_repo("Agent_workspace", "Task_Management")
    proposals_dir = task_mgmt_dir / "01_Proposals"
    active_dir = task_mgmt_dir / "02_Active"
    completed_dir = task_mgmt_dir / "03_Completed"

    proposal_files = list(proposals_dir.glob("*.txt")) if proposals_dir.exists() else []
    active_files = list(active_dir.glob("*.txt")) if active_dir.exists() else []

    to_active = [path for path in proposal_files if _has_assignment(path)]
    to_completed = [path for path in active_files if _has_completion(path)]

    lines: List[str] = []
    lines.append("Task Mover")
    lines.append("==========")
    lines.append(f"to_active: {len(to_active)}")
    lines.append(f"to_completed: {len(to_completed)}")

    dry_run = not apply
    _move_files(to_active, active_dir, dry_run, lines)
    _move_files(to_completed, completed_dir, dry_run, lines)
    return "\n".join(lines)


def _has_assignment(path: Path) -> bool:
    return "## Assignment" in path.read_text(encoding="utf-8")


def _has_completion(path: Path) -> bool:
    return "## 完了報告" in path.read_text(encoding="utf-8")


def _move_files(files: List[Path], dest_dir: Path, dry_run: bool, lines: List[str]) -> None:
    if dry_run:
        for path in files:
            dest = dest_dir / path.name
            lines.append(f"[DRY] move {path} -> {dest}")
        return

    dest_dir.mkdir(parents=True, exist_ok=True)
    for path in files:
        dest = dest_dir / path.name
        if not ensure_write(dest, DEFAULT_ROLE, "task_move"):
            lines.append(f"[DENY] move {path} -> {dest}")
            continue
        shutil.move(str(path), str(dest))
        lines.append(f"moved: {dest}")
