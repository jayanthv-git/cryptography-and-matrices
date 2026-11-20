"""Verify the same-origin deployment entry point, including real calculations."""
import pytest
from starlette.testclient import TestClient

from backend.production import create_app


@pytest.fixture
def client(tmp_path):
    (tmp_path / "index.html").write_text('<html><script src="/assets/app.js"></script></html>')
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text('console.log("test asset")')
    with TestClient(create_app(tmp_path)) as client:
        yield client


def test_frontend_and_api_share_origin(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "text/html" in page.headers["content-type"]
    assert page.headers["cache-control"] == "no-cache"
    assert client.get("/assets/app.js").text == 'console.log("test asset")'
    assert client.get("/api/health").json() == {"status": "ok"}
    result = client.post("/api/cipher", json={"text": "HI", "key": [[3, 3], [2, 5]]})
    assert result.status_code == 200
    assert result.json()["ciphertext"] == "TC"


def test_api_errors_and_downloads_survive_production_wrapper(client):
    response = client.post("/api/cipher", json={"text": "HI", "key": [[True, 3], [2, 5]]})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert client.get("/api/missing").status_code == 404
    assert "error" in client.get("/api/missing").json()
    template = client.get("/api/survey/template")
    assert template.status_code == 200
    assert "attachment" in template.headers["content-disposition"]
    assert client.get("/openapi.json").json()["info"]["title"] == "MatrixCrypt Lab"


def test_missing_assets_and_private_files_are_not_spa_fallback(client):
    for path in ["/assets/missing.js", "/requirements-lock.txt", "/.env", "/backend/api/main.py", "/assets/%2e%2e/index.html"]:
        assert client.get(path).status_code == 404


def test_missing_frontend_fails_at_startup(tmp_path):
    with pytest.raises(RuntimeError, match="Frontend build is missing"):
        create_app(tmp_path)
