"""Opaque cookie sessions and session-bound CSRF; account ownership stays on the server."""

import asyncio
import hashlib
import hmac
import secrets
import time
from flaxon.exceptions import Forbidden, Unauthorized, TooManyRequests
from flaxon.http import JSONResponse
from flaxon.http.cookies import Cookie

COOKIE_NAME = "project_session"
SESSION_SECONDS = 8 * 60 * 60


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


async def read_session(request):
    token = request.cookies.get(COOKIE_NAME, "")
    if not token:
        return None
    return await request.app.course_db.one(
        "SELECT * FROM sessions WHERE token_hash = ? AND expires_at > ?",
        (digest(token), int(time.time())),
    )


async def require_user(request):
    session = await read_session(request)
    if not session or session["user_id"] is None:
        raise Unauthorized("Please sign in.")
    user = await request.app.course_db.one(
        "SELECT id, name, email FROM users WHERE id = ?", (session["user_id"],)
    )
    if user is None:
        raise Unauthorized("Please sign in.")
    return user


async def check_csrf(request):
    origin = request.headers.get("origin")
    if origin and origin != request.app.public_origin:
        raise Forbidden("This request came from an untrusted origin.")
    if "application/json" not in request.headers.get("content-type", "").lower():
        raise Forbidden("Send JSON with a CSRF token.")
    session = await read_session(request)
    supplied = request.headers.get("x-csrf-token", "")
    if (
        not session
        or not supplied
        or not hmac.compare_digest(session["csrf"], supplied)
    ):
        raise Forbidden("Your session expired. Reload the page and try again.")


async def session_response(request, user=None, status=200):
    old = request.cookies.get(COOKIE_NAME, "")
    if old:
        await request.app.course_db.execute(
            "DELETE FROM sessions WHERE token_hash = ?", (digest(old),)
        )
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    await request.app.course_db.execute(
        "DELETE FROM sessions WHERE expires_at <= ?", (int(time.time()),)
    )
    await request.app.course_db.execute(
        "INSERT INTO sessions(token_hash, user_id, csrf, expires_at) VALUES (?, ?, ?, ?)",
        (
            digest(token),
            user["id"] if user else None,
            csrf,
            int(time.time()) + SESSION_SECONDS,
        ),
    )
    cookie = Cookie(
        COOKIE_NAME,
        token,
        path="/",
        httponly=True,
        samesite="Lax",
        secure=not request.app.debug,
        max_age=SESSION_SECONDS,
    )
    response = JSONResponse(
        {"data": {"user": user, "csrf": csrf}},
        status_code=status,
        headers={"cache-control": "no-store"},
    )
    response.headers.add("set-cookie", cookie.to_header())
    return response


async def limit_auth_attempts(request, email):
    """A durable, single-instance limiter; production proxies also limit the auth routes."""
    peer = request.scope.get("client") or ("unknown", 0)
    key = digest(str(peer[0]) + ":" + email)
    now = int(time.time())

    def count():
        with request.app.course_db.connection() as connection:
            connection.execute(
                "DELETE FROM auth_attempts WHERE started_at < ?", (now - 900,)
            )
            connection.execute(
                "INSERT INTO auth_attempts(key, attempts, started_at) VALUES (?, 1, ?) ON CONFLICT(key) DO UPDATE SET attempts = attempts + 1",
                (key, now),
            )
            return connection.execute(
                "SELECT attempts FROM auth_attempts WHERE key = ?", (key,)
            ).fetchone()[0]

    if await asyncio.to_thread(count) > 10:
        raise TooManyRequests("Too many attempts. Try again in 15 minutes.")
