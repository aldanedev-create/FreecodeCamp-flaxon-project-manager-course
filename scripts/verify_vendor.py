"""Verify that bundled wheels match the course's recorded checksums."""

import hashlib
import json
from pathlib import Path

vendor = Path(__file__).resolve().parents[1] / "vendor"
for filename, expected in json.loads((vendor / "checksums.json").read_text()).items():
    actual = hashlib.sha256((vendor / filename).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"Checksum mismatch: {filename}")
    print(f"OK {filename}")
