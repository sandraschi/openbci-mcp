"""OpenBCI board connection portmanteau."""

from __future__ import annotations

import logging
from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.mcp_app import mcp

logger = logging.getLogger(__name__)


def _err(message: str, *, code: str = "OPENBCI_ERROR", suggestions: list[str] | None = None) -> ToolResult:
    return ToolResult(
        content={
            "success": False,
            "error": message,
            "message": message,
            "error_code": code,
            "suggestions": suggestions or [],
        },
        is_error=True,
    )


def _ok(message: str, result: dict[str, Any]) -> ToolResult:
    return ToolResult(content={**result, "message": message})


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
    master_board_key: Annotated[str | None, Field(description="Master board when using streaming mode")] = None,
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

    ## Return Format
    ``{"success": bool, "message": str, ...operation payload}`` — every
    response carries a human-readable ``message``; failures add ``error``,
    ``error_code``, and ``suggestions``.

    ## Examples
    ``openbci_board(operation="list_ports")`` -> COM ports for Cyton dongle.
    ``openbci_board(operation="list_boards")`` -> supported keys + BrainFlow IDs.
    ``openbci_board(operation="connect", board_key="cyton", serial_port="COM3")`` -> session open.
    ``openbci_board(operation="probe", board_key="synthetic")`` -> hardware-free smoke test.
    """
    mgr = get_board_manager()
    try:
        if operation == "list_boards":
            boards = mgr.supported_boards()
            return _ok(f"{len(boards)} boards supported", {"success": True, "boards": boards})
        if operation == "list_ports":
            ports = mgr.list_serial_ports()
            return _ok(f"{len(ports)} serial ports", {"success": True, "ports": ports})
        if operation == "status":
            return _ok("Board status", mgr.status_dict())
        if operation == "probe":
            key = board_key or "synthetic"
            return _ok(f"Probe on {key}", mgr.probe(board_key=key))
        if operation == "disconnect":
            return _ok("Board disconnected", mgr.disconnect())
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
            if not result.get("success", True):
                return _err(
                    str(result.get("error", "connect failed")),
                    suggestions=["Check serial port, drivers, and OpenBCI GUI is closed if using USB"],
                )
            return _ok(f"Connected to {board_key}", result)
        return _err(f"Unknown operation {operation!r}")
    except Exception as exc:
        logger.exception("openbci_board failed")
        return _err(str(exc), suggestions=["Check serial port, drivers, and OpenBCI GUI is closed if using USB"])
