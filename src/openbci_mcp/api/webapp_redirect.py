"""Redirect mistaken backend-port browser hits to the Vite dashboard."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import RedirectResponse

WEBAPP_ORIGIN = "http://127.0.0.1:10758"

WEBAPP_PATHS = (
    "/help",
    "/tools",
    "/apps",
    "/chat",
    "/status",
    "/skill",
    "/triggers",
    "/dashboard",
)


async def redirect_to_webapp(request: Request) -> RedirectResponse:
    path = request.url.path
    query = request.url.query
    target = f"{WEBAPP_ORIGIN}{path}"
    if query:
        target = f"{target}?{query}"
    return RedirectResponse(target, status_code=307)
