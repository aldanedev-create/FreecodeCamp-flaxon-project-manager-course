import pytest


def test_registration_rotates_session_and_never_returns_password_hash(client, account):
    response = account.call("/api/auth/session")
    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "learner@example.test"
    assert "password" not in str(response.json())
    assert "httponly" in account.cookie_header.lower()
    assert "samesite=lax" in account.cookie_header.lower()

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

def test_logout_revokes_session(account):
    old_headers = account.headers
    assert account.call('/api/me').status_code == 200
    response = account.call('/api/auth/logout', 'post', {})
    assert response.status_code == 200
    account.accept_session(response)
    assert account.call('/api/me', headers=old_headers).status_code == 401
    assert account.call('/api/me').status_code == 401
