"""Registration metadata checked by management.py; the custom backoffice uses this same schema."""

from models import Project, Task


def register(admin):
    admin.register(
        Project,
        name="project",
        fields=["name", "description"],
        readonly_fields=["id", "owner_id"],
        search_fields=["name"],
    )
    admin.register(
        Task,
        name="task",
        fields=["title", "status", "due_date"],
        readonly_fields=["id", "project_id"],
        list_filter=["status"],
    )
