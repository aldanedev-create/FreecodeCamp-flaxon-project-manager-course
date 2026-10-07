"""Validate every write on the server, even when the browser already validated it."""

import re
from datetime import date
from flaxon.exceptions import BadRequest


async def json_object(request):
    try:
        data = await request.json()
    except (ValueError, UnicodeDecodeError):
        raise BadRequest("Send a valid JSON object.")
    if not isinstance(data, dict):
        raise BadRequest("Send a JSON object.")
    return data


def text(data, key, maximum=120, required=True):
    value = data.get(key, "")
    if not isinstance(value, str):
        raise BadRequest(f"{key} must be text.")
    value = value.strip()
    if (required and not value) or len(value) > maximum:
        raise BadRequest(
            f"{key} must contain 1 to {maximum} characters."
            if required
            else f"{key} must contain at most {maximum} characters."
        )
    return value


def credentials(data):
    email = text(data, "email", 254).lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise BadRequest("Enter a valid email address.")
    password = data.get("password")
    if not isinstance(password, str) or not 12 <= len(password) <= 128:
        raise BadRequest("Use a password with 12 to 128 characters.")
    return email, password


def task_fields(data, partial=False):
    result = {}
    if not partial or "title" in data:
        result["title"] = text(data, "title", 160)
    if not partial or "status" in data:
        status = data.get("status", "todo")
        if status not in ("todo", "doing", "done"):
            raise BadRequest("Status must be todo, doing, or done.")
        result["status"] = status
    if not partial or "due_date" in data:
        due = data.get("due_date") or None
        if due is not None:
            try:
                due = date.fromisoformat(due).isoformat()
            except (ValueError, TypeError):
                raise BadRequest("Use YYYY-MM-DD for a due date.")
        result["due_date"] = due
    if not result:
        raise BadRequest("Supply at least one editable field.")
    return result
