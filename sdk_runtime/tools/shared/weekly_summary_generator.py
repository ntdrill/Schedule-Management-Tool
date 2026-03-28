from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from sdk_runtime.orchestrator.permissions import DEFAULT_ROLE, ensure_write
from sdk_runtime.runtime_paths import path_in_repo


def run(days: int = 7) -> str:
    manager_dir = path_in_repo("Agent_workspace", "Agent_maneger")
    task_mgmt_dir = path_in_repo("Agent_workspace", "Task_Management")
    active_dir = task_mgmt_dir / "02_Active"
    completed_dir = task_mgmt_dir / "03_Completed"
    clock_dir = manager_dir / "クロック受付"
    out_path = manager_dir / "data" / "weekly_summary.md"

    recent_clock = _within_days(clock_dir, days)
    recent_completed = _within_days(completed_dir, days)
    active = list(active_dir.glob("*.txt")) if active_dir.exists() else []

    lines: List[str] = []
    lines.append("# 週次サマリー（自動生成）")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")
    lines.append("## 今週のクロック受付")
    for path in sorted(recent_clock, key=lambda p: p.stat().st_mtime, reverse=True):
        lines.append(f"- {path.name}")
    if not recent_clock:
        lines.append("- なし")
    lines.append("")
    lines.append("## 今週の完了タスク")
    for path in sorted(recent_completed, key=lambda p: p.stat().st_mtime, reverse=True):
        lines.append(f"- {path.name}")
    if not recent_completed:
        lines.append("- なし")
    lines.append("")
    lines.append("## 現在のActive")
    for path in sorted(active):
        lines.append(f"- {path.name}")
    if not active:
        lines.append("- なし")

    if ensure_write(out_path, DEFAULT_ROLE, "weekly_summary"):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")

    return f"Wrote: {out_path}"


def _within_days(directory: Path, days: int) -> List[Path]:
    if not directory.exists():
        return []
    cutoff = datetime.now() - timedelta(days=days)
    paths = []
    for path in directory.glob("*.txt"):
        ts = datetime.fromtimestamp(path.stat().st_mtime)
        if ts >= cutoff:
            paths.append(path)
    return paths
