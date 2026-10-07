"""Idempotent sample content. Register your own user before running this command."""

from app import create_app


async def seed():
    app = create_app()
    user = await app.course_db.one("SELECT id FROM users ORDER BY id LIMIT 1")
    if not user:
        raise ValueError(
            "Register an account in the browser before seeding sample projects."
        )
    if not await app.course_db.one(
        "SELECT id FROM projects WHERE owner_id = ?", (user["id"],)
    ):
        project_id = await app.course_db.execute(
            "INSERT INTO projects(owner_id, name, description) VALUES (?, ?, ?)",
            (
                user["id"],
                "Launch my portfolio",
                "A small project to practise planning.",
            ),
        )
        for title, status in [
            ("Choose a design", "done"),
            ("Build the homepage", "doing"),
            ("Deploy the website", "todo"),
        ]:
            await app.course_db.execute(
                "INSERT INTO tasks(project_id, title, status) VALUES (?, ?, ?)",
                (project_id, title, status),
            )
    articles = app.cms.content_types["help_article"]
    if not articles.items:
        articles.create(
            {
                "title": "Getting started",
                "summary": "Create a project, add tasks, and track progress.",
                "body": "<p>Open Projects, create a project, and add your first task. Move tasks from To do to Doing to Done.</p>",
                "status": "published",
            }
        )
        app.cms._save(articles)
    print("Sample projects, tasks, and help content are ready.")
