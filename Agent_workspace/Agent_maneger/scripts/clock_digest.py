#!/usr/bin/env python3
import os
import glob
import argparse


def read_text(path):
    with open(path, "r") as f:
        return f.read()


def extract_section(content, header_candidates):
    lines = content.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("##"):
            header = line.strip().lstrip("#").strip()
            if header in header_candidates:
                start_idx = i + 1
                break
    if start_idx is None:
        return []

    items = []
    for line in lines[start_idx:]:
        if line.strip().startswith("##"):
            break
        if line.strip().startswith(("-", "・")):
            items.append(line.strip())
    return items


def digest_clock_reports(clock_dir, limit):
    files = glob.glob(os.path.join(clock_dir, "*.txt"))
    files.sort(key=os.path.getmtime, reverse=True)
    files = files[:limit]

    summaries = []
    for path in files:
        content = read_text(path)
        unresolved = extract_section(content, ["未整備"])
        requests = extract_section(content, ["依頼事項", "依頼", "Request for Action"])
        summaries.append({
            "file": os.path.basename(path),
            "unresolved": unresolved,
            "requests": requests,
        })
    return summaries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    clock_dir = os.path.join(manager_dir, "クロック受付")

    summaries = digest_clock_reports(clock_dir, args.limit)
    print("Clock Digest")
    print("============")
    for s in summaries:
        print(f"\n- {s['file']}")
        if s["requests"]:
            print("  [依頼事項]")
            for item in s["requests"]:
                print(f"  {item}")
        if s["unresolved"]:
            print("  [未整備]")
            for item in s["unresolved"]:
                print(f"  {item}")


if __name__ == "__main__":
    main()
