"""Opaque cookie sessions and session-bound CSRF; account ownership stays on the server."""

import asyncio
import hashlib
import hmac
import secrets
import time
from models import User, Session, AuthAttempt
from tortoise.expressions import F
from flaxon.db import in_transaction
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
    return (
        await Session.filter(token_hash=digest(token), expires_at__gt=int(time.time()))
        .first()
        .values()
    )


async def require_user(request):
    session = await read_session(request)
    if not session or session["user_id"] is None:
        raise Unauthorized("Please sign in.")
    user = (
        await User.filter(id=session["user_id"]).first().values("id", "name", "email")
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
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    now = int(time.time())
    async with in_transaction():
        if old:
            await Session.filter(token_hash=digest(old)).delete()
        await Session.filter(expires_at__lte=now).delete()
        await Session.create(
            token_hash=digest(token),
            user_id=user["id"] if user else None,
            csrf=csrf,
            expires_at=now + SESSION_SECONDS,
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

    async with in_transaction():
        await AuthAttempt.filter(started_at__lt=now - 900).delete()
        await AuthAttempt.get_or_create(key=key, defaults={"started_at": now})
        await AuthAttempt.filter(key=key).update(attempts=F("attempts") + 1)
        record = await AuthAttempt.get(key=key)
        attempts = record.attempts
    if attempts > 10:
        raise TooManyRequests("Too many attempts. Try again in 15 minutes.")
