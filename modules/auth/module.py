"""Registration and cookie authentication, separate from staff Admin accounts."""

import asyncio
import sqlite3
from pathlib import Path
from argon2.exceptions import VerifyMismatchError, VerificationError
from flaxon.modules import FlaxonModule
from flaxon.exceptions import Conflict, Unauthorized
from flaxon.http import JSONResponse
from security import (
    check_csrf,
    read_session,
    require_user,
    session_response,
    limit_auth_attempts,
)
from validation import json_object, text, credentials

auth = FlaxonModule(
    "auth", ui_dir=Path(__file__).parent / "ui", ui_routes={"Login.js": "/login"}
)


@auth.get("/session")
async def session(request):
    current = await read_session(request)
    if current:
        user = await require_user(request) if current["user_id"] else None
        return JSONResponse(
            {"data": {"user": user, "csrf": current["csrf"]}},
            headers={"cache-control": "no-store"},
        )
    return await session_response(request)


@auth.post("/register")
async def register(request):
    await check_csrf(request)
    data = await json_object(request)
    email, password = credentials(data)
    name = text(data, "name", 80)
    await limit_auth_attempts(request, email)
    password_hash = await asyncio.to_thread(request.app.hasher.hash, password)
    try:
        user_id = await request.app.course_db.execute(
            "INSERT INTO users(name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
    except sqlite3.IntegrityError:
        raise Conflict("Unable to create this account. Try signing in.")
    return await session_response(
        request, {"id": user_id, "name": name, "email": email}, status=201
    )


@auth.post("/login")
async def login(request):
    await check_csrf(request)
    email, password = credentials(await json_object(request))
    await limit_auth_attempts(request, email)
    user = await request.app.course_db.one(
        "SELECT * FROM users WHERE email = ?", (email,)
    )
    password_hash = user["password_hash"] if user else request.app.dummy_password_hash
    try:
        await asyncio.to_thread(request.app.hasher.verify, password_hash, password)
    except (VerifyMismatchError, VerificationError):
        raise Unauthorized("Email or password is incorrect.")
    if user is None:
        raise Unauthorized("Email or password is incorrect.")
    public_user = {key: user[key] for key in ("id", "name", "email")}
    return await session_response(request, public_user)


@auth.post("/logout")
async def logout(request):
    await check_csrf(request)
    return await session_response(request)
