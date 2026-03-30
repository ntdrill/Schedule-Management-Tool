#!/usr/bin/env bash
set -euo pipefail

# PROPOSAL/DRAFT
SCRIPT_DIR="$(cd "$(dirname "$0")" ; pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." ; pwd)"

SESSION="sdk_runtime_orchestrator"
CMD="python3 -m sdk_runtime.orchestrator.main --run"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "tmux session already running: $SESSION"
  exit 0
fi

tmux new-session -d -s "$SESSION" -c "$REPO_ROOT" "$CMD"
echo "started: $SESSION"
