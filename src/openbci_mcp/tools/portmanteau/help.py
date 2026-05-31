"""OpenBCI help / discovery portmanteau."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.mcp_app import mcp

TOOL_CATALOG = [
    {
        "name": "openbci_board",
        "operations": ["connect", "disconnect", "status", "list_ports", "list_boards", "probe"],
        "description": "Hardware connection lifecycle",
    },
    {
        "name": "openbci_stream",
        "operations": ["start", "stop", "snapshot", "marker"],
        "description": "Live EEG buffer control",
    },
    {
        "name": "openbci_signal",
        "operations": ["band_power", "filter"],
        "description": "Filters and frequency metrics",
    },
    {
        "name": "openbci_export",
        "operations": ["streamer_add", "streamer_file", "streamer_multicast"],
        "description": "BrainFlow streamer routing",
    },
    {
        "name": "openbci_help",
        "operations": ["overview", "quickstart", "ports"],
        "description": "This help tool",
    },
]


@mcp.tool(version="1.0.0", app=True)
async def openbci_help(
    operation: Annotated[
        Literal["overview", "quickstart", "ports"],
        Field(description="Help section to display."),
    ] = "overview",
) -> ToolResult:
    """
    Discovery and usage guide for openbci-mcp.

    OPERATIONS:
    - overview: Tool catalog and board keys.
    - quickstart: Typical Cyton USB workflow.
    - ports: Fleet port assignments.
    """
    if operation == "ports":
        text = (
            "# openbci-mcp Ports\n\n"
            "- Backend (REST + MCP HTTP): 10759\n"
            "- Frontend (Vite dashboard): 10758\n"
            "- MCP endpoint: http://127.0.0.1:10759/mcp\n"
        )
        return ToolResult(content={"success": True, "markdown": text, "tools": TOOL_CATALOG})

    if operation == "quickstart":
        text = (
            "# OpenBCI Cyton Quickstart\n\n"
            "1. `openbci_board(operation='list_ports')` - find COM port\n"
            "2. `openbci_board(operation='connect', board_key='cyton', serial_port='COM3')`\n"
            "3. `openbci_stream(operation='start')`\n"
            "4. `openbci_stream(operation='snapshot')` or `openbci_signal(operation='band_power')`\n"
            "5. `openbci_export(operation='streamer_multicast')` for GUI bridge\n"
            "6. `openbci_board(operation='disconnect')` when done\n"
        )
        return ToolResult(content={"success": True, "markdown": text})

    text = (
        "# openbci-mcp\n\n"
        "BrainFlow-backed MCP server for OpenBCI Cyton, Ganglion, Galea, synthetic, and streaming boards.\n\n"
        "## Tools\n"
        + "\n".join(f"- **{t['name']}**: {t['description']} ({', '.join(t['operations'])})" for t in TOOL_CATALOG)
        + "\n\n## Env\n"
        "- OPENBCI_SERIAL_PORT, OPENBCI_BOARD_ID, OPENBCI_MCP_PORT\n"
    )
    return ToolResult(content={"success": True, "markdown": text, "tools": TOOL_CATALOG})
