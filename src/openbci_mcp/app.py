"""REST + MCP HTTP + WebSocket ASGI app."""

from __future__ import annotations

import asyncio
from typing import Any

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.config import load_settings
from openbci_mcp.mcp_app import mcp
from openbci_mcp.tools import portmanteau  # noqa: F401

TOOL_CATALOG = [
    {"name": "openbci_board", "type": "portmanteau", "operations": ["connect", "disconnect", "status", "list_ports", "list_boards", "probe"]},
    {"name": "openbci_stream", "type": "portmanteau", "operations": ["start", "stop", "snapshot", "marker"]},
    {"name": "openbci_signal", "type": "portmanteau", "operations": ["band_power", "filter"]},
    {"name": "openbci_export", "type": "portmanteau", "operations": ["streamer_add", "streamer_file", "streamer_multicast"]},
    {"name": "openbci_help", "type": "portmanteau", "operations": ["overview", "quickstart", "ports"]},
]

mcp_http = mcp.http_app(path="/mcp")


async def health(_: Request) -> JSONResponse:
    settings = load_settings()
    mgr = get_board_manager()
    st = mgr.status_dict()
    return JSONResponse(
        {
            "ok": True,
            "service": "openbci-mcp",
            "version": "0.1.0",
            "port": settings.port,
            "mcp_http": f"http://{settings.host}:{settings.port}{settings.mcp_http_path}",
            "board": st,
        }
    )


async def root(_: Request) -> JSONResponse:
    settings = load_settings()
    return JSONResponse(
        {
            "service": "openbci-mcp",
            "version": "0.1.0",
            "webapp": "http://127.0.0.1:10758",
            "mcp_http": f"http://{settings.host}:{settings.port}{settings.mcp_http_path}",
            "health": f"http://{settings.host}:{settings.port}/health",
        }
    )


async def api_status(_: Request) -> JSONResponse:
    return JSONResponse(get_board_manager().status_dict())


async def api_boards(_: Request) -> JSONResponse:
    mgr = get_board_manager()
    return JSONResponse({"success": True, "boards": mgr.supported_boards(), "ports": mgr.list_serial_ports()})


async def api_tools(_: Request) -> JSONResponse:
    return JSONResponse({"success": True, "tools": TOOL_CATALOG})


async def api_board_action(request: Request) -> JSONResponse:
    try:
        body: dict[str, Any] = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "invalid JSON"}, status_code=400)

    op = body.get("operation")
    mgr = get_board_manager()
    try:
        if op == "connect":
            result = mgr.connect(
                board_key=str(body.get("board_key", "cyton")),
                serial_port=body.get("serial_port"),
                mac_address=body.get("mac_address"),
                ip_address=body.get("ip_address"),
                ip_port=body.get("ip_port"),
                master_board_key=body.get("master_board_key"),
            )
        elif op == "disconnect":
            result = mgr.disconnect()
        elif op == "start_stream":
            result = mgr.start_stream()
        elif op == "stop_stream":
            result = mgr.stop_stream()
        elif op == "band_power":
            result = mgr.band_power(max_samples=int(body.get("max_samples", 256)))
        elif op == "snapshot":
            result = mgr.get_board_data(max_samples=int(body.get("max_samples", 128)))
        else:
            return JSONResponse({"success": False, "error": f"unknown operation {op!r}"}, status_code=400)
        return JSONResponse(result)
    except Exception as exc:
        return JSONResponse({"success": False, "error": str(exc)}, status_code=500)


async def ws_eeg(websocket: WebSocket) -> None:
    await websocket.accept()
    mgr = get_board_manager()
    try:
        while True:
            st = mgr.status_dict()
            if not st.get("streaming"):
                await websocket.send_json({"type": "status", "streaming": False, "connected": st.get("connected")})
            else:
                snap = mgr.get_board_data(max_samples=64)
                bands = mgr.band_power(max_samples=128) if snap.get("samples", 0) >= 32 else {"bands": {}}
                await websocket.send_json(
                    {
                        "type": "frame",
                        "snapshot": snap,
                        "bands": bands.get("bands", {}),
                        "status": st,
                    }
                )
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        return
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "error": str(exc)})
        except Exception:
            pass


async def api_skill(_: Request) -> JSONResponse:
    from pathlib import Path

    skill_path = Path(__file__).resolve().parent / "skills" / "openbci" / "SKILL.md"
    if skill_path.is_file():
        return JSONResponse({"success": True, "skill": skill_path.read_text(encoding="utf-8")})
    return JSONResponse({"success": False, "error": "skill not found"}, status_code=404)


def build_app() -> Starlette:
    settings = load_settings()
    path = settings.mcp_http_path.strip() or "/mcp"
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    return Starlette(
        lifespan=mcp_http.lifespan,
        middleware=middleware,
        routes=[
            Route("/", root),
            Route("/health", health),
            Route("/api/status", api_status),
            Route("/api/boards", api_boards),
            Route("/api/tools", api_tools),
            Route("/api/board", api_board_action, methods=["POST"]),
            Route("/api/skill", api_skill),
            WebSocketRoute("/api/ws/eeg", ws_eeg),
            Mount(path, app=mcp_http),
        ],
    )


app = build_app()
