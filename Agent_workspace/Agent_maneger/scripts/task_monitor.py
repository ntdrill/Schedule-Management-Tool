#!/usr/bin/env python3
import os
import glob
import re
from datetime import datetime, timedelta


def read_text(path):
    with open(path, "r") as f:
        return f.read()


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    task_mgmt_dir = os.path.join(os.path.dirname(manager_dir), "Task_Management")
    active_dir = os.path.join(task_mgmt_dir, "02_Active")
    out_path = os.path.join(manager_dir, "data", "task_monitor_report.md")

    today = datetime.now().date()
    stale_threshold = datetime.now() - timedelta(days=7)

    overdue = []
    stale = []

    for path in glob.glob(os.path.join(active_dir, "*.txt")):
        content = read_text(path)
        match = re.search(r"期限.*?:\s*(\d{4}/\d{2}/\d{2})", content)
        if match:
            deadline = datetime.strptime(match.group(1), "%Y/%m/%d").date()
            if deadline < today:
                overdue.append(os.path.basename(path))

        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        if mtime < stale_threshold:
            stale.append(os.path.basename(path))

    lines = []
    lines.append("# タスク監視レポート")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")
    lines.append("## 期限超過")
    for t in overdue:
        lines.append(f"- {t}")
    if not overdue:
        lines.append("- なし")
    lines.append("")
    lines.append("## 更新停滞（7日以上）")
    for t in stale:
        lines.append(f"- {t}")
    if not stale:
        lines.append("- なし")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
