"""Project APIs always constrain queries by the signed-in user's id."""

from pathlib import Path
from models import Project
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
    project = await Project.filter(id=project_id, owner_id=user["id"]).first().values()
    if project is None:
        raise NotFound("Project not found.")
    return project


@projects.get("/")
async def list_projects(request):
    user = await require_user(request)
    items = await Project.filter(owner_id=user["id"]).order_by("-id").values()
    return {"data": items}


@projects.post("/")
async def create_project(request):
    await check_csrf(request)
    user = await require_user(request)
    data = await json_object(request)
    name = text(data, "name")
    description = text(data, "description", 1000, required=False)
    project = await Project.create(
        owner_id=user["id"], name=name, description=description
    )
    project_id = project.id
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
    await Project.filter(id=project_id, owner_id=project["owner_id"]).update(
        name=name, description=description
    )
    return {"data": await owned_project(request, project_id)}


@projects.delete("/<int:project_id>")
async def delete_project(request, project_id):
    await check_csrf(request)
    project = await owned_project(request, project_id)
    await Project.filter(id=project_id, owner_id=project["owner_id"]).delete()
    return {"data": {"deleted": True}}
