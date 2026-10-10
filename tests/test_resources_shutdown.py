"""Tests for the issue-#1 resource, shutdown registration, and new endpoints."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from openbci_mcp.app import app
from openbci_mcp.mcp_app import mcp
from openbci_mcp.resources import board_capabilities

client = TestClient(app, raise_server_exceptions=False)


def test_board_capabilities_resource_shape():
    payload = board_capabilities()
    assert payload["success"] is True
    keys = {b["key"] for b in payload["boards"]}
    assert {"cyton", "ganglion", "cyton_daisy", "galea", "synthetic", "streaming"} <= keys
    cyton = next(b for b in payload["boards"] if b["key"] == "cyton")
    assert cyton["board_id"] == 0
    assert cyton["eeg_channels"] == 8
    assert cyton["transport"] == "serial"
    assert cyton["units"] == "microvolts"
    ganglion = next(b for b in payload["boards"] if b["key"] == "ganglion")
    assert ganglion["transport"] == "ble"
    # Unknown-by-config fields are null, never invented.
    galea = next(b for b in payload["boards"] if b["key"] == "galea")
    assert galea["eeg_channels"] is None


def test_health_status_ok_shape():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["service"] == "openbci-mcp"


def test_capabilities_endpoint():
    body = client.get("/api/capabilities").json()
    assert body["success"] is True
    assert body["ports"]["frontend"] == 10758
    assert body["ports"]["backend"] == 10759
    assert any(t["name"] == "openbci_trigger" for t in body["tools"])
    assert any(b["key"] == "cyton" for b in body["boards"])
    assert "message" in body


def test_diagnostics_endpoint():
    body = client.get("/api/v1/diagnostics").json()
    assert body["success"] is True
    assert "openbci_shutdown" in body["tools"]
    assert "openbci://boards/capabilities" in body["resources"]
    assert body["system"]["platform"]


def test_skills_endpoint_lists_openbci():
    body = client.get("/api/skills").json()
    assert body["success"] is True
    assert any(s["name"] == "openbci" for s in body["skills"])


def test_shutdown_route_registered_without_firing():
    paths = {(getattr(r, "path", None), tuple(getattr(r, "methods", None) or ())) for r in app.routes}
    assert ("/api/shutdown", ("POST",)) in paths


@pytest.mark.asyncio
async def test_shutdown_tool_registered():
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert "openbci_shutdown" in names
    assert {"openbci_board", "openbci_stream", "openbci_signal", "openbci_export", "openbci_trigger"} <= names


@pytest.mark.asyncio
async def test_capabilities_resource_registered():
    resources = await mcp.list_resources()
    uris = {str(getattr(r, "uri", r)) for r in resources}
    assert "openbci://boards/capabilities" in uris
