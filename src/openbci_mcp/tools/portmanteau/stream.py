"""OpenBCI streaming portmanteau."""

from __future__ import annotations

import logging
from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.mcp_app import mcp

logger = logging.getLogger(__name__)


def _err(message: str) -> ToolResult:
    return ToolResult(content={"success": False, "error": message, "message": message}, is_error=True)


def _ok(message: str, result: dict[str, Any]) -> ToolResult:
    return ToolResult(content={**result, "message": message})


@mcp.tool(version="1.0.0")
async def openbci_stream(
    operation: Annotated[
        Literal["start", "stop", "snapshot", "marker"],
        Field(description="Stream control operation."),
    ],
    max_samples: Annotated[int, Field(description="Max samples for snapshot", ge=8, le=5000)] = 250,
    marker: Annotated[str | None, Field(description="Event marker string for marker operation")] = None,
    buffer_size: Annotated[int, Field(description="BrainFlow ring buffer size")] = 450000,
) -> ToolResult:
    """
    Control EEG data streaming from a connected OpenBCI board.

    OPERATIONS:
    - start: Begin streaming samples into BrainFlow buffer.
    - stop: Stop streaming (session stays connected).
    - snapshot: Return latest EEG samples per channel (requires active stream).
    - marker: Insert timestamped marker into stream (P300/speller experiments).

    ## Return Format
    ``{"success": bool, "message": str, ...operation payload}``.

    ## Examples
    ``openbci_stream(operation="start")`` -> streaming begins.
    ``openbci_stream(operation="snapshot", max_samples=128)`` -> latest EEG frames.
    ``openbci_stream(operation="marker", marker="stimulus/on")`` -> event marked.
    """
    mgr = get_board_manager()
    try:
        if operation == "start":
            return _ok("Stream started", mgr.start_stream(buffer_size=buffer_size))
        if operation == "stop":
            return _ok("Stream stopped", mgr.stop_stream())
        if operation == "marker":
            if not marker:
                return _err("marker text is required")
            return _ok(f"Marker {marker!r} inserted", mgr.insert_marker(marker))
        if operation == "snapshot":
            result = mgr.get_board_data(max_samples=max_samples)
            n = result.get("samples", max_samples)
            return _ok(f"Snapshot: {n} samples", result)
        return _err(f"Unknown operation {operation!r}")
    except Exception as exc:
        logger.exception("openbci_stream failed")
        return _err(str(exc))
