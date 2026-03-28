#!/usr/bin/env python3
import os
import glob
from datetime import datetime


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    error_dir = os.path.join(manager_dir, "error_report")
    out_path = os.path.join(manager_dir, "data", "error_report_digest.md")

    lines = []
    lines.append("# エラー報告サマリー")
    lines.append(f"- 生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    lines.append("")

    if not os.path.exists(error_dir):
        lines.append("error_report ディレクトリが存在しません。")
    else:
        files = glob.glob(os.path.join(error_dir, "*.txt"))
        files.sort(key=os.path.getmtime, reverse=True)
        if not files:
            lines.append("報告なし。")
        else:
            for path in files:
                ts = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y/%m/%d %H:%M")
                lines.append(f"- {os.path.basename(path)} ({ts})")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
