from __future__ import annotations

import argparse
import json
import time
from typing import Dict, Any, List, Optional, Tuple

from sdk_runtime.orchestrator.config import load_config, validate_config
from sdk_runtime.orchestrator.dispatch import dispatch_events, load_routes
from sdk_runtime.orchestrator.events import build_event, write_events, WatchEvent
from sdk_runtime.orchestrator.snapshot_store import load_snapshot, save_snapshot
from sdk_runtime.runtime_paths import sdk_runtime_dir
from sdk_runtime.watchers import (
    clock_watcher,
    inbox_watcher,
    progress_watcher,
    taskfolder_watcher,
)
from sdk_runtime.watchers.base import Diff, FileSystemWatcher

DEFAULT_POLL_INTERVAL_SEC = 60


def main() -> int:
    parser = argparse.ArgumentParser(description="sdk_runtime orchestrator (draft)")
    parser.add_argument(
        "--scan",
        action="store_true",
        help="scan watch targets once and print summary",
    )
    parser.add_argument(
        "--poll-once",
        action="store_true",
        help="poll watch targets once, record diffs, and write events",
    )
    parser.add_argument(
        "--dispatch",
        action="store_true",
        help="dispatch events to Task_Inbox based on agents.yaml",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="run continuous polling loop (draft)",
    )
    parser.add_argument(
        "--max-loops",
        type=int,
        default=None,
        help="maximum polling loops when --run is used",
    )
    parser.add_argument(
        "--max-seconds",
        type=int,
        default=None,
        help="maximum seconds to run when --run is used",
    )
    parser.add_argument(
        "--no-dispatch",
        action="store_true",
        help="disable dispatch during --run",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="run health check and exit",
    )
    args = parser.parse_args()

    config = load_config()
    print("config_loaded", _config_summary(config))
    warnings = validate_config(config)
    if warnings:
        print(json.dumps({"config_warnings": warnings}, ensure_ascii=True, indent=2))

    if args.health:
        from sdk_runtime.orchestrator.health import run_health_check

        print(json.dumps(run_health_check(), ensure_ascii=True, indent=2))
        return 0

    if args.run:
        run_loop(
            max_loops=args.max_loops,
            max_seconds=args.max_seconds,
            dispatch_enabled=not args.no_dispatch,
        )
        return 0

    if args.scan:
        results = {
            "taskfolder": taskfolder_watcher.scan_existing(),
            "progress": progress_watcher.scan_existing(),
            "clock": clock_watcher.scan_existing(),
            "inbox": inbox_watcher.scan_existing(),
        }
        print(json.dumps(results, ensure_ascii=True, indent=2))

    events: List[WatchEvent] = []
    if args.poll_once or args.dispatch:
        events = poll_once_all(config.thresholds)
        events_path = sdk_runtime_dir() / "logs" / "events.jsonl"
        write_events(events, events_path)
        print({"events_written": len(events), "path": str(events_path)})

    if args.dispatch and events:
        from sdk_runtime.orchestrator.tool_runner import run_tools_for_events

        tool_results = run_tools_for_events(events)
        print({"tools_executed": len(tool_results)})

    if args.dispatch:
        filtered_events = _apply_dispatch_filters(events, config.thresholds)
        routes = load_routes(config.agents, config.permissions.get("roles", {}))
        dispatched = dispatch_events(filtered_events, routes)
        print({"dispatched": dispatched, "routes": len(routes)})

    return 0


def _config_summary(config: Any) -> Dict[str, object]:
    return {
        "agents": len(config.agents.get("agents", [])),
        "roles": len(config.permissions.get("roles", {})),
        "shared_tools": len(config.tools_registry.get("shared_tools", [])),
    }


def poll_once_all(thresholds: Dict[str, Any]) -> List[WatchEvent]:
    watchers = _build_watchers()

    events: List[WatchEvent] = []
    for watcher in watchers:
        events.extend(_poll_watcher(watcher, thresholds))
    return events


def _poll_watcher(watcher: FileSystemWatcher, thresholds: Dict[str, Any]) -> List[WatchEvent]:
    previous = load_snapshot(watcher.name)
    if previous:
        watcher.set_snapshot(previous)

    new_snapshot, diff = watcher.poll_once()
    save_snapshot(watcher.name, new_snapshot)

    filtered = _apply_watcher_filters(diff, _watcher_thresholds(watcher.name, thresholds))
    if not filtered.added and not filtered.removed and not filtered.modified:
        return []

    return [
        build_event(
            source=watcher.name,
            added=filtered.added,
            removed=filtered.removed,
            modified=filtered.modified,
        )
    ]


def _watcher_thresholds(name: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    watchers_cfg = thresholds.get("watchers", {})
    if not isinstance(watchers_cfg, dict):
        return {}
    key = "inbox" if name.startswith("inbox:") else name
    cfg = watchers_cfg.get(key, {})
    return cfg if isinstance(cfg, dict) else {}


def _apply_watcher_filters(diff: Diff, cfg: Dict[str, Any]) -> Diff:
    include_paths = _as_list(cfg.get("include_paths", []))
    exclude_paths = _as_list(cfg.get("exclude_paths", []))
    min_changes = cfg.get("min_changes")

    added = _filter_paths(diff.added, include_paths, exclude_paths)
    removed = _filter_paths(diff.removed, include_paths, exclude_paths)
    modified = _filter_paths(diff.modified, include_paths, exclude_paths)

    total_changes = len(added) + len(removed) + len(modified)
    if isinstance(min_changes, int) and total_changes < min_changes:
        return Diff(added=[], removed=[], modified=[])

    return Diff(added=added, removed=removed, modified=modified)


def _apply_dispatch_filters(events: List[WatchEvent], thresholds: Dict[str, Any]) -> List[WatchEvent]:
    dispatch_cfg = thresholds.get("dispatch", {})
    if not isinstance(dispatch_cfg, dict):
        return events

    ignore_sources = _as_list(dispatch_cfg.get("ignore_sources", []))
    if ignore_sources:
        events = [event for event in events if not _source_matches_any(event.source, ignore_sources)]

    max_events = dispatch_cfg.get("max_events_per_run")
    if isinstance(max_events, int) and max_events >= 0:
        events = events[:max_events]

    return events


def _filter_paths(paths: List[str], includes: List[str], excludes: List[str]) -> List[str]:
    filtered = paths
    if includes:
        filtered = [path for path in filtered if _match_any(path, includes)]
    if excludes:
        filtered = [path for path in filtered if not _match_any(path, excludes)]
    return filtered


def _match_any(path: str, tokens: List[str]) -> bool:
    return any(token in path for token in tokens if token)


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        return [value] if value.strip() else []
    return []


def _build_watchers() -> List[FileSystemWatcher]:
    watchers = [
        taskfolder_watcher.build_watcher(),
        progress_watcher.build_watcher(),
        clock_watcher.build_watcher(),
    ]
    watchers.extend(inbox_watcher.build_watchers())
    return watchers


def _watcher_interval(name: str, thresholds: Dict[str, Any]) -> int:
    cfg = _watcher_thresholds(name, thresholds)
    interval = cfg.get("poll_interval_sec")
    if isinstance(interval, int) and interval >= 1:
        return interval
    return DEFAULT_POLL_INTERVAL_SEC


def _source_matches_any(source: str, patterns: List[str]) -> bool:
    return any(_source_matches(source, pattern) for pattern in patterns)


def _source_matches(source: str, pattern: str) -> bool:
    if pattern in ("*", "all"):
        return True
    if pattern == "inbox":
        return source.startswith("inbox:")
    if pattern.endswith("*"):
        return source.startswith(pattern[:-1])
    if pattern.endswith(":"):
        return source.startswith(pattern)
    return source == pattern


def run_loop(
    max_loops: Optional[int],
    max_seconds: Optional[int],
    dispatch_enabled: bool,
) -> None:
    start = time.monotonic()
    loop_count = 0
    last_run: Dict[str, float] = {}

    while True:
        now = time.monotonic()
        config = load_config()
        warnings = validate_config(config)
        if warnings:
            print(json.dumps({"config_warnings": warnings}, ensure_ascii=True))

        events: List[WatchEvent] = []
        watchers = _build_watchers()
        intervals: Dict[str, int] = {}
        for watcher in watchers:
            interval = _watcher_interval(watcher.name, config.thresholds)
            intervals[watcher.name] = interval
            last = last_run.get(watcher.name)
            if last is None or (now - last) >= interval:
                events.extend(_poll_watcher(watcher, config.thresholds))
                last_run[watcher.name] = now

        if events:
            events_path = sdk_runtime_dir() / "logs" / "events.jsonl"
            write_events(events, events_path)
            print({"events_written": len(events), "path": str(events_path)})

            from sdk_runtime.orchestrator.tool_runner import run_tools_for_events

            tool_results = run_tools_for_events(events)
            print({"tools_executed": len(tool_results)})

            if dispatch_enabled:
                filtered_events = _apply_dispatch_filters(events, config.thresholds)
                routes = load_routes(config.agents, config.permissions.get("roles", {}))
                dispatched = dispatch_events(filtered_events, routes)
                print({"dispatched": dispatched, "routes": len(routes)})

        loop_count += 1
        if isinstance(max_loops, int) and loop_count >= max_loops:
            break
        if isinstance(max_seconds, int) and (now - start) >= max_seconds:
            break

        sleep_for = _next_sleep(now, last_run, intervals)
        time.sleep(sleep_for)


def _next_sleep(now: float, last_run: Dict[str, float], intervals: Dict[str, int]) -> float:
    if not intervals:
        return 1.0
    remaining: List[float] = []
    for name, interval in intervals.items():
        last = last_run.get(name, now)
        remaining.append(max(0.0, interval - (now - last)))
    sleep_for = min(remaining) if remaining else 1.0
    return max(0.5, min(sleep_for, 60.0))


if __name__ == "__main__":
    raise SystemExit(main())
