"""Build production Teloce assets without touching the live database or Render disk."""

import os
import secrets
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
with tempfile.TemporaryDirectory() as build_data:
    os.environ["DATA_DIR"] = build_data
    os.environ["FLAXON_DEBUG"] = "0"
    os.environ.setdefault("FLAXON_SECRET_KEY", secrets.token_urlsafe(48))
    from app import app

    result = app.teloce.build()
    print(f"Built {result.get('compiled', 0)} Teloce components with MinifyJS.")
