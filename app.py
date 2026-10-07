"""Compose the CLI starter's modules, staff backoffice, and Teloce SPA."""

import os
from pathlib import Path
from urllib.parse import urlsplit
from flaxon.middleware import BodyLimitMiddleware, TrustedHostsMiddleware
from argon2 import PasswordHasher
from flaxon import Flaxon, Request
from flaxon.http import JSONResponse
from flaxon.exceptions import BadRequest
from database import Database
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
    secret_key = os.getenv("FLAXON_SECRET_KEY", "")
    if not debug and len(secret_key) < 32:
        raise ValueError(
            "Set FLAXON_SECRET_KEY to at least 32 random characters in production."
        )
    app = Flaxon(
        "project-manager",
        debug=debug,
        openapi=True,
        config={"SECRET_KEY": secret_key or None},
    )
    app.add_middleware(BodyLimitMiddleware, max_size=256 * 1024)
    if not debug:
        app.add_middleware(
            TrustedHostsMiddleware, allowed_hosts=[urlsplit(PUBLIC_ORIGIN).hostname]
        )
    app.course_db = Database(database_path or DATABASE_PATH)
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
        await app.course_db.one("SELECT 1 FROM users LIMIT 1")
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
