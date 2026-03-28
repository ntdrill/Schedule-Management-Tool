from __future__ import annotations

from pathlib import Path


def sdk_runtime_dir() -> Path:
    return Path(__file__).resolve().parent


def repo_root() -> Path:
    return sdk_runtime_dir().parent


def path_in_repo(*parts: str) -> Path:
    return repo_root().joinpath(*parts)
