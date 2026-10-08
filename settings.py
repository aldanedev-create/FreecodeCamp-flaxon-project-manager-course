"""Shared configuration for the server and management commands."""

from pathlib import Path
from urllib.parse import urlsplit
from flaxon.config import env

BASE_DIR = Path(__file__).resolve().parent
ROOT = BASE_DIR
env.load(BASE_DIR / ".env")
PROJECT_NAME = "Project Manager"
DATA_DIR = Path(env.str("DATA_DIR", str(BASE_DIR / "data"))).resolve()
DATABASE_PATH = DATA_DIR / "app.sqlite3"
ADMIN_DATABASE_PATH = DATA_DIR / "admin.sqlite3"
DATABASE_URL = env.str("DATABASE_URL", f"sqlite://{DATABASE_PATH}")
DEBUG = env.bool("FLAXON_DEBUG", default=True)
SECRET_KEY = env.str("FLAXON_SECRET_KEY")
PUBLIC_ORIGIN = env.str("PUBLIC_ORIGIN", "http://127.0.0.1:8000").rstrip("/")
ALLOWED_HOSTS = env.list(
    "FLAXON_ALLOWED_HOSTS", default=[urlsplit(PUBLIC_ORIGIN).hostname, "testserver"]
)
CSRF_TRUSTED_ORIGINS = [PUBLIC_ORIGIN]
TIME_ZONE = "UTC"
ADMIN_ENABLED = True
CMS_ENABLED = True
ADMIN_SERVICES_ENABLED = False
ADMIN_STORE_BACKEND = "sqlite"
ADMIN_STORAGE_PATH = ADMIN_DATABASE_PATH
