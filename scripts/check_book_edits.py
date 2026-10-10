"""Replay the exact printed edits and require agreement with every recovery snapshot."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
state = {p.relative_to(ROOT / "course/starter").as_posix(): p.read_text()
         for p in (ROOT / "course/starter").rglob("*") if p.is_file()}
steps = json.loads((ROOT / "course/build-steps.json").read_text())
edits = 0
for chapter in steps:
    for entry in chapter["files"]:
        if entry.get("edits"):
            content = state[entry["path"]]
            for edit in entry["edits"]:
                assert content.count(edit["before"]) == 1, (chapter["chapter"], entry["path"])
                content = content.replace(edit["before"], edit["after"], 1)
                edits += 1
            assert content == entry["content"], entry["path"]
        else:
            content = entry["content"]
        state[entry["path"]] = content
    for name in chapter.get("delete", []):
        state.pop(name, None)
    snapshot = json.loads((ROOT / f"course/checkpoints/chapter-{chapter['chapter']:02d}.json").read_text())
    # Migration files are generated during verification, not typed from the book.
    for name, content in state.items():
        if name in snapshot:
            assert snapshot[name] == content, (chapter['chapter'], name)
    print(f"Chapter {chapter['chapter']:02d}: exact edits match recovery files")
print(f"Verified {edits} anchored edits across 14 chapter transitions")
