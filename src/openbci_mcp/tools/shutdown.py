"""Self-termination tool (fleet Phase 1B row 119)."""

from __future__ import annotations

import os
import threading
from typing import Annotated

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.mcp_app import mcp


def _exit_later(delay_ms: int) -> None:
    threading.Timer(delay_ms / 1000.0, lambda: os._exit(0)).start()


@mcp.tool(version="1.0.0")
async def openbci_shutdown(
    grace_ms: Annotated[
        int, Field(description="Delay before exit (ms) so the response flushes.", ge=0, le=10000)
    ] = 500,
) -> ToolResult:
    """
    Shut down the openbci-mcp server process gracefully.

    Responds first, then exits the process after ``grace_ms`` so in-flight
    writes (trigger rules, activity log) can flush.

    ## Return Format
    ``{"success": true, "message": str, "grace_ms": int}``

    ## Examples
    ``openbci_shutdown()`` -> ``{"success": True, "message": "exiting in 500 ms", ...}``
    ``openbci_shutdown(grace_ms=2000)`` -> slower exit for mid-write jobs.
    """
    _exit_later(grace_ms)
    return ToolResult(
        content={
            "success": True,
            "message": f"openbci-mcp exiting in {grace_ms} ms",
            "grace_ms": grace_ms,
        }
    )
