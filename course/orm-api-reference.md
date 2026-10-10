## Flaxon API and ORM: the commands you will teach

This course uses the current Flaxon public integration rather than JSON migrations or hand-written SQL. Flaxon's `Model` and `fields` come from Tortoise; queries are asynchronous. The Flaxon 3.0.0 release target must export the same APIs before recording the release installation path.

**Say:** "Models describe tables. Settings choose the database. Flaxon opens and closes connections. Migrations record schema changes, and management.py applies them explicitly."

In `models.py`, the exact imports are:

```python
from flaxon.db import Model, fields
```

You have already created `Project` in this chapter. After migrating, use these queries in an async handler or the management shell. These examples explain the API; do not paste them at module scope, and do not add an unsecured demonstration route:

```python
project = await Project.create(
    owner_id=user["id"], name="Record the course", description="First project"
)
projects = await Project.filter(owner_id=user["id"]).order_by("-created_at")
project = await Project.filter(id=project_id, owner_id=user["id"]).first()
await Project.filter(id=project_id, owner_id=user["id"]).update(name="New name")
await Project.filter(id=project_id, owner_id=user["id"]).delete()
```

`user` is the authenticated customer dictionary and `project_id` is the validated route parameter introduced in chapters 4-5. Never trust an owner ID supplied by the browser. A model relationship does not perform authorization automatically.

For an operation that must commit or roll back together:

```python
from flaxon.db import in_transaction

async with in_transaction() as connection:
    project = await Project.create(
        owner_id=user["id"], name="Atomic project", using_db=connection
    )
    await Task.create(
        project_id=project.id, title="First task", using_db=connection
    )
```

The server manages normal connection startup and shutdown through `Flaxon.from_settings(...)`. The course tests create disposable schemas explicitly; normal application startup never silently changes tables.

Keep these responsibilities separate:

- `settings.py`: `DATABASE_URL`, debug mode, secrets and deployment configuration.
- `models.py`: fields, foreign keys, indexes and readable model names.
- `app.py`: `Flaxon.from_settings(...)`, middleware and `app.mount_module(...)`.
- `management.py`: one short entry point backed by `flaxon.management.execute`.
- `admin.py`: explicit staff model registration; chapter 12 adds controlled adapters.

Run these from `project_manager`:

```bash
python management.py check
python management.py makemigrations --name initial
python management.py migrate --plan
python management.py migrate
python management.py migrate --status
python management.py shell
python management.py setup-admin
python management.py runserver
```

Only run `makemigrations --name initial` once for this initial schema. Later changes use a descriptive new name. `createsuperuser` is an alias for `setup-admin`; migration files are Python and belong in Git. Stop the server before changing configuration. Staff credentials and customer accounts are separate.

The later chapters show actual `FlaxonModule` definitions, JSON responses, request parsing, middleware, Teloce compilation and Admin/CMS integration in their complete files. Optional SSR is outside this course's client-rendered SPA; use the dedicated framework guide when adding it.
