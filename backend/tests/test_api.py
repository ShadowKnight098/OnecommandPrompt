"""End-to-end integration tests for FastAPI backend routes."""
import io
import zipfile
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_sample_zip():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("main.py", "import requests\nprint('Running app')\nif __name__ == '__main__':\n    pass")
        zf.writestr("requirements.txt", "requests>=2.28.0\n")
    buffer.seek(0)
    return buffer


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_and_inspect_flow():
    zip_bytes = create_sample_zip()
    files = {"file": ("demo-project.zip", zip_bytes, "application/zip")}

    # 1. Upload project
    upload_res = client.post("/api/projects/upload", files=files)
    assert upload_res.status_code == 201
    data = upload_res.json()
    project_id = data["id"]
    assert project_id is not None
    assert data["analysis"]["entry_point"] == "main.py"
    assert data["analysis"]["dependency_source"] == "requirements.txt"

    # 2. Get project details
    get_res = client.get(f"/api/projects/{project_id}")
    assert get_res.status_code == 200
    details = get_res.json()
    assert "installer_commands" in details
    assert "windows" in details["installer_commands"]
    assert "unix" in details["installer_commands"]

    # 3. Fetch Windows PowerShell script
    ps_res = client.get(f"/i/{project_id}.ps1")
    assert ps_res.status_code == 200
    assert "One-Command Project Installer" in ps_res.text
    assert "requests" in ps_res.text

    # 4. Fetch Unix Bash script
    sh_res = client.get(f"/i/{project_id}.sh")
    assert sh_res.status_code == 200
    assert "#!/usr/bin/env bash" in sh_res.text


def test_upload_folder_endpoint():
    files = [
        ("files", ("my-folder/main.py", b"import math\nprint('hello')", "text/x-python")),
        ("files", ("my-folder/utils.py", b"def add(x, y): return x + y", "text/x-python")),
    ]
    res = client.post("/api/projects/upload-folder", files=files)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["analysis"]["entry_point"] == "main.py"


def test_user_privacy_and_scoped_projects():
    # 1. Upload private project for user_alpha
    zip_bytes = create_sample_zip()
    files = {"file": ("alpha-secret.zip", zip_bytes, "application/zip")}
    data_form = {
        "project_name": "alpha-secret",
        "user_id": "user_alpha_123",
        "user_email": "alpha@example.com",
        "is_public": "false",
    }
    upload_res = client.post("/api/projects/upload", files=files, data=data_form)
    assert upload_res.status_code == 201
    record = upload_res.json()
    assert record["user_id"] == "user_alpha_123"
    assert record["is_public"] is False

    # 2. Public showcase listing should not expose the private project to anonymous users
    public_list = client.get("/api/projects").json()["projects"]
    public_ids = [p["id"] for p in public_list]
    assert record["id"] not in public_ids

    # 3. User-scoped listing should return the user's private project
    user_list = client.get(f"/api/projects?user_id=user_alpha_123").json()["projects"]
    user_ids = [p["id"] for p in user_list]
    assert record["id"] in user_ids


