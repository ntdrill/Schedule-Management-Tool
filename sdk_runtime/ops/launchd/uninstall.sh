#!/usr/bin/env bash
set -euo pipefail

# PROPOSAL/DRAFT
PLIST_DEST="$HOME/Library/LaunchAgents/com.schedule_management_tool.sdk_runtime.orchestrator.plist"

launchctl unload "$PLIST_DEST" 2>/dev/null || true
rm -f "$PLIST_DEST"
