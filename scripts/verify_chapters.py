"""Rebuild the ebook in a fresh CLI starter and verify every runnable checkpoint."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STEPS = json.loads((ROOT / "course/build-steps.json").read_text())


def run(project, *arguments):
    env = {
        **os.environ,
        "PYTHONPATH": str(project),
        "DATA_DIR": str(project / "data"),
        "FLAXON_DEBUG": "1",
        "PUBLIC_ORIGIN": "http://127.0.0.1:8000",
    }
    result = subprocess.run(
        [sys.executable, *arguments],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode:
        raise RuntimeError(
            f"{' '.join(arguments)} failed:\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def main():
    with tempfile.TemporaryDirectory(prefix="flaxon-book-") as directory:
        parent = Path(directory)
        run(parent, "-m", "flaxon", "new", "project_manager", "--no-venv")
        project = parent / "project_manager"
        run(project, "-m", "flaxon", "welcome")
        snapshot = ROOT / "course/starter"
        if snapshot.exists():
            shutil.rmtree(snapshot)
        shutil.copytree(
            project,
            snapshot,
            ignore=shutil.ignore_patterns("__pycache__", ".flaxon", "data"),
        )
        checkpoints = ROOT / "course/checkpoints"
        checkpoints.mkdir(exist_ok=True)
        for step in STEPS:
            chapter = step["chapter"]
            for entry in step["files"]:
                target = project / entry["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                if entry.get("edits"):
                    current = target.read_text()
                    for edit in entry["edits"]:
                        if current.count(edit["before"]) != 1:
                            raise ValueError(f"Chapter {chapter}: ambiguous edit in {entry['path']}")
                        current = current.replace(edit["before"], edit["after"], 1)
                    if current != entry["content"]:
                        raise ValueError(f"Chapter {chapter}: edit differs from recovery file")
                    target.write_text(current)
                else:
                    target.write_text(entry["content"])
            for path in step.get("delete", []):
                (project / path).unlink(missing_ok=True)
            if chapter == 3:
                run(project, "management.py", "makemigrations", "--name", "initial")
                run(project, "management.py", "migrate")
                run(project, "management.py", "migrate", "--status")
            run(project, "management.py", "check")
            # Import the actual runtime factory as well as the cheaper management factory.
            run(
                project,
                "-c",
                "from app import app; assert app.router.routes; print('Runtime factory ready')",
            )
            if chapter >= 7:
                run(project, "-m", "pytest", "-q", "tests/test_api.py")
            if chapter == 14:
                run(project, "-m", "pytest", "-q")
            # Persist a compact, exact file manifest for checkout/recovery without caches or data.
            files = {
                p.relative_to(project).as_posix(): p.read_text()
                for p in project.rglob("*")
                if p.is_file()
                and not any(
                    part in {".flaxon", "__pycache__", ".pytest_cache", "data", ".venv"}
                    for part in p.relative_to(project).parts
                )
            }
            (checkpoints / f"chapter-{chapter:02d}.json").write_text(
                json.dumps(files, indent=2) + "\n"
            )
            print(
                f"Chapter {chapter:02d}: runtime, management and available tests passed",
                flush=True,
            )
        run(project, "scripts/build_ui.py")
        print("All ebook checkpoints passed; starter and recovery snapshots saved.")


if __name__ == "__main__":
    main()
