# Record the backend-first course

Audience: learners with basic Python, HTML, CSS, and JavaScript. Introduce the
TypeScript used in the project. Teach working slices and explain why each check
exists. The estimated edited duration is five to six hours; adjust after the pilot.

| Chapter | Teach | Demonstrate |
|---|---|---|
| 1 | Preview, virtual environment, pinned course packages, `flaxon new project-manager` | Generated welcome page and module commands |
| 2 | Application factory, configuration, modules | Separate API prefixes and module-owned UI |
| 3 | Database relationships and migrations | Durable users/projects/tasks; migration status |
| 4 | Registration, hashing, cookie sessions, CSRF, login/logout | curl requests and session rotation |
| 5 | Project CRUD and ownership | Two users; denied cross-user reads/writes |
| 6 | Tasks, due dates, status filters | Valid and invalid API requests |
| 7 | Backend tests | Run API assertions before writing frontend |
| 8 | `.html` components, `lang="ts"`, templates and styles | SPA shell and login screen |
| 9 | Typed API helper and auth UI | Registration, sign-in, loading/errors, logout |
| 10 | Reusable task components, signals and derived progress | Progress updates and filtered tasks |
| 11 | `data-teloce-link`, history and direct URLs | Back/Forward, deep-link refresh, route params |
| 12 | Staff Admin, model adapters and capabilities | Staff access without customer privileges |
| 13 | CMS schemas, drafts, publishing and revision rights | Published help articles in the Teloce SPA |
| 14 | API/browser regression tests | Session expiry, permissions, mobile layouts |
| 15 | MinifyJS, environment secrets and Render | Production build and persistence after restart |

## Reproduce the first CLI lesson

Prepare a fresh parent folder outside this completed repository. Install the
same bundled dependencies in a virtual environment. Then run:

```bash
flaxon new project-manager --no-venv
cd project-manager
python management.py migrate
flaxon welcome
flaxon welcome-status
flaxon run app:app --reload
```

You can install the bundled wheel from its absolute path while in the parent
folder. The generated pyproject contains broad starter dependencies; in the
course, replace them with the pinned course dependency files before recording
later chapters. Do not accidentally generate into an existing project directory.

The generated welcome project is a starting exercise, not the finished course.
The source comparison is preserved in `chapter-01-setup`; `backend-ready` records
the domain APIs and tests; `course-v1` records the completed application.
These are three actual checkpoints, not a claim that all fifteen chapter tags
have been authored. Add finer checkpoints as the recording script is rehearsed.

## Recording approach

Type routes, authorization, validation, signals, components, and tests while
explaining them. Provide decorative CSS and assets as starter files. After each
feature, show a successful request and one relevant failure. Avoid silently
pasting large files or making viewers watch installation waits.

Record a 10–15-minute pilot: show the finished feature, one project route, an
ownership test, and its Teloce screen. Use your own voice, readable code, clear
audio, and 1080p capture. Rehearse clean installation before recording. The PDF
companion is a later deliverable; the Markdown guides here are its source outline.
