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

## Scoped CSS and instructor-guide revision

- The SPA no longer loads a shared app.css stylesheet; nine screen/shell/child
  components own their scoped styles, alongside the existing welcome component.
- Production browser checks verify Login/TaskForm styling, scoped rule isolation,
  absence of an app.css resource, and desktop/mobile workflows.
- The adapted welcome starter was checked at desktop and mobile widths, including
  its Python API button, scoped styles, and absence of horizontal overflow.
- The PDF is an instructor recording guide; no tutorial video was recorded here.
