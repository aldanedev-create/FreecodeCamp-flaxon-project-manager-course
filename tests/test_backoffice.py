import asyncio
from flaxon import Flaxon
from flaxon.admin.cms import CMS, CMSField, ContentType
from flaxon.testing import TestClient


def staff(application, permissions):
    admin = application.backoffice
    admin.auth.add_user(
        {
            "username": "editor",
            "password": "EditorLearning123!",
            "roles": [],
            "permissions": permissions,
        }
    )
    token = asyncio.run(admin.auth.login("editor", "EditorLearning123!"))
    return {"cookie": f"session_id={token}", "x-csrf-token": admin.csrf_token()}


def test_public_content_hides_drafts_and_private_fields(application, client):
    articles = application.cms.content_types["help_article"]
    articles.create({"title": "Hidden draft", "status": "draft"})
    item = articles.create(
        {
            "title": "Published guide",
            "body": "<p>Safe</p><script>bad()</script>",
            "status": "published",
        }
    )
    response = client.get("/api/content/articles")
    assert [row["title"] for row in response.json()["data"]] == ["Published guide"]
    detail = client.get("/api/content/articles/" + item["slug"]).json()["data"]
    assert "<script>" not in detail["body"]
    assert "created_at" not in detail
    assert client.get("/api/content/articles/hidden-draft").status_code == 404


def test_application_accounts_do_not_have_staff_access(client, account):
    assert account.call("/admin/cms/api/help_article/items").status_code == 401


def test_editor_can_write_drafts_but_cannot_publish(application, client):
    headers = staff(
        application,
        [
            "help_article.view_help_article",
            "help_article.add_help_article",
            "help_article.change_help_article",
        ],
    )
    path = "/admin/cms/api/help_article/items"
    assert (
        client.post(path, json_data={"title": "Draft"}, headers=headers).status_code
        == 201
    )
    assert (
        client.post(
            path,
            json_data={"title": "Forbidden", "status": "published"},
            headers=headers,
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/admin/cms/api/import/help_article",
            json_data=[{"title": "Forbidden", "status": "published"}],
            headers=headers,
        ).status_code
        == 403
    )


def test_publisher_requires_csrf(application, client):
    headers = staff(
        application, ["help_article.add_help_article", "cms.publish_content"]
    )
    path = "/admin/cms/api/help_article/items"
    assert (
        client.post(
            path,
            json_data={"title": "Published", "status": "published"},
            headers=headers,
        ).status_code
        == 201
    )
    assert (
        client.post(
            path,
            json_data={"title": "Missing token"},
            headers={"cookie": headers["cookie"]},
        ).status_code
        == 400
    )


def test_standalone_cms_is_closed_by_default():
    app = Flaxon("cms-test", debug=True)
    cms = CMS(app)
    cms.register(ContentType("article", fields=[CMSField("title")]))
    assert (
        TestClient(app)
        .post("/admin/cms/api/article/items", json_data={"title": "Forbidden"})
        .status_code
        == 403
    )


def test_database_and_cms_survive_new_application_instance(
    application, client, account, tmp_path
):
    from app import create_app

    account.call("/api/projects/", "post", {"name": "Persistent"})
    articles = application.cms.content_types["help_article"]
    articles.create({"title": "Persistent article", "status": "published"})
    application.cms._save(articles)
    new_app = create_app(
        tmp_path / "app.sqlite3", tmp_path / "admin.sqlite3", debug=True
    )
    assert (
        asyncio.run(new_app.course_db.one("SELECT name FROM projects"))["name"]
        == "Persistent"
    )
    assert len(new_app.cms.content_types["help_article"].items) == 1


def test_staff_model_adapter_reads_domain_records_and_denies_ungranted_changes(
    application, client, account
):
    account.call("/api/projects/", "post", {"name": "Domain record"})
    headers = staff(application, ["admin.view_dashboard", "project.view_project"])
    response = client.get("/admin/project", headers=headers)
    assert response.status_code == 200
    assert "Domain record" in response.text
    assert client.get("/admin/project/1/edit", headers=headers).status_code == 403
    assert client.post("/admin/project/1/delete", headers=headers).status_code == 403
