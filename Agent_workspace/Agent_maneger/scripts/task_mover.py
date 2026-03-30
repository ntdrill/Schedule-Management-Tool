#!/usr/bin/env python3
import os
import glob
import argparse
import shutil


def has_assignment(path):
    with open(path, "r") as f:
        return "## Assignment" in f.read()


def has_completion(path):
    with open(path, "r") as f:
        return "## 完了報告" in f.read()


def move_files(files, dest_dir, dry_run):
    for path in files:
        dest = os.path.join(dest_dir, os.path.basename(path))
        if dry_run:
            print(f"[DRY] move {path} -> {dest}")
        else:
            shutil.move(path, dest)
            print(f"moved: {dest}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="実行する")
    args = parser.parse_args()

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    task_mgmt_dir = os.path.join(os.path.dirname(manager_dir), "Task_Management")
    proposals_dir = os.path.join(task_mgmt_dir, "01_Proposals")
    active_dir = os.path.join(task_mgmt_dir, "02_Active")
    completed_dir = os.path.join(task_mgmt_dir, "03_Completed")

    proposal_files = glob.glob(os.path.join(proposals_dir, "*.txt"))
    active_files = glob.glob(os.path.join(active_dir, "*.txt"))

    to_active = [p for p in proposal_files if has_assignment(p)]
    to_completed = [p for p in active_files if has_completion(p)]

    print("Task Mover")
    print("==========")
    print(f"to_active: {len(to_active)}")
    print(f"to_completed: {len(to_completed)}")

    dry_run = not args.apply
    move_files(to_active, active_dir, dry_run)
    move_files(to_completed, completed_dir, dry_run)


if __name__ == "__main__":
    main()
