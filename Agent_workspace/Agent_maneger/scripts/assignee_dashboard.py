#!/usr/bin/env python3
import os
import glob
import re
from datetime import datetime


def read_text(path):
    with open(path, "r") as f:
        return f.read()


def extract_assignee(content):
    match = re.search(r"Assignee.*?:\s*(.+)", content)
    return match.group(1).strip() if match else "Unassigned"


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    task_mgmt_dir = os.path.join(os.path.dirname(manager_dir), "Task_Management")
    active_dir = os.path.join(task_mgmt_dir, "02_Active")
    out_path = os.path.join(manager_dir, "data", "assignee_dashboard.md")

    dashboard = {}
    for path in glob.glob(os.path.join(active_dir, "*.txt")):
        content = read_text(path)
        assignee = extract_assignee(content)
        dashboard.setdefault(assignee, []).append(os.path.basename(path))

    lines = []
    lines.append("# Assigneeダッシュボード")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")
    for assignee in sorted(dashboard.keys()):
        lines.append(f"## {assignee}")
        for t in sorted(dashboard[assignee]):
            lines.append(f"- {t}")
        lines.append("")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
