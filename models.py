"""Application tables. Generate Python migrations whenever these models change."""

from flaxon.db import Model, fields


class User(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=80)
    email = fields.CharField(max_length=254, unique=True)
    password_hash = fields.TextField()

    class Meta:
        table = "users"

    def __str__(self):
        return self.name


class Project(Model):
    id = fields.IntField(primary_key=True)
    owner = fields.ForeignKeyField(
        "models.User", related_name="projects", on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=120)
    description = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "projects"

    def __str__(self):
        return self.name


class Task(Model):
    id = fields.IntField(primary_key=True)
    project = fields.ForeignKeyField(
        "models.Project", related_name="tasks", on_delete=fields.CASCADE
    )
    title = fields.CharField(max_length=200)
    status = fields.CharField(max_length=10, default="todo")
    due_date = fields.DateField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tasks"

    def __str__(self):
        return self.title


class Session(Model):
    token_hash = fields.CharField(max_length=64, primary_key=True)
    user = fields.ForeignKeyField("models.User", null=True, on_delete=fields.CASCADE)
    csrf = fields.CharField(max_length=64)
    expires_at = fields.BigIntField(db_index=True)

    class Meta:
        table = "sessions"


class AuthAttempt(Model):
    key = fields.CharField(max_length=64, primary_key=True)
    attempts = fields.IntField(default=0)
    started_at = fields.BigIntField(db_index=True)

    class Meta:
        table = "auth_attempts"
