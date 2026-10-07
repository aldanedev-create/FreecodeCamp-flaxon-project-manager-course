"""Project APIs always constrain queries by the signed-in user's id."""

from pathlib import Path
from flaxon.modules import FlaxonModule
from flaxon.http import JSONResponse
from flaxon.exceptions import NotFound
from security import require_user, check_csrf
from validation import json_object, text

projects = FlaxonModule(
    "projects",
    ui_dir=Path(__file__).parent / "ui",
    ui_routes={
        "ProjectList.js": "/projects",
        "ProjectDetails/[id].js": "/projects/:id",
    },
)


async def owned_project(request, project_id):
    user = await require_user(request)
    project = await request.app.course_db.one(
        "SELECT * FROM projects WHERE id = ? AND owner_id = ?", (project_id, user["id"])
    )
    if project is None:
        raise NotFound("Project not found.")
    return project


@projects.get("/")
async def list_projects(request):
    user = await require_user(request)
    items = await request.app.course_db.all(
        "SELECT * FROM projects WHERE owner_id = ? ORDER BY id DESC", (user["id"],)
    )
    return {"data": items}


@projects.post("/")
async def create_project(request):
    await check_csrf(request)
    user = await require_user(request)
    data = await json_object(request)
    name = text(data, "name")
    description = text(data, "description", 1000, required=False)
    project_id = await request.app.course_db.execute(
        "INSERT INTO projects(owner_id, name, description) VALUES (?, ?, ?)",
        (user["id"], name, description),
    )
    return JSONResponse(
        {"data": await owned_project(request, project_id)}, status_code=201
    )


@projects.get("/<int:project_id>")
async def get_project(request, project_id):
    return {"data": await owned_project(request, project_id)}


@projects.put("/<int:project_id>")
async def update_project(request, project_id):
    await check_csrf(request)
    project = await owned_project(request, project_id)
    data = await json_object(request)
    name = text(data, "name")
    description = text(data, "description", 1000, required=False)
    await request.app.course_db.execute(
        "UPDATE projects SET name = ?, description = ? WHERE id = ? AND owner_id = ?",
        (name, description, project_id, project["owner_id"]),
    )
    return {"data": await owned_project(request, project_id)}


@projects.delete("/<int:project_id>")
async def delete_project(request, project_id):
    await check_csrf(request)
    project = await owned_project(request, project_id)
    await request.app.course_db.execute(
        "DELETE FROM projects WHERE id = ? AND owner_id = ?",
        (project_id, project["owner_id"]),
    )
    return {"data": {"deleted": True}}
