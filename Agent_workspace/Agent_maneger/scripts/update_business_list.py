#!/usr/bin/env python3
import os
import glob
from datetime import datetime


def list_tasks(directory):
    tasks = []
    for path in sorted(glob.glob(os.path.join(directory, "*.txt"))):
        tasks.append(os.path.basename(path))
    return tasks


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    task_mgmt_dir = os.path.join(os.path.dirname(manager_dir), "Task_Management")
    active_dir = os.path.join(task_mgmt_dir, "02_Active")
    completed_dir = os.path.join(task_mgmt_dir, "03_Completed")
    out_path = os.path.join(manager_dir, "data", "business_list_generated.md")

    active = list_tasks(active_dir)
    completed = list_tasks(completed_dir)

    lines = []
    lines.append("# 業務リスト（自動生成）")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")
    lines.append("## 進行中")
    for t in active:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("## 完了")
    for t in completed:
        lines.append(f"- {t}")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
