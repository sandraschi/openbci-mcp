"""OpenBCI board connection portmanteau."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.mcp_app import mcp


def _err(message: str, *, code: str = "OPENBCI_ERROR", suggestions: list[str] | None = None) -> ToolResult:
    return ToolResult(
        content={
            "success": False,
            "error": message,
            "error_code": code,
            "suggestions": suggestions or [],
        },
        is_error=True,
    )


@mcp.tool(version="1.0.0")
async def openbci_board(
    operation: Annotated[
        Literal["connect", "disconnect", "status", "list_ports", "list_boards", "probe"],
        Field(description="Board lifecycle operation."),
    ],
    board_key: Annotated[
        str | None,
        Field(description="Board type: cyton, ganglion, cyton_daisy, galea, synthetic, streaming"),
    ] = None,
    serial_port: Annotated[str | None, Field(description="Serial port for Cyton/Galea, e.g. COM3")] = None,
    mac_address: Annotated[str | None, Field(description="BLE MAC for Ganglion")] = None,
    ip_address: Annotated[str | None, Field(description="Multicast IP for streaming board")] = None,
    ip_port: Annotated[int | None, Field(description="Multicast port for streaming board")] = None,
    master_board_key: Annotated[
        str | None, Field(description="Master board when using streaming mode")
    ] = None,
) -> ToolResult:
    """
    Manage OpenBCI hardware connections via BrainFlow.

    OPERATIONS:
    - connect: Open session to Cyton, Ganglion, Galea, synthetic, or streaming board.
    - disconnect: Release session and stop streams.
    - status: Current connection and channel metadata.
    - list_ports: Enumerate serial COM ports (Windows/macOS/Linux).
    - list_boards: Supported board keys and BrainFlow IDs.
    - probe: Quick synthetic-board smoke test.
    """
    mgr = get_board_manager()
    try:
        if operation == "list_boards":
            return ToolResult(content={"success": True, "boards": mgr.supported_boards()})
        if operation == "list_ports":
            return ToolResult(content={"success": True, "ports": mgr.list_serial_ports()})
        if operation == "status":
            return ToolResult(content=mgr.status_dict())
        if operation == "probe":
            key = board_key or "synthetic"
            return ToolResult(content=mgr.probe(board_key=key))
        if operation == "disconnect":
            return ToolResult(content=mgr.disconnect())
        if operation == "connect":
            if not board_key:
                return _err(
                    "board_key is required for connect",
                    code="MISSING_BOARD_KEY",
                    suggestions=["Use operation=list_boards", "Cyton default: board_key='cyton', serial_port='COM3'"],
                )
            result = mgr.connect(
                board_key=board_key,
                serial_port=serial_port,
                mac_address=mac_address,
                ip_address=ip_address,
                ip_port=ip_port,
                master_board_key=master_board_key,
            )
            return ToolResult(content=result)
        return _err(f"Unknown operation {operation!r}")
    except Exception as exc:
        return _err(str(exc), suggestions=["Check serial port, drivers, and OpenBCI GUI is closed if using USB"])
