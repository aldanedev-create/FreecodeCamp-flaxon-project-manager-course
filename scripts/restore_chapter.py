"""Restore an ebook checkpoint into a new directory without overwriting learner work."""
import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("chapter", type=int, choices=range(1, 16))
parser.add_argument("directory", type=Path)
args = parser.parse_args()
if args.directory.exists():
    parser.error("Choose a new directory; existing work is never overwritten.")
if args.chapter == 1:
    shutil.copytree(ROOT / "course/starter", args.directory)
else:
    data = json.loads((ROOT / f"course/checkpoints/chapter-{args.chapter:02d}.json").read_text())
    args.directory.mkdir(parents=True)
    for name, content in data.items():
        target = args.directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
shutil.copytree(ROOT / "vendor", args.directory / "vendor")
for name in ("requirements.txt", "requirements-dev.txt", "requirements.lock.txt"):
    shutil.copy2(ROOT / name, args.directory / name)
(args.directory / "scripts").mkdir(exist_ok=True)
shutil.copy2(ROOT / "scripts/verify_vendor.py", args.directory / "scripts/verify_vendor.py")
print(f"Chapter {args.chapter:02d} restored to {args.directory}. Install dependencies and migrate.")
