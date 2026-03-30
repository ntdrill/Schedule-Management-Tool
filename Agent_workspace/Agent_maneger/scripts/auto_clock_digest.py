#!/usr/bin/env python3
import os
import subprocess


def run_script(path, args):
    cmd = ["python3", path] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip())
    else:
        print(result.stdout.strip())


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    digest = os.path.join(scripts_dir, "clock_digest.py")
    indexer = os.path.join(scripts_dir, "unresolved_index.py")
    proposal = os.path.join(scripts_dir, "unresolved_to_proposal.py")

    run_script(digest, [])
    run_script(indexer, [])
    run_script(proposal, [])


if __name__ == "__main__":
    main()
