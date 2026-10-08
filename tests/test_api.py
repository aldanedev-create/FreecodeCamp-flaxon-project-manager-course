import asyncio
import time
import pytest
from conftest import Account, orm
from models import Task, Session


def project(account):
    response = account.call(
        "/api/projects/",
        "post",
        {"name": "Course project", "description": "Build the app"},
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_registration_rotates_session_and_never_returns_password_hash(client, account):
    response = account.call("/api/auth/session")
    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "learner@example.test"
    assert "password" not in str(response.json())
    assert "httponly" in account.cookie_header.lower()
    assert "samesite=lax" in account.cookie_header.lower()


def test_login_logout_and_old_session_revocation(account):
    old_headers = account.headers
    response = account.call("/api/auth/logout", "post", {})
    assert response.status_code == 200
    account.accept_session(response)
    assert account.call("/api/projects/", headers=old_headers).status_code == 401
    response = account.call(
        "/api/auth/login",
        "post",
        {"email": "learner@example.test", "password": "LearningPython123!"},
    )
    assert response.status_code == 200
    account.accept_session(response)
    assert account.call("/api/projects/").status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"name": "", "email": "bad", "password": "short"},
        {"name": "A", "email": "a@test.test", "password": "short"},
    ],
)
def test_invalid_registration(account, payload):
    assert account.call("/api/auth/register", "post", payload).status_code == 400


def test_wrong_password_and_duplicate_registration(account):
    assert (
        account.call(
            "/api/auth/login",
            "post",
            {"email": "learner@example.test", "password": "IncorrectPassword123!"},
        ).status_code
        == 401
    )
    assert (
        account.call(
            "/api/auth/register",
            "post",
            {
                "name": "Other",
                "email": "LEARNER@example.test",
                "password": "LearningPython123!",
            },
        ).status_code
        == 409
    )


def test_authentication_and_csrf_boundaries(client, account):
    assert client.get("/api/projects/").status_code == 401
    assert (
        account.call(
            "/api/projects/",
            "post",
            {"name": "Blocked"},
            headers={"cookie": account.cookie},
        ).status_code
        == 403
    )
    other = Account(client, "other@example.test")
    headers = {**account.headers, "x-csrf-token": other.csrf}
    assert (
        account.call(
            "/api/projects/", "post", {"name": "Blocked"}, headers=headers
        ).status_code
        == 403
    )
    headers = {**account.headers, "origin": "https://evil.example"}
    assert (
        account.call(
            "/api/projects/", "post", {"name": "Blocked"}, headers=headers
        ).status_code
        == 403
    )


def test_project_crud_and_ownership(client, account):
    item = project(account)
    other = Account(client, "other@example.test")
    path = f"/api/projects/{item['id']}"
    for method in ["get", "put", "delete"]:
        assert (
            other.call(
                path, method, {"name": "Stolen"} if method != "get" else None
            ).status_code
            == 404
        )
    assert other.call("/api/projects/").json()["data"] == []
    assert (
        account.call(path, "put", {"name": "Renamed", "description": "Updated"}).json()[
            "data"
        ]["name"]
        == "Renamed"
    )
    assert account.call(path, "delete", {}).status_code == 200
    assert account.call(path).status_code == 404


def test_task_workflow_filter_and_cascade(account, application):
    item = project(account)
    path = f"/api/tasks/project/{item['id']}"
    response = account.call(
        path, "post", {"title": "Record lesson", "due_date": "2026-12-01"}
    )
    assert response.status_code == 201
    task_id = response.json()["data"]["id"]
    assert (
        account.call(f"/api/tasks/{task_id}", "patch", {"status": "done"}).status_code
        == 200
    )
    assert len(account.call(path + "?status=done").json()["data"]) == 1
    assert account.call(path + "?status=todo").json()["data"] == []
    assert account.call(path + "?status=unknown").status_code == 400
    account.call(f"/api/projects/{item['id']}", "delete", {})
    assert orm(application, lambda: Task.filter(id=task_id).first()) is None


@pytest.mark.parametrize(
    "data",
    [
        {"title": ""},
        {"title": "Task", "status": "invalid"},
        {"title": "Task", "due_date": "2026-02-30"},
        {"title": 123},
    ],
)
def test_task_validation(account, data):
    item = project(account)
    assert (
        account.call(f"/api/tasks/project/{item['id']}", "post", data).status_code
        == 400
    )


def test_task_ownership_and_deletion(client, account):
    item = project(account)
    path = f"/api/tasks/project/{item['id']}"
    task = account.call(path, "post", {"title": "Private task"}).json()["data"]
    other = Account(client, "other@example.test")
    assert other.call(path).status_code == 404
    assert other.call(path, "post", {"title": "Wrong owner"}).status_code == 404
    assert (
        other.call(f"/api/tasks/{task['id']}", "patch", {"status": "done"}).status_code
        == 404
    )
    assert other.call(f"/api/tasks/{task['id']}", "delete", {}).status_code == 404
    assert account.call(f"/api/tasks/{task['id']}", "delete", {}).status_code == 200


def test_expired_session_is_rejected(account, application):
    orm(application, lambda: Session.all().update(expires_at=int(time.time()) - 1))
    assert account.call("/api/projects/").status_code == 401


def test_sql_values_are_not_executed(account):
    response = account.call(
        "/api/projects/", "post", {"name": "Robert'); DROP TABLE users;--"}
    )
    assert response.status_code == 201
    assert account.call("/api/auth/session").json()["data"]["user"] is not None


def test_auth_rate_limit(account):
    codes = [
        account.call(
            "/api/auth/login",
            "post",
            {"email": "learner@example.test", "password": "WrongPassword123!"},
        ).status_code
        for _ in range(11)
    ]
    assert 429 in codes


def test_unknown_api_is_404(client):
    assert client.get("/api/not-a-route").status_code == 404


def test_request_body_limit(client):
    response = client.post("/api/auth/register", json_data={"name": "x" * (300 * 1024)})
    assert response.status_code == 413


def test_production_requires_secret(monkeypatch, tmp_path):
    from app import create_app

    monkeypatch.delenv("FLAXON_SECRET_KEY", raising=False)
    with pytest.raises(ValueError, match="FLAXON_SECRET_KEY"):
        create_app(tmp_path / "app.sqlite3", tmp_path / "admin.sqlite3", debug=False)
