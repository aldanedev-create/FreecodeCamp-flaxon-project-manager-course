"""Copy maintained learner chapters to a framework checkout before its website sync."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("framework", type=Path)
args = parser.parse_args()
target = args.framework / "docs/fullstack/project-manager"
target.mkdir(parents=True, exist_ok=True)
chapters = sorted((ROOT / "book/chapters").glob("*.md"))
for chapter in chapters:
    text = chapter.read_text()
    number = int(chapter.stem)
    previous = f"[Previous]({number - 1:02d}.md) | " if number > 1 else ""
    following = f" | [Next]({number + 1:02d}.md)" if number < len(chapters) else ""
    chapter_text = text + f"\n\n{previous}[Course contents](index.md){following}\n"
    (target / chapter.name).write_text(chapter_text)
links = "\n".join(f"- [{chapter.read_text().splitlines()[0][2:]}]({chapter.name})" for chapter in chapters)
(target / "index.md").write_text('''# Project Manager: complete full-stack ebook

Create your own project with `flaxon new project_manager`, then build the entire
application in order. Every lesson includes precise CREATE/EDIT/REPLACE instructions, code, recording notes, commands, verification,
common errors and an exercise. Use Python 3.12 and the pinned course dependencies.
The public recording target is Flaxon 3.0.0 after publication and a clean rehearsal.
Until then, the supplied preview wheels remain the verified installation path.
The book distinguishes release and preview requirements explicitly.

[Course repository and completed application](https://github.com/aldanedev-create/FreecodeCamp-flaxon-project-manager-course)

'''+links+'''

Use scoped CSS in Teloce `.html` components, automatic signal helper imports,
`data-teloce-link` navigation, explicit Flaxon modules, `settings.py`, `models.py`,
Python migrations and `management.py`. Backend-only guides remain in the main
documentation. These chapters are synchronized from the maintained course book.
''')
index = args.framework / "docs/index.md"
text = index.read_text()
for file in [target / "index.md", *[target / p.name for p in chapters]]:
    relative = file.relative_to(args.framework / "docs").as_posix()
    if f"({relative})" not in text:
        text += f"\n- [{file.read_text().splitlines()[0][2:]}]({relative})\n"
index.write_text(text)
print(f"Synced {len(chapters)} complete course chapters")
