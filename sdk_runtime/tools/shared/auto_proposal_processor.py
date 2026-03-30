from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from sdk_runtime.orchestrator.permissions import DEFAULT_ROLE, ensure_write
from sdk_runtime.runtime_paths import path_in_repo


def run() -> str:
    manager_dir = path_in_repo("Agent_workspace", "Agent_maneger")
    task_mgmt_dir = path_in_repo("Agent_workspace", "Task_Management")
    proposals_dir = task_mgmt_dir / "01_Proposals"
    out_path = manager_dir / "data" / "proposal_digest.md"

    lines: List[str] = []
    lines.append("# 提案ファイル要約")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")

    if proposals_dir.exists():
        files = list(proposals_dir.glob("*.txt"))
        files.sort()
        for path in files:
            content = path.read_text(encoding="utf-8").strip()
            lines.append(f"## {path.name}")
            lines.append(content)
            lines.append("")

    if ensure_write(out_path, DEFAULT_ROLE, "proposal_digest"):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")

    return f"Wrote: {out_path}"
