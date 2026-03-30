#!/usr/bin/env bash
set -euo pipefail

# PROPOSAL/DRAFT
SCRIPT_DIR="$(cd "$(dirname "$0")" ; pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." ; pwd)"

PLIST_SOURCE="$REPO_ROOT/sdk_runtime/ops/launchd/com.schedule_management_tool.sdk_runtime.orchestrator.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.schedule_management_tool.sdk_runtime.orchestrator.plist"

mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SOURCE" "$PLIST_DEST"

launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"
launchctl start com.schedule_management_tool.sdk_runtime.orchestrator
