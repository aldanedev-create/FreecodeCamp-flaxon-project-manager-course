# Companion book

Read [companion.md](companion.md) or [the PDF](../output/pdf/flaxon-project-manager-book.pdf).
The cover uses the existing Flaxon logo, copied from the framework assets.

The teaching text and automatic source excerpts live in `scripts/write_book.py`.
After changing course code or chapter explanations, regenerate Markdown and PDF:

```bash
python -m pip install -r book/requirements.txt
python scripts/write_book.py
python scripts/export_book.py
```

The exporter preserves exact source in Markdown and wraps long lines only in PDF
for print legibility. The PDF includes a linked contents page and bookmarks.
See `course/checkpoints.md` and `course/sample-lesson.md` for recording preparation.
