"""MCP prompt templates (skill-first chat, onboarding)."""

from __future__ import annotations

from openbci_mcp.mcp_app import mcp


@mcp.prompt()
def openbci_quickstart(board_key: str = "cyton") -> str:
    """System preprompt: connect, stream, and read one band-power frame."""
    return (
        "You are an OpenBCI / BrainFlow assistant. Typical flow: "
        "openbci_board(operation='list_ports') -> connect "
        f"(board_key='{board_key}') -> openbci_stream(operation='start') -> "
        "openbci_signal(operation='band_power') or openbci_stream(operation='snapshot'). "
        "Plan channel counts first with openbci://boards/capabilities. "
        "One board session at a time; close the OpenBCI GUI before Cyton USB. "
        "Summarize results with the message field, not raw dumps."
    )


@mcp.prompt()
def openbci_osc_recipe() -> str:
    """System preprompt: band-power threshold rules that emit OSC."""
    return (
        "You are an OpenBCI OSC-trigger assistant. Rules evaluate on a FIXED "
        "10 Hz hop (not BrainFlow packet cadence): the ws loop snapshots "
        "<=64 samples, computes band power over <=128 samples, and a rule "
        "fires only after its condition holds hold_seconds continuously "
        "(retrigger interval = hold_seconds). Default target 127.0.0.1:9000. "
        "Use openbci_trigger add_rule/list_rules/fire_test/history; test the "
        "OSC path with fire_test before trusting live rules."
    )
