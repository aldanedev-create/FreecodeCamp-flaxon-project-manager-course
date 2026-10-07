# Backend first: architecture and API walkthrough

`app.py` composes modules. `database.py` owns short SQLite operations, executed
in worker threads so they do not block the ASGI loop. `security.py` owns opaque
sessions and CSRF; `validation.py` validates writes. SQL uses placeholders.

The domain database has users, projects, tasks, sessions, and auth attempts.
Users own projects; tasks belong to projects. Foreign keys cascade task deletion
when a project is deleted. Both web and Admin model adapters use the same domain
repository. Admin/CMS auxiliary records use a separate persistent SQLite store.

## Modules

| Module | API prefix | Teloce pages |
|---|---|---|
| auth | `/api/auth` | `/login` |
| projects | `/api/projects` | `/projects`, `/projects/:id` |
| tasks | `/api/tasks` | Tasks are components on a project page |
| content | `/api/content` | `/help`, `/help/:slug` |
| welcome | `/api/welcome` | Original CLI starter reference |

Success responses use `{"data": ...}`. Errors use Flaxon's `error.code` and
`error.message`. Public requests never call CMS editing endpoints. A missing
or other user's project returns 404; no ownership decisions happen in JavaScript.

## Exercise each endpoint before building the UI

Use curl (Windows PowerShell: use `curl.exe`). First create an anonymous session:

```bash
curl -c cookies.txt http://127.0.0.1:8000/api/auth/session
```

Copy `data.csrf` from that response. Replace `CSRF_TOKEN` below with its value:

```bash
curl -b cookies.txt -c cookies.txt -H "Content-Type: application/json" -H "X-CSRF-Token: CSRF_TOKEN" -d '{"name":"Learner","email":"learner@example.test","password":"LearningPython123!"}' http://127.0.0.1:8000/api/auth/register
```

Registration rotates both the session and CSRF token. Use the NEW `data.csrf`
for subsequent writes, with the updated cookie jar:

```bash
curl -b cookies.txt -H "Content-Type: application/json" -H "X-CSRF-Token: NEW_CSRF_TOKEN" -d '{"name":"My portfolio","description":"Build and deploy"}' http://127.0.0.1:8000/api/projects/
curl -b cookies.txt http://127.0.0.1:8000/api/projects/
```

Windows shell JSON quoting varies; the automated tests provide the same requests
in readable Python without shell quoting issues. Never commit cookie jars.

| Method | Endpoint | Behavior |
|---|---|---|
| GET | `/api/auth/session` | Return user and CSRF token; establish anonymous session when necessary |
| POST | `/api/auth/register` | Register and rotate session |
| POST | `/api/auth/login` | Verify password and rotate session |
| POST | `/api/auth/logout` | Revoke old session and create anonymous session |
| GET/POST | `/api/projects/` | List owned projects/create project |
| GET/PUT/DELETE | `/api/projects/{id}` | Read, edit, delete owned project |
| GET/POST | `/api/tasks/project/{id}` | List/create project tasks; optional `?status=done` |
| PATCH/DELETE | `/api/tasks/{id}` | Edit/delete an owned task |
| GET | `/api/content/articles` | Published help summaries only |
| GET | `/api/content/articles/{slug}` | Published sanitized article only |

## How Flaxon and Teloce work together

Flaxon mounts APIs and module-owned interface directories. `app.use_teloce()`
registers the build, shared runtime, assets, and router. The server returns the
compiled `ui/app.html` shell for explicit SPA routes. The browser router mounts
page components into `data-teloce-router-view`.

Links marked `data-teloce-link` navigate within the SPA. Staff Admin links are
ordinary links because Admin is a separate Jinax interface. Explicit Python
shell routes make direct navigation and refresh work without masking API 404s.

The shared `ui/api.ts` helper sends cookies and the session's CSRF header.
`ui/types.ts` records the JSON contracts. TypeScript transpilation removes types;
it is not a substitute for a separate type checker.

Component `data()` is already reactive. `ProjectDetails/[id].html` additionally
uses a task signal and computed completion percentage, then mirrors that value
into component state through an effect. It stops the effect on unmount.
Compiled `.html` components automatically receive imports for the signal helper
calls detected by Teloce; ordinary `.ts` helper files do not receive those imports.

The account form uses `v-show` so toggling registration preserves the form DOM
and its listeners. Loading/error messages have accessible status/alert roles.
