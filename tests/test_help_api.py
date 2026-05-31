"""Help API route tests."""

from __future__ import annotations

from starlette.testclient import TestClient

from openbci_mcp.app import app


def test_help_index_and_doc() -> None:
    client = TestClient(app)
    index = client.get("/api/help")
    assert index.status_code == 200
    body = index.json()
    assert body["success"] is True
    assert "overview" in body["docs"]

    doc = client.get("/api/help/overview")
    assert doc.status_code == 200
    assert "openbci-mcp" in doc.json()["markdown"].lower()


def test_backend_help_redirects_to_webapp() -> None:
    client = TestClient(app, follow_redirects=False)
    response = client.get("/help")
    assert response.status_code == 307
    assert response.headers["location"] == "http://127.0.0.1:10758/help"
