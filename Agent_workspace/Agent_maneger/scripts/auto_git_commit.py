#!/usr/bin/env python3
import os
import subprocess
import argparse


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="コミットを実行")
    parser.add_argument("--message", default="chore: update manager artifacts")
    args = parser.parse_args()

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(scripts_dir))

    status = run(["git", "status", "--porcelain"], repo_root)
    if status.returncode != 0:
        print(status.stderr.strip())
        return
    if not status.stdout.strip():
        print("No changes to commit.")
        return

    print("Changes detected:")
    print(status.stdout.strip())

    if not args.apply:
        print("Dry run. Use --apply to commit.")
        return

    add = run(["git", "add", "."], repo_root)
    if add.returncode != 0:
        print(add.stderr.strip())
        return

    commit = run(["git", "commit", "-m", args.message], repo_root)
    if commit.returncode != 0:
        print(commit.stderr.strip())
        return

    print(commit.stdout.strip())


if __name__ == "__main__":
    main()
