import asyncio
import json
import sqlite3
import pytest
from app import create_app
import httpx


class TestClient:
    def __init__(self, app):
        self.app = app

    def __getattr__(self, method):
        def request(path, json_data=None, **kwargs):
            async def send():
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=self.app),
                    base_url="http://testserver",
                ) as client:
                    return await client.request(
                        method.upper(), path, json=json_data, **kwargs
                    )

            return asyncio.run(send())

        return request


from settings import ROOT


@pytest.fixture
def application(tmp_path):
    path = tmp_path / "app.sqlite3"
    migration = json.loads((ROOT / "migrations/0001_initial.json").read_text())
    with sqlite3.connect(path) as connection:
        connection.executescript(migration["up"])
    return create_app(path, tmp_path / "admin.sqlite3", debug=True)


@pytest.fixture
def client(application):
    return TestClient(application)


class Account:
    def __init__(self, client, email="learner@example.test"):
        self.client = client
        response = client.get("/api/auth/session")
        self.accept_session(response)
        response = self.call(
            "/api/auth/register",
            "post",
            {"name": "Learner", "email": email, "password": "LearningPython123!"},
        )
        assert response.status_code == 201, response.content
        self.accept_session(response)

    def accept_session(self, response):
        self.cookie_header = next(
            value
            for value in response.headers.get_list("set-cookie")
            if value.startswith("project_session=")
        )
        self.cookie = self.cookie_header.split(";")[0]
        self.csrf = response.json()["data"]["csrf"]

    @property
    def headers(self):
        return {
            "cookie": self.cookie,
            "x-csrf-token": self.csrf,
            "content-type": "application/json",
        }

    def call(self, path, method="get", data=None, headers=None):
        options = {"headers": self.headers if headers is None else headers}
        if data is not None:
            options["json_data"] = data
        return getattr(self.client, method)(path, **options)


@pytest.fixture
def account(client):
    return Account(client)
