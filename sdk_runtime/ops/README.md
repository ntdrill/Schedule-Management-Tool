# Ops Standard (PROPOSAL/DRAFT)

Standard runtime method: launchd.
Fallback/dev method: tmux.

## Standard (launchd)
- Use: sdk_runtime/ops/launchd/install.sh
- Stop: sdk_runtime/ops/launchd/uninstall.sh

## Fallback (tmux)
- Start: sdk_runtime/ops/tmux/run_orchestrator.sh
- Stop: sdk_runtime/ops/tmux/stop_orchestrator.sh
- Attach: sdk_runtime/ops/tmux/attach_orchestrator.sh

See:
- launchd: sdk_runtime/ops/launchd
- tmux: sdk_runtime/ops/tmux
