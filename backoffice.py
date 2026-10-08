"""Staff model adapters reuse the domain database; CMS owns only editorial content."""

from models import Project, Task
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
            return await Project.all().order_by("-id").values()

        @classmethod
        async def get_instance(cls, object_id):
            return await Project.filter(id=object_id).first().values()

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
            await Project.filter(id=object_id).update(
                name=name, description=description
            )
            return await cls.get_instance(object_id)

        @classmethod
        async def delete_instance(cls, object_id):
            current = await cls.get_instance(object_id)
            if not current:
                return False
            await Project.filter(id=object_id).delete()
            return True

    class TaskAdmin:
        @classmethod
        async def get_instances(cls):
            return await Task.all().order_by("-id").values()

        @classmethod
        async def get_instance(cls, object_id):
            return await Task.filter(id=object_id).first().values()

        @classmethod
        async def create_instance(cls, data):
            raise BadRequest("Create tasks through their project in the application.")

        @classmethod
        async def update_instance(cls, object_id, data):
            current = await cls.get_instance(object_id)
            if current is None:
                return None
            values = {**current, **task_fields(data, partial=True)}
            await Task.filter(id=object_id).update(
                **{key: values[key] for key in ("title", "status", "due_date")}
            )
            return await cls.get_instance(object_id)

        @classmethod
        async def delete_instance(cls, object_id):
            current = await cls.get_instance(object_id)
            if not current:
                return False
            await Task.filter(id=object_id).delete()
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
