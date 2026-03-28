from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set
import json

from sdk_runtime.orchestrator.events import WatchEvent
from sdk_runtime.orchestrator.logging_utils import append_line
from sdk_runtime.orchestrator.permissions import DEFAULT_ROLE, ensure_write
from sdk_runtime.runtime_paths import sdk_runtime_dir
from sdk_runtime.tools.shared import (
    auto_proposal_processor,
    clock_digest,
    clock_diff,
    daily_check,
    task_mover,
    unresolved_index,
    unresolved_to_proposal,
    weekly_summary_generator,
)


TOOL_OUTPUT_DIR = sdk_runtime_dir() / "logs" / "tool_outputs"
TOOL_RUN_LOG = sdk_runtime_dir() / "logs" / "tool_runs.jsonl"


def run_tools_for_events(events: Iterable[WatchEvent]) -> List[Dict[str, Any]]:
    tool_ids = _collect_tool_ids(events)
    results: List[Dict[str, Any]] = []
    for tool_id in tool_ids:
        result = _run_tool(tool_id)
        results.append(result)
        _log_tool_run(result)
    return results


def _collect_tool_ids(events: Iterable[WatchEvent]) -> Set[str]:
    sources = {event.source for event in events}
    tool_ids: Set[str] = set()

    if _has_source(sources, "clock"):
        tool_ids.update(
            {
                "clock_diff",
                "clock_digest",
                "unresolved_index",
                "unresolved_to_proposal",
            }
        )

    if _has_source(sources, "taskfolder"):
        tool_ids.update({"auto_proposal_processor", "task_mover"})

    if _has_source(sources, "progress"):
        tool_ids.update({"daily_check", "weekly_summary_generator"})

    return tool_ids


def _has_source(sources: Set[str], key: str) -> bool:
    if key in sources:
        return True
    if key == "clock":
        return any(source.startswith("clock") for source in sources)
    if key == "progress":
        return any(source.startswith("progress") for source in sources)
    if key == "taskfolder":
        return any(source.startswith("taskfolder") for source in sources)
    return False


def _run_tool(tool_id: str) -> Dict[str, Any]:
    try:
        output = _invoke_tool(tool_id)
        _write_tool_output(tool_id, output)
        return {
            "tool": tool_id,
            "status": "ok",
            "timestamp": _now(),
        }
    except Exception as exc:
        _write_tool_output(tool_id, f"[ERROR] {exc}")
        return {
            "tool": tool_id,
            "status": "error",
            "error": str(exc),
            "timestamp": _now(),
        }


def _invoke_tool(tool_id: str) -> str:
    if tool_id == "clock_diff":
        return clock_diff.run(dry_run=False)
    if tool_id == "clock_digest":
        return clock_digest.run()
    if tool_id == "daily_check":
        return daily_check.run()
    if tool_id == "weekly_summary_generator":
        return weekly_summary_generator.run()
    if tool_id == "unresolved_index":
        return unresolved_index.run()
    if tool_id == "unresolved_to_proposal":
        return unresolved_to_proposal.run()
    if tool_id == "task_mover":
        return task_mover.run(apply=False)
    if tool_id == "auto_proposal_processor":
        return auto_proposal_processor.run()
    raise ValueError(f"Unknown tool: {tool_id}")


def _write_tool_output(tool_id: str, output: str) -> None:
    path = TOOL_OUTPUT_DIR / f"{tool_id}.log"
    if not ensure_write(path, DEFAULT_ROLE, "tool_output"):
        return
    append_line(path, output)


def _log_tool_run(result: Dict[str, Any]) -> None:
    if not ensure_write(TOOL_RUN_LOG, DEFAULT_ROLE, "tool_run_log"):
        return
    append_line(TOOL_RUN_LOG, json.dumps(result, ensure_ascii=True))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
