"""Settings from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    mcp_http_path: str
    default_board_id: int
    serial_port: str
    mac_address: str
    ip_address: str
    ip_port: int
    probe_on_startup: bool
    osc_host: str
    osc_port: int

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            host=os.getenv("OPENBCI_MCP_HOST", "127.0.0.1"),
            port=int(os.getenv("OPENBCI_MCP_PORT", "10759")),
            mcp_http_path=os.getenv("OPENBCI_MCP_HTTP_PATH", "/mcp"),
            default_board_id=int(os.getenv("OPENBCI_BOARD_ID", "0")),
            serial_port=os.getenv("OPENBCI_SERIAL_PORT", ""),
            mac_address=os.getenv("OPENBCI_MAC_ADDRESS", ""),
            ip_address=os.getenv("OPENBCI_IP_ADDRESS", "225.1.1.1"),
            ip_port=int(os.getenv("OPENBCI_IP_PORT", "6677")),
            probe_on_startup=os.getenv("OPENBCI_PROBE", "0") == "1",
            osc_host=os.getenv("OPENBCI_OSC_HOST", "127.0.0.1"),
            osc_port=int(os.getenv("OPENBCI_OSC_PORT", "9000")),
        )


def load_settings() -> Settings:
    return Settings.from_env()
