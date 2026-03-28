from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Tuple
import re

from sdk_runtime.runtime_paths import path_in_repo


def run() -> str:
    task_mgmt_dir = path_in_repo("Agent_workspace", "Task_Management")
    active_dir = task_mgmt_dir / "02_Active"
    clock_dir = path_in_repo("Agent_workspace", "Agent_maneger", "クロック受付")

    lines: List[str] = []
    lines.append("Checking overdue tasks...")
    overdue = _overdue_tasks(active_dir)
    if overdue:
        lines.append("")
        lines.append("[ALERT] Overdue Tasks:")
        for task, date in overdue:
            lines.append(f"- {task} (Deadline: {date})")
    else:
        lines.append("No overdue tasks found.")

    lines.append("")
    lines.append("Checking clock files...")
    lines.append("Recent 3 reports:")
    recent = _recent_clock(clock_dir, 3)
    for filename in recent:
        lines.append(f"- {filename}")

    return "\n".join(lines)


def _overdue_tasks(active_dir: Path) -> List[Tuple[str, str]]:
    if not active_dir.exists():
        return []
    today = datetime.now().date()
    tasks = list(active_dir.glob("*.txt"))
    overdue: List[Tuple[str, str]] = []
    for task_path in tasks:
        content = task_path.read_text(encoding="utf-8")
        match = re.search(r"期限.*(\\d{4}/\\d{2}/\\d{2})", content)
        if match:
            deadline_str = match.group(1)
            deadline = datetime.strptime(deadline_str, "%Y/%m/%d").date()
            if deadline < today:
                overdue.append((task_path.name, deadline_str))
    return overdue


def _recent_clock(clock_dir: Path, limit: int) -> List[str]:
    if not clock_dir.exists():
        return []
    files = list(clock_dir.glob("*.txt"))
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return [path.name for path in files[:limit]]
