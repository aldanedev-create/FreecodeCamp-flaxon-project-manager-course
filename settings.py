"""Environment settings; both the application and management commands use these."""

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
PROJECT_NAME = "Project Manager"
DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT / "data")))
DATABASE_PATH = DATA_DIR / "app.sqlite3"
ADMIN_DATABASE_PATH = DATA_DIR / "admin.sqlite3"
DEBUG = os.getenv("FLAXON_DEBUG", "1") == "1"
PUBLIC_ORIGIN = os.getenv("PUBLIC_ORIGIN", "http://127.0.0.1:8000").rstrip("/")
