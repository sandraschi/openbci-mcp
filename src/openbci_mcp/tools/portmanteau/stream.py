"""OpenBCI streaming portmanteau."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.mcp_app import mcp


def _err(message: str) -> ToolResult:
    return ToolResult(content={"success": False, "error": message}, is_error=True)


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
    """
    mgr = get_board_manager()
    try:
        if operation == "start":
            return ToolResult(content=mgr.start_stream(buffer_size=buffer_size))
        if operation == "stop":
            return ToolResult(content=mgr.stop_stream())
        if operation == "marker":
            if not marker:
                return _err("marker text is required")
            return ToolResult(content=mgr.insert_marker(marker))
        if operation == "snapshot":
            return ToolResult(content=mgr.get_board_data(max_samples=max_samples))
        return _err(f"Unknown operation {operation!r}")
    except Exception as exc:
        return _err(str(exc))
