"""Chapter 04: authentication backend, before project APIs and SPA screens."""
import os
from urllib.parse import urlsplit
from argon2 import PasswordHasher
from flaxon import Flaxon
from flaxon.middleware import BodyLimitMiddleware, TrustedHostsMiddleware
from database import Database
from modules.auth.module import auth
from security import require_user
from settings import DATABASE_PATH, DEBUG, PUBLIC_ORIGIN


def create_app(database_path=None, admin_path=None, debug=None):
    debug = DEBUG if debug is None else debug
    secret = os.getenv("FLAXON_SECRET_KEY", "")
    if not debug and len(secret) < 32:
        raise ValueError("Set FLAXON_SECRET_KEY to at least 32 random characters.")
    app = Flaxon("project-manager-auth", debug=debug, openapi=True, config={"SECRET_KEY": secret or None})
    app.course_db = Database(database_path or DATABASE_PATH)
    app.public_origin = PUBLIC_ORIGIN
    app.hasher = PasswordHasher()
    app.dummy_password_hash = app.hasher.hash("dummy-password-for-timing-only")
    app.add_middleware(BodyLimitMiddleware, max_size=256 * 1024)
    if not debug:
        app.add_middleware(TrustedHostsMiddleware, allowed_hosts=[urlsplit(PUBLIC_ORIGIN).hostname])
    app.mount_module(auth, prefix="/api/auth")

    @app.get("/api/me")
    async def me(request):
        return {"data": await require_user(request)}

    @app.get("/")
    async def home():
        return {"data": {"chapter": "04-auth", "next": "Project APIs"}}

    return app


app = create_app()
