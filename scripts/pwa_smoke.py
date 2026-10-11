"""Check production PWA registration and offline fallback using disposable data."""
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time

import httpx
from playwright.sync_api import sync_playwright
from create_pwa_icons import main as create_icons

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8124"


def main():
    create_icons()
    with tempfile.TemporaryDirectory(prefix="course-pwa-") as directory:
        environment = {
            **os.environ,
            "DATA_DIR": directory,
            "FLAXON_DEBUG": "0",
            "FLAXON_SECRET_KEY": secrets.token_urlsafe(48),
            "PUBLIC_ORIGIN": BASE,
        }
        subprocess.run([sys.executable, "management.py", "migrate"], cwd=ROOT, env=environment, check=True)
        with open(Path(directory) / "server.log", "w") as log:
            server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--port", "8124"], cwd=ROOT, env=environment, stdout=log, stderr=log)
            try:
                for _ in range(150):
                    try:
                        if httpx.get(BASE + "/login", trust_env=False).status_code == 200:
                            break
                    except httpx.ConnectError:
                        pass
                    time.sleep(0.1)
                else:
                    raise RuntimeError((Path(directory) / "server.log").read_text())
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch()
                    context = browser.new_context(service_workers="allow")
                    page = context.new_page()
                    page.goto(BASE + "/login")
                    page.evaluate("async () => { await Promise.race([navigator.serviceWorker.ready, new Promise((_, reject) => setTimeout(() => reject(new Error('Service worker did not become ready')), 15000))]); }")
                    page.reload()
                    page.wait_for_function("navigator.serviceWorker.controller !== null")
                    assert page.locator('link[rel="manifest"]').count() == 1
                    cached = page.evaluate("async () => { const names = await caches.keys(); const urls = []; for (const name of names) { for (const request of await (await caches.open(name)).keys()) urls.push(new URL(request.url).pathname); } return urls; }")
                    assert cached and any(path.endswith("offline.html") for path in cached)
                    assert not any(path.startswith(("/api/", "/admin")) for path in cached)
                    # Browser offline emulation can leave worker fetches online.
                    # Stop the server so this checks an actual network failure.
                    server.terminate()
                    server.wait(timeout=10)
                    context.set_offline(True)
                    page.goto(BASE + "/projects")
                    assert page.get_by_role("heading", name="You are offline").is_visible()
                    context.set_offline(False)
                    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--port", "8124"], cwd=ROOT, env=environment, stdout=log, stderr=log)
                    for _ in range(150):
                        try:
                            if httpx.get(BASE + "/login", trust_env=False).status_code == 200:
                                break
                        except httpx.ConnectError:
                            pass
                        time.sleep(0.1)
                    else:
                        raise RuntimeError("Server did not restart after the offline check")
                    page.goto(BASE + "/login")
                    assert page.get_by_label("Email", exact=True).is_visible()
                    context.close()
                    browser.close()
                    print("PWA registration, private-cache exclusion, offline fallback and reconnect passed.")
            finally:
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()


if __name__ == "__main__":
    main()
