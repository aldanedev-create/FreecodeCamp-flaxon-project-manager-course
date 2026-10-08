"""Idempotent sample content. Register your own user before running this command."""

from app import create_app
from models import User, Project, Task


async def seed():
    app = create_app()
    async with app.db:
        user = await User.all().order_by("id").first()
        if user is None:
            raise ValueError("Register an account before seeding sample projects.")
        if not await Project.filter(owner_id=user.id).exists():
            project = await Project.create(
                owner_id=user.id,
                name="Launch my portfolio",
                description="A small project to practise planning.",
            )
            for title, status in [
                ("Choose a design", "done"),
                ("Build the homepage", "doing"),
                ("Deploy the website", "todo"),
            ]:
                await Task.create(project_id=project.id, title=title, status=status)
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
