"""Run desktop/mobile workflows against a fresh temporary database. No real user data."""

import os
import subprocess
import sys
import secrets
import tempfile
import time
from pathlib import Path
import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8123"


def main():
    with tempfile.TemporaryDirectory() as directory:
        production = "--production" in sys.argv
        env = {
            **os.environ,
            "DATA_DIR": directory,
            "FLAXON_DEBUG": "0" if production else "1",
            "PUBLIC_ORIGIN": BASE,
            "FLAXON_SECRET_KEY": secrets.token_urlsafe(48),
        }
        subprocess.run(
            [sys.executable, "management.py", "migrate"], cwd=ROOT, env=env, check=True
        )
        # Bootstrap a staff account in the disposable Admin store before startup.
        bootstrap = """
from flaxon.admin.services import AdminAuth, AdminStore
from settings import ADMIN_DATABASE_PATH
store = AdminStore(str(ADMIN_DATABASE_PATH))
auth = AdminAuth(users=[], store=store, strict_permissions=True)
record = auth.add_user({'username': 'course-admin', 'password': 'CourseStaffPassword123!', 'roles': ['administrator']})
store.set('users', 'course-admin', record)
"""
        subprocess.run([sys.executable, "-c", bootstrap], cwd=ROOT, env=env, check=True)
        log = open(Path(directory) / "server.log", "w")
        server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--port", "8123"],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=log,
        )
        try:
            for _ in range(150):
                try:
                    if httpx.get(BASE + "/", trust_env=False).status_code == 200:
                        break
                except httpx.ConnectError:
                    time.sleep(0.1)
            else:
                raise RuntimeError("Server failed to start")
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                staff_context = browser.new_context()
                staff_page = staff_context.new_page()
                staff_page.goto(BASE + "/admin/login")
                staff_page.get_by_label("Username", exact=True).fill("course-admin")
                staff_page.get_by_label("Password", exact=True).fill(
                    "CourseStaffPassword123!"
                )
                staff_page.get_by_role("button", name="Sign in", exact=True).click()
                staff_page.wait_for_url("**/admin/")
                assert (
                    staff_page.evaluate(
                        "async () => (await fetch('/admin/project')).status"
                    )
                    == 200
                )
                staff_page.goto(BASE + "/admin/cms/")
                csrf = staff_page.locator('meta[name="csrf-token"]').get_attribute(
                    "content"
                )
                response = staff_page.evaluate(
                    """async (csrf) => {
                    const response = await fetch('/admin/cms/api/help_article/items', {
                        method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf},
                        body: JSON.stringify({title: 'Browser help guide', summary: 'Published by staff', body: '<p>Safe help content.</p>', status: 'published'})
                    });
                    return {status: response.status, body: await response.text()};
                }""",
                    csrf,
                )
                assert response["status"] == 201, response["body"]
                staff_context.close()
                print("Staff Admin login and CMS publication passed")
                for width in [1440, 390]:
                    context = browser.new_context(
                        viewport={"width": width, "height": 900}
                    )
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto(BASE + "/login")
                    page.get_by_role("button", name="Register instead").click()
                    page.get_by_label("Name", exact=True).fill("Course Learner")
                    page.get_by_label("Email", exact=True).fill(
                        f"learner{width}@example.test"
                    )
                    page.get_by_label("Password", exact=True).fill("LearningPython123!")
                    page.get_by_role(
                        "button", name="Create account", exact=True
                    ).click()
                    try:
                        page.wait_for_url("**/projects", timeout=8000)
                    except Exception:
                        print("Browser errors:", errors)
                        print("URL:", page.url)
                        print("Page:", page.locator("body").inner_text())
                        raise
                    page.get_by_label("Name", exact=True).fill("Browser project")
                    page.get_by_label("Description", exact=True).fill(
                        "Verified in the browser"
                    )
                    page.get_by_role(
                        "button", name="Create project", exact=True
                    ).click()
                    page.get_by_role("link", name="Browser project").click()
                    page.get_by_role(
                        "heading", name="Browser project", exact=True
                    ).wait_for()
                    page.get_by_label("Task title").fill("Record the lesson")
                    page.get_by_role("button", name="Add task", exact=True).click()
                    page.get_by_text("Record the lesson", exact=True).wait_for()
                    page.get_by_label("Task status", exact=True).select_option("done")
                    page.get_by_text("100% complete", exact=True).wait_for()
                    page.get_by_label("Filter tasks").select_option("todo")
                    page.get_by_text(
                        "No tasks match this filter.", exact=True
                    ).wait_for()
                    page.get_by_label("Filter tasks").select_option("all")
                    page.evaluate("window.courseNavigationMarker = 42")
                    page.get_by_role("link", name="Help", exact=True).click()
                    page.get_by_role("heading", name="Help centre").wait_for()
                    assert (
                        page.evaluate("window.courseNavigationMarker") == 42
                    ), "SPA link reloaded the document"
                    page.get_by_role("link", name="Browser help guide").click()
                    page.get_by_role(
                        "heading", name="Browser help guide", exact=True
                    ).wait_for()
                    page.get_by_text("Safe help content.", exact=True).wait_for()
                    page.go_back()
                    page.get_by_role("heading", name="Help centre").wait_for()
                    page.go_back()
                    page.get_by_role(
                        "heading", name="Browser project", exact=True
                    ).wait_for()
                    page.reload()
                    page.get_by_text("100% complete", exact=True).wait_for()
                    assert page.evaluate(
                        "document.documentElement.scrollWidth <= innerWidth"
                    ), "Mobile overflow"
                    page.get_by_role("link", name="Account", exact=True).click()
                    page.get_by_role("button", name="Sign out").click()
                    page.get_by_text("Signed out.", exact=True).wait_for()
                    assert page.request.get(BASE + "/api/projects/").status == 401
                    assert not errors, errors
                    context.close()
                    print(
                        f"{'Production MinifyJS' if production else 'Development'} browser workflow passed at {width}px"
                    )
                browser.close()
        finally:
            server.terminate()
            server.wait(timeout=10)
            log.close()


if __name__ == "__main__":
    main()
