# Chapter 01: scoped-CSS welcome starter

This is the generated Flaxon welcome project adapted for the course. All Teloce
styles live in style scoped blocks. The shell owns inherited typography, with a
single deliberate global body margin reset. Welcome owns links and buttons.
The optional Jinax example keeps its styles inside its server-rendered HTML.
There is no external app.css file.

```bash
python -m venv .venv
# Activate the environment for your operating system.
python scripts/verify_vendor.py
python -m pip install -r requirements-dev.txt
python management.py migrate
python -m flaxon welcome
python -m flaxon welcome-status
python -m flaxon run app:app --reload
```

Open http://127.0.0.1:8000/. The completed application and instructor PDF are on
main. The pinned course wheels are included; this starter is not a different
framework release. The original generated starter remains in chapter-01-setup
as a historical reference.
