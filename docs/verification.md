# Verification record

Verified locally on 2026-10-07 with Python 3.12.14 on Linux.

- Fresh virtual environment installed the bundled Flaxon/Teloce wheels and pinned dependencies.
- Locked requirements reinstalled successfully; `pip check` found no broken requirements.
- Editable installation of the course project succeeded.
- `flaxon new project-manager --no-venv`, generated migrations, `welcome`, and `welcome-status` succeeded in a fresh directory.
- 43 course API, backoffice, and CMS-security tests passed.
- 33 targeted framework Admin/CMS tests passed in the framework patch checkout.
- Production MinifyJS compiled all 13 components successfully.
- Desktop (1440 px) and mobile (390 px) browser workflows passed.
- Production browser verification included staff login, CMS publishing, public article rendering, registration, project/task workflow, derived progress, filtering, SPA navigation, Back/Forward, deep refresh, and logout.

The production browser test uses a disposable SQLite database and loopback HTTP.
Live HTTPS, Render infrastructure, Windows installation, mail, media scanning,
and multi-process deployments were not verified. The upstream framework patch is included in `vendor/`; it has not been
published or merged into the framework repository.
