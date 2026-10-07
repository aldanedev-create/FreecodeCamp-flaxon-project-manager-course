# Deploy the course to Render

This deployment keeps SQLite and the Admin/CMS store on one persistent disk.
Use a paid web service with a disk, one instance, and one Uvicorn worker.
The included `.python-version` selects the latest Python 3.12 patch on Render. The
free service's ephemeral filesystem is unsuitable for this data model.

## 1. Connect your repository

Push the complete repository, including the bundled course wheels, to GitHub.
In Render create a Blueprint from `render.yaml`, or create a Python web service
with the values below. Keep the service private to testing until setup finishes.

| Setting | Value |
|---|---|
| Build | `python scripts/verify_vendor.py && pip install -r requirements.txt && python scripts/build_ui.py` |
| Start | `python management.py migrate && python -m uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1` |
| Health check | `/health/course` |
| Disk mount | `/var/data` |
| Data directory | `DATA_DIR=/var/data` |
| Debug | `FLAXON_DEBUG=0` |
| Secret | A long randomly generated `FLAXON_SECRET_KEY` |
| Origin | `PUBLIC_ORIGIN=https://YOUR-SERVICE.onrender.com` |

Use HTTPS for the real service. A custom domain requires updating PUBLIC_ORIGIN;
production also derives its allowed Host from that origin. Configure the exact
service URL before checking health.

## 2. Why migrations run in the start command

Render disks are only accessible at runtime, not during build or pre-deploy.
Consequently SQLite migrations run before Uvicorn in the start command. They are
idempotent: already-applied migrations are not applied again. Adding a disk also
means deployments can briefly interrupt service.

`build_ui.py` uses a disposable data directory, so production asset compilation
never touches the live disk. Flaxon also builds the UI at startup; the course
keeps that default integration behavior.

## 3. Bootstrap the administrator

In the service's interactive Shell run:

```bash
python management.py setup-admin
```

Enter a unique staff username and a strong password. Do not put the password in
render.yaml or commit it. Open `/admin/login`, enroll MFA, and configure groups.
Create a normal application account through `/login`. To use sample data, stop
writing to the app, run `python management.py seed`, then restart the service.
Do not automatically seed production on every deploy.

## 4. Verify the deployment

Register and sign in; create a project and task; update its status; refresh a
nested route; sign out; verify protected APIs reject anonymous requests. Create
a published help article through CMS and confirm the public Help page shows it.
Check a read-only/editor account cannot mutate/publish restricted records.
Restart the service and confirm application and CMS data remain present.

Check cookies in browser developer tools: application and Admin cookies must be
HttpOnly and Secure over HTTPS. Confirm debug pages/error tracebacks are absent.

## 5. Backups and growth

Use SQLite's online backup API or a quiesced database copy; keep backup copies
outside the service disk and test restoration. Back up both `app.sqlite3` and
`admin.sqlite3`. Render disk snapshots alone are not the application's backup plan.

This configuration is for one process and one instance. More workers/instances
require shared database, sessions, coordination, CMS publication state, and
storage. Do not increase worker count with this course configuration.

Official references: [Render persistent disks](https://render.com/docs/disks),
[Python versions](https://render.com/docs/python-version), and
[Blueprint specification](https://render.com/docs/blueprint-spec).
This configuration is prepared and locally verified, but has not been deployed
or tested against your Render account.
