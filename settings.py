"""Settings shared by the web app and management commands."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_NAME = 'project-manager'
DATA_DIR = ROOT / "data"
DATABASE_PATH = DATA_DIR / "app.sqlite3"
DEBUG = os.getenv("FLAXON_DEBUG", "1") == "1"
