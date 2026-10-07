"""Show the project API over HTTP; start the development server first."""
import secrets
import httpx


def main():
    # Each run creates its own learner and project in your development database.
    with httpx.Client(base_url="http://127.0.0.1:8000", trust_env=False) as client:
        response = client.get("/api/auth/session")
        response.raise_for_status()
        csrf = response.json()["data"]["csrf"]
        response = client.post(
            "/api/auth/register",
            headers={"X-CSRF-Token": csrf},
            json={"name": "Sample Learner", "email": f"sample-{secrets.token_hex(6)}@example.test", "password": "LearningPython123!"},
        )
        response.raise_for_status()
        csrf = response.json()["data"]["csrf"]
        response = client.post(
            "/api/projects/", headers={"X-CSRF-Token": csrf},
            json={"name": "My first project", "description": "Record the sample lesson"},
        )
        response.raise_for_status()
        assert response.status_code == 201
        project = response.json()["data"]
        print("Created:", project)
        response = client.get(f"/api/projects/{project['id']}")
        response.raise_for_status()
        print("Read:", response.json()["data"])
        response = client.post("/api/projects/", headers={"X-CSRF-Token": csrf}, json={"name": " "})
        assert response.status_code == 400
        print("Invalid input rejected:", response.status_code)
        print("Use your own browser account to create a separate project on /projects.")


if __name__ == "__main__":
    main()
