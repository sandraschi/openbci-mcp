"""Fleet-standard /api/logs routes."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from openbci_mcp.activity_log import (
    SortOrder,
    clear_logs,
    export_logs,
    log_activity,
    log_stats,
    query_logs,
)


def _sort_order(value: str | None) -> SortOrder:
    return "asc" if value == "asc" else "desc"


async def api_logs_query(request: Request) -> JSONResponse:
    params = request.query_params
    limit = max(1, min(int(params.get("limit", "50")), 500))
    offset = max(0, int(params.get("offset", "0")))
    return JSONResponse(
        query_logs(
            limit=limit,
            offset=offset,
            level=params.get("level"),
            kind=params.get("kind"),
            search=params.get("search"),
            sort=_sort_order(params.get("sort")),
            after_id=params.get("after_id"),
        )
    )


async def api_logs_stats(_: Request) -> JSONResponse:
    return JSONResponse(log_stats())


async def api_logs_export(request: Request) -> Response:
    params = request.query_params
    fmt = params.get("format", "json")
    if fmt not in ("json", "csv"):
        fmt = "json"
    body, media_type, filename = export_logs(
        format=fmt,
        level=params.get("level"),
        kind=params.get("kind"),
        search=params.get("search"),
        sort=_sort_order(params.get("sort")),
    )
    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def api_logs_clear(_: Request) -> JSONResponse:
    clear_logs()
    log_activity("system", "Log buffer cleared", level="WARNING")
    return JSONResponse({"success": True})
