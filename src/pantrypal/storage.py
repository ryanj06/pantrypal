"""Storage layer for pantry inventory.

Persists pantry contents as JSON in the user's home directory
(~/.pantrypal/pantry.json) unless overridden via PANTRYPAL_HOME.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict


def _data_dir() -> Path:
    base = os.environ.get("PANTRYPAL_HOME")
    if base:
        return Path(base)
    return Path.home() / ".pantrypal"


def _pantry_file() -> Path:
    return _data_dir() / "pantry.json"


def load_pantry() -> Dict[str, float]:
    """Load the pantry inventory as a dict of {ingredient: quantity}."""
    path = _pantry_file()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_pantry(pantry: Dict[str, float]) -> None:
    """Persist the pantry inventory to disk."""
    data_dir = _data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(_pantry_file(), "w") as f:
        json.dump(pantry, f, indent=2, sort_keys=True)


def normalize_name(name: str) -> str:
    """Normalize ingredient names for consistent matching (lowercase, stripped)."""
    return name.strip().lower()
