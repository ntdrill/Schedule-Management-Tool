# launchd (PROPOSAL/DRAFT)

This directory contains launchd artifacts to run the orchestrator as a daemon.
Standard method: launchd.

## Files
- `com.schedule_management_tool.sdk_runtime.orchestrator.plist`
- `install.sh`
- `uninstall.sh`

## Usage
- Install: `bash sdk_runtime/ops/launchd/install.sh`
- Uninstall: `bash sdk_runtime/ops/launchd/uninstall.sh`

## Notes
- Update paths if the repo location changes.
- Logs are written to `sdk_runtime/logs/launchd.out.log` and `launchd.err.log`.
