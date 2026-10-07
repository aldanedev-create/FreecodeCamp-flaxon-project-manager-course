"""Tasks belong to projects; project ownership guards every task operation."""

from flaxon.modules import FlaxonModule
from flaxon.http import JSONResponse
from flaxon.exceptions import NotFound, BadRequest
from security import check_csrf
from validation import json_object, task_fields
from modules.projects.module import owned_project

tasks = FlaxonModule("tasks")


async def owned_task(request, task_id):
    task = await request.app.course_db.one(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    )
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
    sql = "SELECT * FROM tasks WHERE project_id = ?"
    parameters = [project_id]
    if status:
        sql += " AND status = ?"
        parameters.append(status)
    return {
        "data": await request.app.course_db.all(sql + " ORDER BY id DESC", parameters)
    }


@tasks.post("/project/<int:project_id>")
async def create_task(request, project_id):
    await check_csrf(request)
    await owned_project(request, project_id)
    data = task_fields(await json_object(request))
    task_id = await request.app.course_db.execute(
        "INSERT INTO tasks(project_id, title, status, due_date) VALUES (?, ?, ?, ?)",
        (project_id, data["title"], data["status"], data["due_date"]),
    )
    return JSONResponse({"data": await owned_task(request, task_id)}, status_code=201)


@tasks.patch("/<int:task_id>")
async def update_task(request, task_id):
    await check_csrf(request)
    current = await owned_task(request, task_id)
    data = task_fields(await json_object(request), partial=True)
    updated = {**current, **data}
    await request.app.course_db.execute(
        "UPDATE tasks SET title = ?, status = ?, due_date = ? WHERE id = ?",
        (updated["title"], updated["status"], updated["due_date"], task_id),
    )
    return {"data": await owned_task(request, task_id)}


@tasks.delete("/<int:task_id>")
async def delete_task(request, task_id):
    await check_csrf(request)
    await owned_task(request, task_id)
    await request.app.course_db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return {"data": {"deleted": True}}
