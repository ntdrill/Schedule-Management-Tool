#!/usr/bin/env bash
set -euo pipefail

# PROPOSAL/DRAFT
SESSION="sdk_runtime_orchestrator"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux kill-session -t "$SESSION"
  echo "stopped: $SESSION"
else
  echo "tmux session not running: $SESSION"
fi
