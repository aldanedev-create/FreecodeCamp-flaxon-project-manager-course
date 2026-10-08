"""Compose the CLI starter's modules, staff backoffice, and Teloce SPA."""

import settings
from types import SimpleNamespace
from pathlib import Path
from urllib.parse import urlsplit
from flaxon.middleware import BodyLimitMiddleware, TrustedHostsMiddleware
from argon2 import PasswordHasher
from flaxon import Flaxon, Request
from flaxon.http import JSONResponse
from backoffice import configure_backoffice
from modules.auth.module import auth
from modules.projects.module import projects
from modules.tasks.module import tasks
from modules.content.module import content
from modules.welcome.module import welcome
from settings import (
    ROOT,
    DATA_DIR,
    DATABASE_PATH,
    ADMIN_DATABASE_PATH,
    DEBUG,
    PUBLIC_ORIGIN,
)


def create_app(database_path=None, admin_path=None, debug=None):
    debug = DEBUG if debug is None else debug
    values = {key: getattr(settings, key) for key in dir(settings) if key.isupper()}
    values.update(DEBUG=debug)
    if database_path is not None:
        values["DATABASE_URL"] = f"sqlite://{Path(database_path).resolve()}"
    if admin_path is not None:
        values["ADMIN_STORAGE_PATH"] = Path(admin_path)
    app = Flaxon.from_settings(SimpleNamespace(__file__=settings.__file__, **values))
    app.add_middleware(BodyLimitMiddleware, max_size=256 * 1024)
    if not debug:
        app.add_middleware(
            TrustedHostsMiddleware, allowed_hosts=[urlsplit(PUBLIC_ORIGIN).hostname]
        )
    app.public_origin = PUBLIC_ORIGIN
    app.hasher = PasswordHasher()
    app.dummy_password_hash = app.hasher.hash("dummy-password-for-timing-only")
    for module, prefix in [
        (auth, "/api/auth"),
        (projects, "/api/projects"),
        (tasks, "/api/tasks"),
        (content, "/api/content"),
        (welcome, "/api/welcome"),
    ]:
        app.mount_module(module, prefix=prefix)
    if app.is_management:
        return app

    configure_backoffice(
        app,
        admin_path or ADMIN_DATABASE_PATH,
        Path(admin_path or ADMIN_DATABASE_PATH).parent / "uploads",
    )
    app.use_teloce(
        project_root=ROOT,
        ui_dir="ui",
        title="Project Manager",
        options={"minifier": "minifyjs"},
    )

    @app.get("/health/course")
    async def health():
        from models import User

        await User.all().limit(1)
        return {"data": {"status": "ok"}}

    # Explicit shell routes preserve real 404 responses for unknown API paths.
    @app.get("/")
    @app.get("/login")
    @app.get("/projects")
    @app.get("/projects/<int:project_id>")
    @app.get("/help")
    @app.get("/help/<slug>")
    async def spa(request: Request, project_id=None, slug=None):
        return await request.compile("app.html", {})

    return app


app = create_app()
