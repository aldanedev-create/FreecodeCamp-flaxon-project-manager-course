"""Build the learner ebook from the same complete files verified by chapter tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = json.loads((ROOT / "course/build-steps.json").read_text())

LESSONS = [
    ("Preview and CLI setup", "Generate your own project and run its welcome screen.",
     "You will build a project manager with customer accounts, private projects, tasks, progress, a staff Admin and published help. Flaxon runs Python on the server. Teloce compiles HTML components and TypeScript into a browser SPA. MinifyJS optimizes the production JavaScript. We build the APIs first so every screen connects to a working backend.",
     "The welcome page loads. Click its API button and see the Python response. The welcome command prints the project name.",
     "If flaxon is missing, activate the environment or use python -m flaxon. Environment creation does not install application dependencies; run the separate installation commands. Keep course_reference beside project_manager. Do not generate inside the completed repository.",
     "Find the welcome module's route and the HTML component that calls it."),
    ("Settings, management and application composition", "Replace the welcome shell with a small backend and keep one shared configuration.",
     "settings.py reads environment values and gives both the server and management commands the same database location. app.py creates an application from those settings and mounts modules explicitly. management.py delegates to Flaxon; you do not maintain a second command framework. The factory returns early in management mode so migration commands do not compile browser assets or open the staff store. For now, the only mounted feature is the generated welcome module. Later chapters add each module when its code is ready.",
     "The root returns a Backend lesson ready JSON message. /api/welcome/status returns its timestamp and framework version.",
     "Run commands inside project_manager. Do not place module mounts in settings.py. Keep the generated models.py until chapter 3; the ORM discovers it but does not create tables on startup.",
     "Change PROJECT_NAME in settings.py and inspect app.settings in a Python session."),
    ("Models and Python migrations", "Define all five application tables and apply the first Python migration.",
     "User owns projects; Project owns tasks. The ForeignKeyField names use the root ORM label models. Cascading a project deletion removes its tasks. Session stores a digest of an opaque cookie and an expiry; AuthAttempt persists login attempt counts. Define the schema once in models.py. makemigrations compares models with migration history and generates Python code; migrate applies that code. Commit the generated file. No JSON migration is needed. We define the complete schema now so later API chapters focus on behavior rather than repeated table changes.",
     "check reports valid settings and registrations. makemigrations creates migrations/0001_initial.py. migrate applies it; status lists it as applied. A second migrate performs no new schema changes.",
     "Use a fresh learner project. Do not apply the starter ProjectNote migration before replacing models.py. If you already migrated the starter, select a NEW DATA_DIR in .env and start the course migration history in a separate project. Do not delete or reset a database containing data you need. No such table means the selected database has not been migrated.",
     "Add a priority field to Task in a disposable copy. Generate and inspect a second migration without applying it to your course database."),
    ("Customer authentication and sessions", "Register, sign in, sign out and reject requests without valid sessions.",
     "validation.py checks JSON and field types before handlers write anything. security.py reads hashed session tokens, compares CSRF tokens, checks browser origins and rotates sessions after authentication changes. Password hashing runs in a worker thread because Argon2 is CPU intensive. The login handler verifies a dummy hash for unknown emails. The durable limiter counts attempts inside a transaction. Customer accounts are separate from staff Admin accounts. Start by requesting /api/auth/session; this issues an anonymous cookie and CSRF token. Registration and login replace both, so use the new values for the next request.",
     "GET /api/auth/session returns data.user = null and a CSRF token. POST /api/auth/register with the cookie and token creates a customer. GET /api/projects is introduced next; the auth module itself now supports login and logout.",
     "Use PUBLIC_ORIGIN exactly, including scheme, hostname and port. A 403 can mean a missing or rotated CSRF token, wrong Origin or non-JSON body. Passwords must have 12-128 characters. Never put the HttpOnly cookie in localStorage.",
     "Use curl or a small HTTP client to register, then log out and show that the previous cookie cannot authenticate."),
    ("Owned project APIs", "Create, list, read, update and delete projects belonging to the signed-in customer.",
     "owned_project combines the requested ID with the authenticated owner's ID in the ORM query. Every detail, edit and delete uses that guard. Creation takes owner_id from the session rather than accepting it from JSON. list_projects filters before returning rows. A nonexistent project and another person's project both return 404. The small HTTP demo establishes cookies and CSRF automatically, registers an account and exercises a working project endpoint.",
     "The HTTP demo creates a project and reads it back. Projects return a data envelope with the owner, name and description. A second customer's request cannot retrieve it.",
     "Do not repeat /api/projects inside decorators: app.py supplies that mount prefix. Use a trailing slash for the list/create endpoint. A 401 means no valid customer session; 404 after sign-in can be an ownership denial.",
     "Extend the demo to update a project's description and assert the read response changed."),
    ("Task workflow", "Add tasks, update status and due dates, filter tasks and delete them.",
     "Tasks belong to an owned project. list_tasks checks that project before querying its tasks. owned_task checks the parent project before permitting any mutation. A PATCH validates only supplied fields; allowed statuses are todo, doing and done. Date-only values use YYYY-MM-DD or null. The ORM handles values as parameters rather than SQL fragments. Deleting a project cascades through the database relationship.",
     "A signed-in customer can create a task, mark it done, filter by done and remove it. Invalid status and impossible date inputs return 400.",
     "Use /api/tasks/project/PROJECT_ID for task lists and creation. Use /api/tasks/TASK_ID for PATCH and DELETE. An empty PATCH and an unknown status are rejected.",
     "Create two customers and prove one cannot update the other's task."),
    ("Backend tests", "Run realistic HTTP requests against disposable ORM databases before writing the UI.",
     "conftest.py creates a test app and owns its event loop and ORM lifecycle. generate_schemas is used ONLY to prepare disposable test databases; production and development use migrations. TestClient exercises the ASGI app with HTTPX. Account carries its cookie and rotated CSRF token. Tests cover valid workflows, rejected input, expired sessions and cross-user access. Read an ownership test aloud: arrange two accounts, create a project, attempt another user's request and assert it is denied.",
     "tests/test_api.py passes. Each test uses temporary files and does not modify your learner database.",
     "Do not run later Admin tests yet. Keep the ORM context and event loop alive for the whole fixture. Sharing one account's cookie with another makes an ownership test invalid.",
     "Add a regression test that sends an extra owner_id in project JSON and proves it cannot choose a different owner."),
    ("Teloce HTML shell and scoped CSS", "Serve a browser shell and placeholder pages from the existing backend.",
     "app.use_teloce registers the compiler, runtime and browser routes. request.compile returns the compiled app.html shell for known page URLs. Each .html file has a template, script lang=ts and style scoped. The shell provides data-teloce-router-view. Module ui_routes maps compiled page names to browser paths. The first account/project pages are labelled placeholders; we replace them in the next two chapters. Shared types.ts describes JSON contracts and api.ts includes cookies, CSRF and error handling. Scoped CSS belongs to each component, so there is no separate app.css file.",
     "The shell and navigation appear at /. The account and project placeholder pages mount. /api/welcome/status still responds as JSON.",
     "A blank page can be a compiler/import error: inspect terminal and browser console. Delete public/app.css after replacing the factory; the completed app does not mount it. The shell's explicit global body reset is intentional; child components own their other rules.",
     "Change the shell's scoped header rules without modifying a child component's styles."),
    ("Login and project screens", "Replace placeholders with working account forms and a project list.",
     "Login uses the shared API helper to load the anonymous session, submit register/login, and replace cached session state after rotation. Loading guards disable duplicate submissions and error messages remain visible. ProjectList requests only authorized records from the API and creates a project from a form. Internal project anchors use data-teloce-link. The server owns authorization; TypeScript types and disabled buttons do not enforce permissions.",
     "Register in /login, open /projects and create a project. Sign out and sign back in. The new project survives the restart.",
     "Always inspect response.ok. A resolved fetch promise can still represent a 400/403/500. Relative imports are resolved from each HTML component. Registration must refresh the cached CSRF token.",
     "Show the validation message for an empty project name and make the same denied request directly to the API."),
    ("Task components, signals and progress", "Complete the task detail screen using reusable components and reactive progress.",
     "TaskForm emits a create event; TaskList emits status and remove events. ProjectDetails owns API calls and the task collection. signal stores that collection, computed derives completion, and an effect copies the value into displayed component data. Stop the effect before unmount. Teloce's .html compiler imports detected signal helpers automatically: do not add a redundant import. Ordinary TypeScript modules do not get the same automatic imports. Replacing the collection via its setter keeps progress and task display consistent. Empty projects return 0 percent.",
     "Create two tasks and complete one: progress becomes 50 percent. Filtering to done changes the visible rows while overall project progress remains 50 percent.",
     "Read a signal by calling it and replace it through set. An effect left alive after navigation can update an obsolete screen. Do not calculate project progress from only filtered rows.",
     "Complete both tasks and expect 100 percent, then delete one and verify progress stays correct."),
    ("SPA routing and direct refresh", "Support internal clicks, Back/Forward and direct nested URLs.",
     "There are two routers. Teloce's ui_routes maps /projects/:id to the detail component and passes id as a prop. data-teloce-link lets an ordinary anchor navigate without replacing the document; data-teloce-router-view provides the mount point. Flaxon's explicit /projects/<int:project_id> shell route handles direct visits and refreshes. The browser then fetches protected JSON. Keep Admin links as ordinary full-page navigation. Do not use a catch-all shell route that turns an unknown API path into HTML.",
     "Click into a project, use Back and Forward and refresh /projects/ID. The same screen loads. /api/does-not-exist remains a JSON 404.",
     "A successful click with a failed refresh means the server shell route is missing. A document reload on an internal link means its data-teloce-link marker is missing. Use /projects/:id in browser routes and <int:project_id> in Python routes.",
     "Put a temporary window marker in the browser console and prove an internal link preserves it."),
    ("Staff Admin", "Create staff credentials and manage existing domain records with explicit permissions.",
     "The custom ORM adapters deliberately expose only approved project/task fields and enforce the application's ownership creation rules. Staff create customer-owned records through the customer workflow; permitted staff may inspect and edit existing records. Root admin.py describes registration for management checks; backoffice.py configures the actual custom dashboard adapters. This is an example of business-specific adapters. Flaxon also supports direct ORM registration for ordinary CRUD. Staff records use a separate durable AdminStore. setup-admin creates the first privileged staff account interactively, with no default password. Grant view/change/delete capabilities separately for ordinary staff.",
     "Staff sign-in works at /admin/login. The model lists show the same projects and tasks used by the customer API. A public customer account cannot access staff tools.",
     "Role labels alone do not grant every capability. Use project.view_project and task.view_task for readers; add change permissions only when needed. These staff adapters are global operations tools, not a tenant-scoped customer portal.",
     "Create a read-only staff user and prove a direct edit request is denied as well as hiding its edit controls."),
    ("CMS help and sample data", "Publish sanitized help articles and show them through read-only public endpoints.",
     "CMS uses staff authentication. Help articles have title, summary, body and draft/published status. Public endpoints whitelist fields and expose only published items. Rich text is sanitized before the article component displays it with v-html; ordinary customer text remains escaped. seed is a project custom command exposed by flaxon_cli.py. It creates a sample project for the first registered customer and a published help article. Stop the server before seeding, then restart it so in-process CMS state reloads. Publishing permission remains distinct from drafting permission.",
     "Run seed after registering a customer. /help lists the sample published article and the article page survives a refresh. Drafts remain absent from public responses.",
     "Do not call authenticated CMS editing endpoints from public reader pages. Do not display arbitrary HTML using v-html. A draft editor also needs publishing permission to modify live content.",
     "Create a draft in staff CMS, confirm it is hidden publicly, then publish it with a permitted staff account."),
    ("Full-stack verification", "Exercise customer, staff and CMS workflows in a real browser.",
     "API tests cannot prove form listeners, history navigation or mobile layout. The browser script starts a disposable server, seeds a temporary staff account and tests desktop and 390-pixel workflows. It checks registration, login, projects, tasks, progress, help, navigation, refresh and logout. Run it in development and production mode to test MinifyJS output. Use labels, status messages and alerts; also rehearse with the keyboard.",
     "All application tests and both browser modes pass. Test data stays outside your learner database. No browser console errors occur in the verified workflow.",
     "Install Chromium before Playwright. Stop other servers using port 8123. Loopback production smoke verifies assets and behavior, not cloud infrastructure or TLS.",
     "Complete the workflow using only the keyboard and check one layout change at both desktop and mobile sizes."),
    ("Production build and Render", "Build optimized assets and deploy one persistent application instance.",
     "The Blueprint installs pinned dependencies and builds Teloce with MinifyJS. The start command applies committed Python migrations, then starts one Uvicorn worker. SQLite and staff/CMS data live under /var/data on a paid persistent disk. Render's build and pre-deploy processes cannot access that disk, which is why this design migrates at startup. Set PUBLIC_ORIGIN to your exact HTTPS service URL, DEBUG to false and a persistent generated secret. This course deliberately uses one instance: scaling needs a shared database, sessions, media and CMS coordination strategy.",
     "After deployment, /health/course returns ok. Create a project/task, publish an article, refresh a nested route, sign out and restart the service. Customer and staff data survive; cookies use Secure and HttpOnly.",
     "Free Render services cannot attach this persistent disk. Do not generate new migration files during deployment: commit them beforehand. An incorrect PUBLIC_ORIGIN causes CSRF failures. An ephemeral database loses records on restart. Production deployment must be verified in your account; local smoke is not proof of a live deployment.",
     "Back up both SQLite files safely, restore them into a test environment and verify a project plus one published help article."),
]

NOTES = {
 "modules/projects/module.py": "Create the projects module, then implement owned_project before the handlers that use it. The mount adds /api/projects once. Every ORM query for an existing project includes the signed-in customer's owner ID.",
 "modules/auth/module.py": "Create the auth module with session, registration, login and logout routes. Start with the anonymous CSRF handshake; registration rotates the cookie and token.",
 "modules/tasks/module.py": "Create the tasks module. Require ownership of the parent project before listing, creating, editing or deleting tasks. Validate status and due dates before saving.",
 "modules/content/module.py": "Create the public content API. Return only published CMS help articles. Staff draft and publishing operations remain in Admin.",
 "modules/projects/ui/pages/ProjectList.html": "Replace the placeholder with the complete projects screen. Connect its form to the typed API helper; show loading, error and empty states. Keep all CSS inside style scoped.",
 "modules/auth/ui/pages/Login.html": "Replace the placeholder with account forms. Use the session API and rotated CSRF token; do not read the HttpOnly cookie from JavaScript.",
 "modules/projects/ui/components/TaskForm.html": "Create the reusable task form. Collect title, status and due date, validate feedback and emit the saved task to its parent.",
 "modules/projects/ui/components/TaskList.html": "Create the reusable task list. Use stable task IDs for keyed rows and show the filtered workflow without changing database ownership.",
 "modules/projects/ui/pages/ProjectDetails/[id].html": "Replace the placeholder with the project detail page. Load the owned project and its tasks using the router ID, then compose the task form, list and progress display.",

 "settings.py": "Read this first: choose paths and environment values in one place. The rest of the app uses these values.",
 "management.py": "This short entry point delegates commands to Flaxon and fixes the project root.",
 "app.py": "The application factory mounts only the features already introduced. Follow the action label: a marked-block edit keeps the surrounding factory intact.",
 "models.py": "These five models are the complete schema. Relationships define ownership and deletion behavior; handlers add authorization.",
 "admin.py": "Keep explicit registration in this file. At chapter 3 it is empty; chapter 12 adds the domain models.",
 "security.py": "Read each helper in order: identify a session, require its user, check CSRF, rotate credentials, then limit attempts.",
 "validation.py": "Validate JSON before passing values to ORM calls. Reuse these checks in all mutations.",
 "backoffice.py": "These adapters query the same ORM models as the API and expose a deliberate staff field whitelist.",
 "ui/api.ts": "Centralize fetch, cookies, CSRF rotation and error messages here so pages share one contract.",
 "ui/types.ts": "Match the Python response fields exactly. These types document the browser contract; runtime validation stays on the server.",
 "ui/app.html": "This is the SPA shell. Its internal anchors and router view cooperate with each module's page mappings.",
 "tests/conftest.py": "Own the test database lifecycle and event loop. Never use development files in this fixture.",
 "seed.py": "Populate sample data explicitly after a customer exists; do not seed on every server start.",
 "render.yaml": "This is the complete single-instance deployment definition. Supply the service-specific HTTPS origin in Render.",
}

def fence(path, content):
    language = {".py": "python", ".ts": "typescript", ".html": "html", ".yaml": "yaml"}.get(Path(path).suffix, "text")
    return f"```{language}\n{content.rstrip()}\n```\n"

intro = '''# Build a Full-Stack Project Manager

Flaxon + Teloce HTML SPA + signals + scoped CSS + Admin/CMS + MinifyJS

Author: Aldane Hutchinson

Learner ebook and recording companion - revision 5 - October 2026

![Flaxon logo](assets/flaxon.png)

## Read this first

Start with `flaxon new project_manager`. Build in that generated directory; keep the separate course_reference checkout for pinned dependencies and recovery files. Use Python 3.12 and basic Python, HTML and JavaScript knowledge. You do not need Node.js for this course.

Follow chapters in order. Stop the development server before replacing Python files. Follow the action label on each step. CREATE supplies the complete new file. REPLACE THE ENTIRE FILE supplies a complete replacement. EDIT MARKED BLOCKS shows an exact existing block and its replacement: find the old block once and replace only that block, keeping everything else. Never append a duplicate function or route. Complete recovery files are available for every chapter. Create parent folders when they do not exist. Empty __init__.py blocks mean create an empty file. Commands run inside project_manager unless a chapter explicitly says otherwise. Once a check passes, commit your work before the next lesson.

The recording target is Flaxon 3.0.0. Its release installation commands become usable only after publication and a clean release rehearsal. Until then, the supplied preview wheels are the verified installation path; they are not labelled as a published 3.0.0 package. Keep the supplied requirements and vendor wheels together. Their checksums are verified before installation. This revision uses Python ORM migrations and management.py throughout. Older chapter tags describe the previous course revision and remain unchanged.

Each lesson gives a goal, an explanation, exact files, commands, expected results, common errors and a short exercise. For recording, demonstrate the expected result, explain the boundary being changed, type the important behavior and run its check. The final recording appendix is optional; you can learn the application directly from the chapters.

## Finished application

Customer pages: /login, /projects, /projects/ID, /help and /help/SLUG. Customers register, manage their own projects and tasks, filter status and see progress. Staff pages: /admin/login, /admin/project, /admin/task and /admin/cms/. Staff permission checks run on the server. Each Teloce component has scoped CSS. Internal SPA anchors use data-teloce-link; staff navigation remains ordinary page navigation.

## Contents

'''
chapters = []
for number, lesson in enumerate(LESSONS, 1):
    title, goal, explanation, result, errors, exercise = lesson
    parts = [f"# {number:02d} | {title}\n\n## Goal\n\n{goal}\n\n## What you are building\n\n{explanation}\n\n"]
    if number == 1:
        parts.append((ROOT / "course/lesson-01-setup.md").read_text())
    else:
        step = STEPS[number - 2]
        parts.append("## Build this chapter\n\nStop the server. Work in project_manager. Follow each CREATE, whole-file replacement, or marked-block edit below in order.\n\n")
        for i, entry in enumerate(step["files"], 1):
            path = entry["path"]
            note = NOTES.get(path, "This file owns the feature named by its module or component. Read the route/form flow before continuing.")
            parts.append(f"## Step {i}: {entry['action']} - {path}\n\n{note}\n\n")
            operations = entry.get("edits", [])
            if operations:
                for edit_number, operation in enumerate(operations, 1):
                    parts.append(f"### Edit {edit_number}: find this exact block\n\nOpen `{path}`. Locate this block once. The unchanged surrounding lines identify its position; do not use line numbers from another revision.\n\n" + fence(path, operation["before"]))
                    parts.append("### Replace that block with\n\n" + fence(path, operation["after"]) + "\nLeave the rest of the file unchanged.\n\n")
            else:
                parts.append(("Create the parent directories, then save this complete file.\n\n" if entry['action'].startswith('CREATE') else "Select all existing contents of this file and replace them with the complete code below.\n\n") + fence(path, entry["content"]) + "\n")
            parts.append(f"**Say:** \"{note}\"\n\n**Type:** Follow the action above in `{path}`; explain each new function or binding as you add it.\n\n**Viewers should see:** The saved file matches this step. After all steps, run the chapter checks below and show the expected result.\n\n")
        for path in step.get("delete", []):
            parts.append(f"## Remove {path}\n\nThe replacement factory and components no longer load this generated starter stylesheet. Remove the file after replacing the shell.\n\n")
        parts.append("## Run and check\n\n```bash\n" + step["commands"] + "\n```\n\n")
        if number == 4:
            parts.append('''## Make the first authenticated request

Keep the server running. In a second terminal use an HTTP client to GET /api/auth/session and save its Set-Cookie value and data.csrf. Then POST /api/auth/register with that cookie, Content-Type: application/json and X-CSRF-Token set to data.csrf. The complete Python demo in chapter 5 automates this exchange. For curl on macOS/Linux:

```bash
curl -c cookies.txt http://127.0.0.1:8000/api/auth/session
# Replace TOKEN with data.csrf from the response above:
curl -b cookies.txt -c cookies.txt -H 'Content-Type: application/json' -H 'X-CSRF-Token: TOKEN' -d '{"name":"Learner","email":"learner@example.test","password":"LearningPython123!"}' http://127.0.0.1:8000/api/auth/register
```

Save the NEW token returned by registration. Do not commit cookies.txt.

''')
        if number == 6:
            parts.append('''## Exercise the task API now

Use the cookie and current CSRF token from chapter 4; replace PROJECT_ID with the ID returned by chapter 5. Then read the task list and change TASK_ID to the returned task ID:

```bash
curl -b cookies.txt -H 'Content-Type: application/json' -H 'X-CSRF-Token: TOKEN' -d '{"title":"Record the lesson","status":"todo","due_date":"2026-12-01"}' http://127.0.0.1:8000/api/tasks/project/PROJECT_ID
curl -b cookies.txt http://127.0.0.1:8000/api/tasks/project/PROJECT_ID
curl -X PATCH -b cookies.txt -H 'Content-Type: application/json' -H 'X-CSRF-Token: TOKEN' -d '{"status":"done"}' http://127.0.0.1:8000/api/tasks/TASK_ID
curl -b cookies.txt 'http://127.0.0.1:8000/api/tasks/project/PROJECT_ID?status=done'
```

''')
        if number == 15:
            parts.append('''## Release-only edit: Render installation

If you chose the published Flaxon 3.0.0 path, use `requirements-release.txt` as your project's `requirements.txt`. In `render.yaml`, find:

```yaml
    buildCommand: python scripts/verify_vendor.py && pip install -r requirements.txt && python scripts/build_ui.py
```

Replace only that line with:

```yaml
    buildCommand: pip install -r requirements.txt && python scripts/build_ui.py
```

Leave the rest of the Blueprint unchanged. The preview path keeps wheel verification and includes `vendor/`. The release path installs the pinned published packages and does not need preview wheels. This release branch must pass the clean course rehearsal after publication before you record it.

## Deploy the completed project

1. Stop the local server. Run all tests and both browser checks from chapter 14. Run the production build above.
2. Commit your Python migrations, application files, vendor wheels and requirements. Keep .env, data, cookie jars and local virtual environments out of Git. Push the project to your GitHub repository.
3. In Render, choose New > Blueprint, connect your repository and select the branch containing render.yaml. Review the paid service and persistent disk before deploying.
4. Supply PUBLIC_ORIGIN as the exact https://SERVICE.onrender.com address (or your configured HTTPS domain). Keep FLAXON_DEBUG=0, DATA_DIR=/var/data and the generated persistent secret. Python is pinned by the Blueprint.
5. Deploy and inspect logs: migrations must complete before Uvicorn listens. Do not move SQLite migrations to a pre-deploy command; that process cannot access the attached disk.
6. In the service Shell run python management.py setup-admin and enter staff credentials interactively. Never commit a staff password.
7. Visit /health/course, then register a customer, create a project and task, sign into staff Admin and publish a help article. Refresh /projects/ID and /help/SLUG. Sign out and check protected API requests are rejected.
8. Restart the service and confirm both the project and help article survive. Inspect browser cookies over HTTPS for Secure and HttpOnly. Back up data and uploads before upgrades.

Official deployment references, checked October 2026: [Render Blueprints](https://render.com/docs/blueprint-spec), [persistent disks](https://render.com/docs/disks), [deployment lifecycle](https://render.com/docs/deploys), and [Python versions](https://render.com/docs/python-version). This book supplies deployable configuration; it does not claim a deployment has been made in your account.

''')
    if number == 3:
        parts.append((ROOT / "course/orm-api-reference.md").read_text() + "\n\n")
    parts.append(f"## Expected result\n\n{result}\n\n## Common errors\n\n{errors}\n\n## Short exercise\n\n{exercise}\n\n## What to say and show\n\nSay: \"{goal} The server remains responsible for persistence and authorization; the browser presents the result.\"\n\nShow the expected result above, then point to the file responsible for it. Run the chapter check before the next lesson.\n\n## Save your checkpoint\n\n```bash\ngit add .\ngit commit -m \"Complete chapter {number:02d}: {title}\"\n```\n")
    chapters.append("".join(parts))
    directory = ROOT / "book/chapters"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{number:02d}.md").write_text(chapters[-1])
intro += "\n".join(f"- {i:02d}: {item[0]}" for i, item in enumerate(LESSONS, 1)) + "\n\n"
appendix = '''# Appendix | Recording this application

Rehearse the complete build once before recording. Keep this ebook beside the editor. For each lesson: demonstrate the current result, introduce the file, explain one function or component at a time, type its behavior, run the check and show the working result. Provide full scoped CSS for copying, then explain a few relevant rules while recording.

Record a short sample using chapter 5's owned project endpoint, its HTTP demo, and chapter 9's ProjectList form. Tell viewers which earlier chapters supply sessions and validation. Gather feedback on pacing and error explanations before recording all chapters.

The repository contains the completed application, generated learner starter, chapter files and verification script. `course/checkpoints/chapter-NN.json` supplies the exact complete files for chapters 2-15. Run `python scripts/restore_chapter.py 5 ../chapter-05-recovery` from course_reference to recover chapter 5 into a new folder. Existing work is never overwritten. Use the revision-5 chapter snapshots rather than the earlier SQL-course tags. A snapshot is for recovery, not a replacement for teaching the file changes.
'''
(ROOT / "book/companion.md").write_text(intro + "\n\n".join(chapters) + "\n\n" + appendix)
print(f"Wrote {len(chapters)} complete learner chapters")
