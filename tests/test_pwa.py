"""Verify the course's optional PWA assets and production configuration."""
import json
import runpy
from pathlib import Path
from flaxon.testing import TestClient

ROOT = Path(__file__).resolve().parents[1]


def test_course_pwa_assets(application):
    runpy.run_path(str(ROOT / "scripts/create_pwa_icons.py"), run_name="__main__")
    integration = application.teloce
    result = integration.build()
    assert result["plugins"]["enabled"] == ["pwa"]
    client = TestClient(application)
    shell = client.get("/")
    assert shell.status_code == 200
    assert 'rel="manifest"' in shell.text
    manifest = json.loads(client.get("/_flaxon/teloce-plugins/manifest.webmanifest").text)
    assert manifest["start_url"] == "/projects"
    assert {icon["sizes"] for icon in manifest["icons"]} == {"192x192", "512x512"}
    for icon in manifest["icons"]:
        response = client.get(icon["src"])
        assert response.status_code == 200
        assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
    worker = client.get("/teloce-sw.js")
    assert worker.headers["service-worker-allowed"] == "/"
    assert "application/javascript" in worker.headers["content-type"]
    assert "/api/" not in worker.text
    assert "/admin/" not in worker.text
    plugin = client.get("/_flaxon/teloce-plugins/index.js").text
    assert '"enabled": false' in plugin  # Debug builds do not register a worker.
