# SDK Runtime (DRAFT)

This directory is the initial scaffold for the SDK-based runtime.

FACTS (source-based)
- The runtime is expected to load agent and permission configs at bootstrap.
- Watchers are expected to monitor task folders, progress reports, clock inbox, and per-agent inboxes.
- The orchestrator is expected to dispatch events to the correct agent inbox and resume only needed agents.

PROPOSAL/DRAFT
- Directory layout here is a starting point and may change.
- Watcher scheduling policy and thresholds are defined in `config/thresholds.yaml` (draft values).
- Permissions model is defined in `config/permissions.yaml` (draft values).

NEXT STEPS (PROPOSAL/DRAFT)
- Add tool wrappers for existing scripts.
- Add health checks and log rotation.

HOW TO RUN (PROPOSAL/DRAFT)
- Scan once: python3 -m sdk_runtime.orchestrator.main --scan
- Poll once: python3 -m sdk_runtime.orchestrator.main --poll-once
- Poll + dispatch: python3 -m sdk_runtime.orchestrator.main --dispatch
- Run loop: python3 -m sdk_runtime.orchestrator.main --run
- Health check: python3 -m sdk_runtime.orchestrator.main --health

TASK FORMAT (PROPOSAL/DRAFT)
- See sdk_runtime/docs/task_inbox_format.md

THRESHOLDS / FILTERS (PROPOSAL/DRAFT)
- See sdk_runtime/config/thresholds.yaml
- Per-watcher filters: min_changes, include_paths, exclude_paths
- Dispatch filters: ignore_sources, max_events_per_run
- Polling interval: poll_interval_sec (per watcher)
- Default ignore_sources includes inbox to avoid dispatch loops

OPS (PROPOSAL/DRAFT)
- standard: sdk_runtime/ops/launchd
- fallback/dev: sdk_runtime/ops/tmux
- overview: sdk_runtime/ops/README.md

OPERATION BASELINE (PROPOSAL/DRAFT)
- `config/agents.yaml` and `config/permissions.yaml` are aligned.
- `config/thresholds.yaml` has explicit poll intervals.
- Task_Inbox directories exist for all listed agents.
- launchd is the standard runtime method (tmux is fallback/dev).
 - Writes are permission-checked and denied writes are logged.

LOGGING (PROPOSAL/DRAFT)
- `sdk_runtime/logs/events.jsonl` and `sdk_runtime/logs/denied.log` rotate by size (10MB).

PERMISSIONS (PROPOSAL/DRAFT)
- Writes are blocked if the role is not permitted by `config/permissions.yaml`.
- Denied writes are appended to `sdk_runtime/logs/denied.log`.

TOOLS (PROPOSAL/DRAFT)
- Tools registry: `sdk_runtime/config/tools_registry.yaml`
- Shared tools: `sdk_runtime/tools/shared/`
- Trigger mapping:
  - `clock`: clock_diff, clock_digest, unresolved_index, unresolved_to_proposal
  - `taskfolder`: auto_proposal_processor, task_mover (dry-run)
  - `progress`: daily_check, weekly_summary_generator
- Tool outputs: `sdk_runtime/logs/tool_outputs/*.log`
- Tool runs: `sdk_runtime/logs/tool_runs.jsonl`
