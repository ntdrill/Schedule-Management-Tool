#!/usr/bin/env python3
import os
import glob
from datetime import datetime


def read_text(path):
    with open(path, "r") as f:
        return f.read()


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    task_mgmt_dir = os.path.join(os.path.dirname(manager_dir), "Task_Management")
    proposals_dir = os.path.join(task_mgmt_dir, "01_Proposals")
    out_path = os.path.join(manager_dir, "data", "proposal_digest.md")

    files = glob.glob(os.path.join(proposals_dir, "*.txt"))
    files.sort()

    lines = []
    lines.append("# 提案ファイル要約")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")
    for path in files:
        content = read_text(path)
        lines.append(f"## {os.path.basename(path)}")
        lines.append(content.strip())
        lines.append("")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
