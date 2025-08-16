from __future__ import annotations
from pathlib import Path
import os
import yaml

# markers for identifying project root in a pip-based repo
_MARKERS = ("configs", "requirements.txt", "requirements-dev.txt", "setup.py", "setup.cfg", ".git")

def _project_root(start: Path | None = None) -> Path:
    """
    Walk up from this file until we find a directory that contains one of the markers.
    Falls back to repo root (parents[3]) for the src/common/utils layout.
    """
    # start from this file's directory if not provided
    here = (start or Path(__file__)).resolve()
    cur = here.parent
    # climb at most 6 levels to be safe
    for _ in range(6):
        if any((cur / m).exists() for m in _MARKERS):
            return cur
        cur = cur.parent
    # fallback for .../src/common/utils -> repo root
    return Path(__file__).resolve().parents[3]

def load_config(config_path: str | None = None) -> dict:
    """
    Resolve config path reliably irrespective of CWD.

    Priority:
    1) explicit arg
    2) CONFIG_PATH env
    3) <project_root>/configs/dev.yaml
    """
    env_path = os.getenv("CONFIG_PATH")

    if config_path is None:
        config_path = env_path or str(_project_root() / "configs" / "dev.yaml")

    path = Path(config_path)

    # If a relative path was provided, resolve it against project root
    if not path.is_absolute():
        path = _project_root() / path

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
