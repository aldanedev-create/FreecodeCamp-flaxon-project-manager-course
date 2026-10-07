"""Staff model adapters reuse the domain database; CMS owns only editorial content."""

from flaxon.admin import AdminDashboard, AdminConfig
from flaxon.admin.registry import Registry
from flaxon.admin.cms import CMS, ContentType, CMSField
from flaxon.exceptions import BadRequest
from validation import text, task_fields


def configure_backoffice(app, admin_path, uploads_path):
    admin = AdminDashboard(
        app,
        registry=Registry(),
        users=[],
        storage_path=str(admin_path),
        upload_dir=str(uploads_path),
        strict_permissions=True,
        microservices=False,
        config=AdminConfig(site_title="Project Manager Operations"),
    )

    class ProjectAdmin:
        @classmethod
        async def get_instances(cls):
            return await app.course_db.all("SELECT * FROM projects ORDER BY id DESC")

        @classmethod
        async def get_instance(cls, object_id):
            return await app.course_db.one(
                "SELECT * FROM projects WHERE id = ?", (object_id,)
            )

        @classmethod
        async def create_instance(cls, data):
            raise BadRequest(
                "Create projects through the application to assign an owner."
            )

        @classmethod
        async def update_instance(cls, object_id, data):
            current = await cls.get_instance(object_id)
            if current is None:
                return None
            name = text(data, "name")
            description = text(data, "description", 1000, required=False)
            await app.course_db.execute(
                "UPDATE projects SET name = ?, description = ? WHERE id = ?",
                (name, description, object_id),
            )
            return await cls.get_instance(object_id)

        @classmethod
        async def delete_instance(cls, object_id):
            current = await cls.get_instance(object_id)
            if not current:
                return False
            await app.course_db.execute(
                "DELETE FROM projects WHERE id = ?", (object_id,)
            )
            return True

    class TaskAdmin:
        @classmethod
        async def get_instances(cls):
            return await app.course_db.all("SELECT * FROM tasks ORDER BY id DESC")

        @classmethod
        async def get_instance(cls, object_id):
            return await app.course_db.one(
                "SELECT * FROM tasks WHERE id = ?", (object_id,)
            )

        @classmethod
        async def create_instance(cls, data):
            raise BadRequest("Create tasks through their project in the application.")

        @classmethod
        async def update_instance(cls, object_id, data):
            current = await cls.get_instance(object_id)
            if current is None:
                return None
            values = {**current, **task_fields(data, partial=True)}
            await app.course_db.execute(
                "UPDATE tasks SET title = ?, status = ?, due_date = ? WHERE id = ?",
                (values["title"], values["status"], values["due_date"], object_id),
            )
            return await cls.get_instance(object_id)

        @classmethod
        async def delete_instance(cls, object_id):
            current = await cls.get_instance(object_id)
            if not current:
                return False
            await app.course_db.execute("DELETE FROM tasks WHERE id = ?", (object_id,))
            return True

    admin.register(
        ProjectAdmin,
        name="project",
        list_display=["id", "name", "owner_id"],
        search_fields=["name"],
        fields=["name", "description"],
        readonly_fields=["id", "owner_id"],
    )
    admin.register(
        TaskAdmin,
        name="task",
        list_display=["id", "title", "status", "due_date"],
        search_fields=["title"],
        list_filter=["status"],
        fields=["title", "status", "due_date"],
        readonly_fields=["id", "project_id"],
    )
    cms = CMS(app, auth=admin.auth)
    cms.register(
        ContentType(
            "help_article",
            label="Help article",
            label_plural="Help articles",
            fields=[
                CMSField("title", required=True),
                CMSField("summary", type="textarea"),
                CMSField("body", type="richtext"),
            ],
            statuses=["draft", "published"],
            list_display=["title", "status"],
        )
    )
    cms.register(
        ContentType(
            "announcement",
            fields=[
                CMSField("title", required=True),
                CMSField("body", type="textarea"),
            ],
            statuses=["draft", "published"],
        )
    )
    app.backoffice, app.cms = admin, cms
