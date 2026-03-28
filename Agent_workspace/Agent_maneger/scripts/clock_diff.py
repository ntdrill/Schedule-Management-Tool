#!/usr/bin/env python3
import os
import glob
import argparse
from datetime import datetime


def list_clock_files(clock_dir):
    files = glob.glob(os.path.join(clock_dir, "*.txt"))
    files.sort(key=os.path.getmtime)
    return files


def read_last_seen(path):
    if not os.path.exists(path):
        return 0.0
    with open(path, "r") as f:
        value = f.read().strip()
    return float(value) if value else 0.0


def write_last_seen(path, timestamp):
    with open(path, "w") as f:
        f.write(str(timestamp))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    clock_dir = os.path.join(manager_dir, "クロック受付")
    state_path = os.path.join(manager_dir, "data", "clock_last_seen.txt")

    last_seen = read_last_seen(state_path)
    files = list_clock_files(clock_dir)
    new_files = [f for f in files if os.path.getmtime(f) > last_seen]

    print("Clock Diff")
    print("==========")
    if not new_files:
        print("No new clock reports.")
    else:
        for f in new_files:
            ts = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y/%m/%d %H:%M")
            print(f"- {os.path.basename(f)} ({ts})")

    if not args.dry_run and files:
        latest_ts = os.path.getmtime(files[-1])
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        write_last_seen(state_path, latest_ts)


if __name__ == "__main__":
    main()
