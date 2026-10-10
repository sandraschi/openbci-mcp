"""MCP resources: machine-readable board capabilities (issue #1).

Agents previously had to infer channel counts, transports, and units from
``openbci_board(operation='list_boards')``. This resource exposes the same
catalog enriched with established BrainFlow defaults so clients can plan
*before* ``connect``. Fields that vary by firmware/setup are ``null`` with a
note to read them from ``openbci_board(operation='status')`` after connect —
never invented.
"""

from __future__ import annotations

from typing import Any

from openbci_mcp.board_manager import SUPPORTED_BOARDS
from openbci_mcp.mcp_app import mcp

# Established BrainFlow defaults (board shim constants + docs). Galea fields
# that depend on configuration are null — read live status after connect.
_BOARD_FACTS: dict[str, dict[str, Any]] = {
    "cyton": {
        "eeg_channels": 8,
        "sampling_rate_hz": 250,
        "transport": "serial",
        "units": "microvolts",
    },
    "ganglion": {
        "eeg_channels": 4,
        "sampling_rate_hz": 200,
        "transport": "ble",
        "units": "microvolts",
    },
    "cyton_daisy": {
        "eeg_channels": 16,
        "sampling_rate_hz": 125,
        "transport": "serial",
        "units": "microvolts",
    },
    "galea": {
        "eeg_channels": None,
        "sampling_rate_hz": None,
        "transport": "serial",
        "units": "microvolts",
        "note": "Multimodal headest — read eeg_channel_names/sampling_rate from status after connect.",
    },
    "synthetic": {
        "eeg_channels": 8,
        "sampling_rate_hz": 250,
        "transport": "none",
        "units": "microvolts",
        "note": "Safe dev/test board, no hardware.",
    },
    "streaming": {
        "eeg_channels": None,
        "sampling_rate_hz": None,
        "transport": "udp",
        "units": "microvolts",
        "note": "Mirrors the master board — read channels/rate from status after connect.",
    },
}


@mcp.resource(
    "openbci://boards/capabilities",
    name="openbci-board-capabilities",
    description="Board catalog: BrainFlow board id, channel count, transport, units, sampling rate.",
    mime_type="application/json",
)
def board_capabilities() -> dict[str, Any]:
    """Return the enriched board capability catalog as JSON."""
    boards: list[dict[str, Any]] = []
    for key, base in SUPPORTED_BOARDS.items():
        facts = _BOARD_FACTS.get(key, {})
        boards.append(
            {
                "key": key,
                "board_id": base.get("board_id"),
                "label": base.get("label"),
                "connection": base.get("connection"),
                "eeg_channels": facts.get("eeg_channels"),
                "sampling_rate_hz": facts.get("sampling_rate_hz"),
                "transport": facts.get("transport", base.get("connection")),
                "units": facts.get("units", "microvolts"),
                **({"note": facts["note"]} if "note" in facts else {}),
            }
        )
    return {"success": True, "boards": boards}
