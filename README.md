# Python Full-Stack Course: Project Manager

Build a project manager with **Flaxon modules**, a **Teloce HTML SPA**, **signals**,
**staff Admin**, **CMS help articles**, and **MinifyJS production builds**.

This repository begins with the actual CLI command:

```bash
flaxon new project-manager --no-venv
```

The original generated starter is preserved in `chapter-01-setup`. Use
`starter-scoped-css` for the prepared course starter with pinned dependencies
and component-owned styles. `main`
contains the finished application. Read [the recording plan](docs/course-outline.md)
for the backend-first teaching sequence.

## Run the finished application

Use Python 3.12 (the verified environment), Git, and a terminal. Python 3.11 or
newer is supported by the source packages, but other interpreters have not been
verified for this course. Node.js is not needed for this application's build.

From this repository's root:

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
python scripts/verify_vendor.py
python -m pip install -r requirements-dev.txt
python management.py migrate
python -m flaxon run app:app --reload
```

Open http://127.0.0.1:8000/login and create your own account. Passwords must be
12–128 characters. Create a project, add tasks, and change their status.

Optional settings: copy `.env.example` to `.env`. Never commit `.env`.
`requirements.lock.txt` pins the resolved dependencies. Runtime-only installs
use `python -m pip install -r requirements.txt`.

## Sample data and staff access

After registering a user, stop the server and run:

```bash
python management.py seed
python management.py setup-admin
python -m flaxon run app:app --reload
```

The seed is idempotent and creates three sample tasks and one published help
article. Restart after seeding because CMS content is loaded into each process.
The Admin command prompts securely for a username and password; no default
staff password exists. Open `/admin/login`, then `/admin/` and `/admin/cms/`.
Public application accounts and staff Admin accounts are separate.

## Component-owned styles

Customer screens and child components use `<style scoped>` in their `.html`
files. The shell owns layout and inherited typography; each child owns its form
and controls. Only the shell's deliberate `:global(body)` margin reset escapes
scope. The SPA has no shared app.css stylesheet.

## Tests and production build

```bash
python -m pytest -q
python -m playwright install chromium
python scripts/browser_smoke.py
python scripts/browser_smoke.py --production
python scripts/build_ui.py
python -m pip check
```

The production browser smoke test uses loopback HTTP, which Chromium treats as
a trustworthy local context. It verifies the minified application and cookie
behavior locally; Render deployment must use HTTPS.

The code tests ownership, authentication, validation, session expiry, CSRF,
publishing permissions, persistence, and SQL parameterization. The browser
script uses disposable databases and verifies desktop/mobile SPA navigation,
registration, task progress, refresh, and logout.

## Framework versions and security fixes

The bundled `flaxon==0.2.6+course.1` wheel is an explicitly labelled course build,
**not an official PyPI release**. It includes CMS authorization fixes that are
not yet published upstream. The original patch and wheel checksums are in
`vendor/`; see [dependency provenance](vendor/README.md).

Teloce-Py is built from the exact source revision recorded there. MinifyJS is
pinned to `0.1.3`. Use the provided install commands rather than installing an
unpatched framework version over this environment.

## Instructor recording guide

- [Read the chapter-by-chapter recording guide](book/companion.md)
- [Download the instructor PDF](output/pdf/flaxon-project-manager-book.pdf)
- [Starter and chapter checkpoints](course/checkpoints.md)
- [Sample lesson recording script](course/sample-lesson.md)

## Read next

- [Backend architecture and API examples](docs/backend.md)
- [Admin/CMS security and role setup](docs/security.md)
- [Render deployment](docs/render.md)
- [Course outline and recording checkpoints](docs/course-outline.md)
- [Publishing this repository to GitHub](docs/github.md)

This is a tested teaching application for a single server process. The Render
configuration has not been deployed from this environment. Before inviting
real users, configure backups, monitoring, recovery, and the infrastructure
appropriate to your deployment.

Released under the [MIT License](LICENSE).
