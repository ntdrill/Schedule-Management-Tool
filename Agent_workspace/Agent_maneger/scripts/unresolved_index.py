#!/usr/bin/env python3
import os
import glob


def read_text(path):
    with open(path, "r") as f:
        return f.read()


def extract_unresolved(content):
    lines = content.splitlines()
    items = []
    in_section = False
    for line in lines:
        if line.strip().startswith("##"):
            header = line.strip().lstrip("#").strip()
            in_section = header == "未整備"
            continue
        if in_section and line.strip().startswith(("-", "・")):
            items.append(line.strip())
    return items


def build_index(clock_dir):
    files = glob.glob(os.path.join(clock_dir, "*.txt"))
    files.sort()
    index = []
    for path in files:
        items = extract_unresolved(read_text(path))
        if items:
            index.append((os.path.basename(path), items))
    return index


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    clock_dir = os.path.join(manager_dir, "クロック受付")
    out_path = os.path.join(manager_dir, "data", "unresolved_index.md")

    index = build_index(clock_dir)
    lines = []
    lines.append("# 未整備インデックス")
    lines.append("")
    for filename, items in index:
        lines.append(f"## {filename}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
