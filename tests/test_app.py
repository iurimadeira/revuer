from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from revuer.app import create_app


@pytest.fixture
def static_dir(tmp_path: Path) -> Path:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<title>revuer</title>")
    (tmp_path / "assets" / "app.js").write_text("console.log(1)")
    return tmp_path


def test_health(tmp_path: Path) -> None:
    response = TestClient(create_app(tmp_path)).get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("path", ["/", "/some/client/route"])
def test_serves_index_for_ui_routes(static_dir: Path, path: str) -> None:
    response = TestClient(create_app(static_dir)).get(path)
    assert response.status_code == 200
    assert "<title>revuer</title>" in response.text


def test_serves_static_assets(static_dir: Path) -> None:
    response = TestClient(create_app(static_dir)).get("/assets/app.js")
    assert response.status_code == 200
    assert response.text == "console.log(1)"


def test_does_not_serve_files_outside_static_dir(static_dir: Path) -> None:
    (static_dir.parent / "secret.txt").write_text("secret")
    response = TestClient(create_app(static_dir)).get("/..%2Fsecret.txt")
    assert "secret" not in response.text


def test_unknown_api_route_is_not_found(static_dir: Path) -> None:
    response = TestClient(create_app(static_dir)).get("/api/missing")
    assert response.status_code == 404


def test_ui_not_built(tmp_path: Path) -> None:
    response = TestClient(create_app(tmp_path / "missing")).get("/")
    assert response.status_code == 503
    assert "UI not built" in response.text
