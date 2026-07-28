"""FastMCP application singleton (no tool imports)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.config import load_settings


@asynccontextmanager
async def lifespan(_: FastMCP) -> AsyncIterator[None]:
    settings = load_settings()
    if settings.probe_on_startup:
        get_board_manager().probe(board_key="synthetic")
    yield


mcp = FastMCP(
    "openbci-mcp",
    instructions=(
        "OpenBCI brain-computer interface server via BrainFlow. "
        "Connect Cyton/Ganglion/Galea hardware, stream EEG, compute band power, "
        "apply filters, and export via BrainFlow streamers. "
        "Tools: openbci_board, openbci_stream, openbci_signal, openbci_export, openbci_help."
    ),
    lifespan=lifespan,
)
