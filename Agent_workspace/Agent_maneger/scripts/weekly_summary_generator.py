#!/usr/bin/env python3
import os
import glob
from datetime import datetime, timedelta


def within_days(path, days):
    ts = datetime.fromtimestamp(os.path.getmtime(path))
    return ts >= datetime.now() - timedelta(days=days)


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    task_mgmt_dir = os.path.join(os.path.dirname(manager_dir), "Task_Management")
    active_dir = os.path.join(task_mgmt_dir, "02_Active")
    completed_dir = os.path.join(task_mgmt_dir, "03_Completed")
    clock_dir = os.path.join(manager_dir, "クロック受付")
    out_path = os.path.join(manager_dir, "data", "weekly_summary.md")

    recent_clock = [p for p in glob.glob(os.path.join(clock_dir, "*.txt")) if within_days(p, 7)]
    recent_completed = [p for p in glob.glob(os.path.join(completed_dir, "*.txt")) if within_days(p, 7)]
    active = glob.glob(os.path.join(active_dir, "*.txt"))

    lines = []
    lines.append("# 週次サマリー（自動生成）")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")
    lines.append("## 今週のクロック受付")
    for p in sorted(recent_clock, key=os.path.getmtime, reverse=True):
        lines.append(f"- {os.path.basename(p)}")
    if not recent_clock:
        lines.append("- なし")
    lines.append("")
    lines.append("## 今週の完了タスク")
    for p in sorted(recent_completed, key=os.path.getmtime, reverse=True):
        lines.append(f"- {os.path.basename(p)}")
    if not recent_completed:
        lines.append("- なし")
    lines.append("")
    lines.append("## 現在のActive")
    for p in sorted(active):
        lines.append(f"- {os.path.basename(p)}")
    if not active:
        lines.append("- なし")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
