"""OpenBCI data export portmanteau."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.mcp_app import mcp


def _err(message: str) -> ToolResult:
    return ToolResult(content={"success": False, "error": message}, is_error=True)


@mcp.tool(version="1.0.0")
async def openbci_export(
    operation: Annotated[
        Literal["streamer_add", "streamer_file", "streamer_multicast"],
        Field(description="Export/stream routing operation."),
    ],
    file_path: Annotated[str | None, Field(description="Local CSV path for file streamer")] = None,
    ip_address: Annotated[str, Field(description="Multicast or LSL target address")] = "225.1.1.1",
    ip_port: Annotated[int, Field(description="Multicast port")] = 6677,
    streamer_params: Annotated[str | None, Field(description="Raw BrainFlow streamer string (advanced)")] = None,
) -> ToolResult:
    """
    Route live EEG to external consumers via BrainFlow streamers.

    OPERATIONS:
    - streamer_add: Pass raw BrainFlow streamer params (see BrainFlow docs).
    - streamer_file: Record to CSV via file:// streamer.
    - streamer_multicast: Forward to multicast for OpenBCI GUI / custom listeners.

    Examples (BrainFlow streamer syntax):
    - file://C:/recordings/session.csv
    - streaming_board://225.1.1.1:6677
    """
    mgr = get_board_manager()
    try:
        if operation == "streamer_add":
            if not streamer_params:
                return _err("streamer_params is required for streamer_add")
            return ToolResult(content=mgr.add_streamer(streamer_params))
        if operation == "streamer_file":
            if not file_path:
                return _err("file_path is required for streamer_file")
            uri = file_path if file_path.startswith("file://") else f"file://{file_path}"
            return ToolResult(content=mgr.add_streamer(uri))
        if operation == "streamer_multicast":
            uri = f"streaming_board://{ip_address}:{ip_port}"
            return ToolResult(content=mgr.add_streamer(uri))
        return _err(f"Unknown operation {operation!r}")
    except Exception as exc:
        return _err(str(exc))
