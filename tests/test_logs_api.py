"""Logs API route tests."""

from __future__ import annotations

from starlette.testclient import TestClient

from openbci_mcp.activity_log import log_activity
from openbci_mcp.app import app


def test_logs_query_export_and_clear() -> None:
    client = TestClient(app)
    log_activity("board_action", "connect test", level="INFO", meta={"operation": "connect"})

    logs = client.get("/api/logs?limit=10&kind=board_action").json()
    assert logs["total"] >= 1
    assert logs["entries"][0]["kind"] == "board_action"
    assert "level" in logs["entries"][0]

    stats = client.get("/api/logs/stats").json()
    assert stats["total"] >= 1
    assert stats["rotation"] == "ring_buffer"

    export = client.get("/api/logs/export?format=json&kind=board_action")
    assert export.status_code == 200
    assert "application/json" in export.headers["content-type"]

    cleared = client.delete("/api/logs")
    assert cleared.json()["success"] is True
    assert client.get("/api/logs/stats").json()["total"] >= 1


def test_logs_and_settings_redirect_to_webapp() -> None:
    client = TestClient(app, follow_redirects=False)
    for path in ("/logs", "/settings"):
        response = client.get(path)
        assert response.status_code == 307
        assert response.headers["location"] == f"http://127.0.0.1:10758{path}"


def test_llm_providers_endpoint() -> None:
    client = TestClient(app)
    body = client.get("/api/llm/providers").json()
    assert body["success"] is True
    assert isinstance(body["providers"], list)
