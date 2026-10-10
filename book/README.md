# Instructor recording guide

Read [companion.md](companion.md) or [the PDF](../output/pdf/flaxon-project-manager-book.pdf).
The cover uses the existing Flaxon logo, copied from the framework assets.

The teaching text and complete chapter file blocks live in `scripts/write_book.py`.
The editable narration and live-coding plan is `course/recording-plan.json`.
Each chapter includes preparation, Say/Type/Show takes, demonstrations, editing
notes, commands, troubleshooting, and an exercise. All UI source uses component
scoped CSS.
After changing course code or chapter explanations, regenerate Markdown and PDF:

```bash
python -m pip install -r book/requirements.txt
python scripts/build_lesson_steps.py
python scripts/check_book_edits.py
python scripts/write_book.py
python scripts/export_book.py
```

The exporter preserves exact source in Markdown and wraps long lines only in PDF
for print legibility. The PDF includes a linked contents page and bookmarks.
See `course/checkpoints.md` and `course/sample-lesson.md` for recording preparation.

Revision 5 begins with `flaxon new project_manager`. `course/build-steps.json`
contains the ordered CREATE, complete replacement, and exact anchored block edits for chapters 2-15.
Chapter 1 bootstrap instructions are maintained in `course/lesson-01-setup.md`.

The chapter 2-15 file sequence was verified against a fresh generated starter:
application imports/HTML compilation, database migrations, API tests, all 43
backend/Admin/CMS tests, and the production UI build passed.

The planned PyPI target is Flaxon 3.0.0, installed with the standard/admin extras. The book separates the post-publication release path from the verified preview. Each edit is replayed against the preceding file and compared with its complete recovery snapshot.
