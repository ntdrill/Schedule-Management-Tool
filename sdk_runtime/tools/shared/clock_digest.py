from __future__ import annotations

from pathlib import Path
from typing import List

from sdk_runtime.runtime_paths import path_in_repo


def run(limit: int = 5) -> str:
    clock_dir = path_in_repo("Agent_workspace", "Agent_maneger", "クロック受付")
    summaries = _digest_clock_reports(clock_dir, limit)

    lines: List[str] = []
    lines.append("Clock Digest")
    lines.append("============")
    for summary in summaries:
        lines.append(f"\n- {summary['file']}")
        if summary["requests"]:
            lines.append("  [依頼事項]")
            for item in summary["requests"]:
                lines.append(f"  {item}")
        if summary["unresolved"]:
            lines.append("  [未整備]")
            for item in summary["unresolved"]:
                lines.append(f"  {item}")
    return "\n".join(lines)


def _digest_clock_reports(clock_dir: Path, limit: int) -> List[dict]:
    if not clock_dir.exists():
        return []
    files = list(clock_dir.glob("*.txt"))
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    files = files[:limit]
    summaries = []
    for path in files:
        content = path.read_text(encoding="utf-8")
        unresolved = _extract_section(content, ["未整備"])
        requests = _extract_section(content, ["依頼事項", "依頼", "Request for Action"])
        summaries.append(
            {
                "file": path.name,
                "unresolved": unresolved,
                "requests": requests,
            }
        )
    return summaries


def _extract_section(content: str, header_candidates: List[str]) -> List[str]:
    lines = content.splitlines()
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("##"):
            header = line.strip().lstrip("#").strip()
            if header in header_candidates:
                start_idx = idx + 1
                break
    if start_idx is None:
        return []
    items: List[str] = []
    for line in lines[start_idx:]:
        if line.strip().startswith("##"):
            break
        if line.strip().startswith(("-", "・")):
            items.append(line.strip())
    return items
