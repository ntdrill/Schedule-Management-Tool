#!/usr/bin/env python3
import os
import glob
import re
from datetime import datetime


def read_text(path):
    with open(path, "r") as f:
        return f.read()


def extract_field(pattern, content):
    match = re.search(pattern, content)
    return match.group(1).strip() if match else ""


def collect_active_tasks(active_dir):
    tasks = []
    for path in sorted(glob.glob(os.path.join(active_dir, "*.txt"))):
        content = read_text(path)
        assignee = extract_field(r"Assignee.*?:\s*(.+)", content)
        deadline = extract_field(r"期限.*?:\s*(\d{4}/\d{2}/\d{2})", content)
        mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y/%m/%d %H:%M")
        tasks.append({
            "file": os.path.basename(path),
            "assignee": assignee,
            "deadline": deadline,
            "mtime": mtime,
        })
    return tasks


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    task_mgmt_dir = os.path.join(os.path.dirname(manager_dir), "Task_Management")
    active_dir = os.path.join(task_mgmt_dir, "02_Active")
    out_path = os.path.join(manager_dir, "data", "active_tasks_report.md")

    tasks = collect_active_tasks(active_dir)
    lines = []
    lines.append("# Activeタスク棚卸し")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")
    lines.append("| タスク | Assignee | 期限 | 更新時刻 |")
    lines.append("| --- | --- | --- | --- |")
    for t in tasks:
        lines.append(f"| {t['file']} | {t['assignee'] or '-'} | {t['deadline'] or '-'} | {t['mtime']} |")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
