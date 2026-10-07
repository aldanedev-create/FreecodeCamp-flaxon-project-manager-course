# Chapter 04: authentication backend

A runnable checkpoint before project APIs, staff Admin/CMS, and SPA screens.
The shared schema already includes later domain tables, but only auth is mounted.

```bash
python -m venv .venv
# Activate the environment.
python -m pip install -r requirements-dev.txt
python management.py migrate
python -m pytest -q
python -m flaxon run app:app --reload
```

Start with GET /api/auth/session, then register/login with the CSRF header.
GET /api/me requires a signed-in user. Logout revokes the old cookie session.
Use main for the finished application. setup-admin is not used in this checkpoint.
