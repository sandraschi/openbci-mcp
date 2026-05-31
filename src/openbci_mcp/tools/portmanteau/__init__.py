"""Portmanteau tool registration."""

from openbci_mcp.tools.portmanteau.board import openbci_board
from openbci_mcp.tools.portmanteau.export import openbci_export
from openbci_mcp.tools.portmanteau.help import openbci_help
from openbci_mcp.tools.portmanteau.signal import openbci_signal
from openbci_mcp.tools.portmanteau.stream import openbci_stream
from openbci_mcp.tools.portmanteau.trigger import openbci_trigger

__all__ = [
    "openbci_board",
    "openbci_stream",
    "openbci_signal",
    "openbci_export",
    "openbci_trigger",
    "openbci_help",
]
