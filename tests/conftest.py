import asyncio
import pytest
from app import create_app
import httpx


class TestClient:
    def __init__(self, app):
        self.app = app
        self.loop = getattr(app, "test_loop", None)

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

            return (
                self.loop.run_until_complete(send())
                if self.loop
                else asyncio.run(send())
            )

        return request


from settings import ROOT


@pytest.fixture
def application(tmp_path):
    path = tmp_path / "app.sqlite3"
    app = create_app(path, tmp_path / "admin.sqlite3", debug=True)
    loop = asyncio.new_event_loop()
    app.test_loop = loop
    loop.run_until_complete(app.db.initialize())
    with app.db.bind():
        loop.run_until_complete(app.db.context.generate_schemas())
    yield app
    loop.run_until_complete(app.db.close())
    loop.close()


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


def orm(application, query):
    """Run a direct ORM assertion in the same database context as this test app."""
    with application.db.bind():
        return application.test_loop.run_until_complete(query())
