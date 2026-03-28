from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from sdk_runtime.orchestrator.permissions import DEFAULT_ROLE, ensure_write
from sdk_runtime.runtime_paths import path_in_repo


def run() -> str:
    manager_dir = path_in_repo("Agent_workspace", "Agent_maneger")
    clock_dir = manager_dir / "クロック受付"
    out_path = manager_dir / "data" / "unresolved_index.md"

    index = _build_index(clock_dir)
    lines: List[str] = []
    lines.append("# 未整備インデックス")
    lines.append("")
    for filename, items in index:
        lines.append(f"## {filename}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    if ensure_write(out_path, DEFAULT_ROLE, "unresolved_index"):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")

    return f"Wrote: {out_path}"


def _build_index(clock_dir: Path) -> List[Tuple[str, List[str]]]:
    if not clock_dir.exists():
        return []
    files = list(clock_dir.glob("*.txt"))
    files.sort()
    index = []
    for path in files:
        items = _extract_unresolved(path.read_text(encoding="utf-8"))
        if items:
            index.append((path.name, items))
    return index


def _extract_unresolved(content: str) -> List[str]:
    lines = content.splitlines()
    items: List[str] = []
    in_section = False
    for line in lines:
        if line.strip().startswith("##"):
            header = line.strip().lstrip("#").strip()
            in_section = header == "未整備"
            continue
        if in_section and line.strip().startswith(("-", "・")):
            items.append(line.strip())
    return items
