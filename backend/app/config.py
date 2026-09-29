from __future__ import annotations

import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"


def load_local_environment() -> None:
    """Load local development settings without requiring another dependency."""
    environment_file = PROJECT_DIR / ".env"
    if not environment_file.exists():
        return
    for raw_line in environment_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_environment()
DATABASE_PATH = Path(os.getenv("WAYFARER_DB_PATH", DATA_DIR / "travel.db"))
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY", "")
FRONTEND_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5174",
    "http://127.0.0.1:5176",
    "http://localhost:5176",
]
