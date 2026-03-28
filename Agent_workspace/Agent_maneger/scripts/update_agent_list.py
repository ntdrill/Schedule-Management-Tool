#!/usr/bin/env python3
import os
import glob
from datetime import datetime


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    agent_workspace = os.path.dirname(manager_dir)
    out_path = os.path.join(manager_dir, "data", "agent_list_report.md")

    agent_dirs = []
    for path in glob.glob(os.path.join(agent_workspace, "*")):
        if os.path.isdir(path) and path != manager_dir:
            agent_dirs.append(os.path.basename(path))
    agent_dirs.sort()

    lines = []
    lines.append("# エージェント一覧レポート")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")
    for name in agent_dirs:
        lines.append(f"- {name}")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
