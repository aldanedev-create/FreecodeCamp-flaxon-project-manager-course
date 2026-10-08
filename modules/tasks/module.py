"""Tasks belong to projects; project ownership guards every task operation."""

from models import Task
from flaxon.modules import FlaxonModule
from flaxon.http import JSONResponse
from flaxon.exceptions import NotFound, BadRequest
from security import check_csrf
from validation import json_object, task_fields
from modules.projects.module import owned_project

tasks = FlaxonModule("tasks")


async def owned_task(request, task_id):
    task = await Task.filter(id=task_id).first().values()
    if task is None:
        raise NotFound("Task not found.")
    await owned_project(request, task["project_id"])
    return task


@tasks.get("/project/<int:project_id>")
async def list_tasks(request, project_id):
    await owned_project(request, project_id)
    status = request.query.get("status")
    if status and status not in ("todo", "doing", "done"):
        raise BadRequest("Unknown task status.")
    query = Task.filter(project_id=project_id)
    if status:
        query = query.filter(status=status)
    return {"data": await query.order_by("-id").values()}


@tasks.post("/project/<int:project_id>")
async def create_task(request, project_id):
    await check_csrf(request)
    await owned_project(request, project_id)
    data = task_fields(await json_object(request))
    task = await Task.create(project_id=project_id, **data)
    task_id = task.id
    return JSONResponse({"data": await owned_task(request, task_id)}, status_code=201)


@tasks.patch("/<int:task_id>")
async def update_task(request, task_id):
    await check_csrf(request)
    current = await owned_task(request, task_id)
    data = task_fields(await json_object(request), partial=True)
    await Task.filter(id=task_id, project_id=current["project_id"]).update(**data)
    return {"data": await owned_task(request, task_id)}


@tasks.delete("/<int:task_id>")
async def delete_task(request, task_id):
    await check_csrf(request)
    await owned_task(request, task_id)
    await Task.filter(id=task_id).delete()
    return {"data": {"deleted": True}}
