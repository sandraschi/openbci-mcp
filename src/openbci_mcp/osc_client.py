"""Minimal OSC UDP client for BCI trigger output."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from pythonosc.udp_client import SimpleUDPClient

    HAS_PYTHON_OSC = True
except ImportError:  # pragma: no cover
    HAS_PYTHON_OSC = False
    SimpleUDPClient = None  # type: ignore[misc, assignment]


def send_osc(host: str, port: int, address: str, values: list[Any] | None = None) -> dict[str, Any]:
    if not HAS_PYTHON_OSC:
        raise RuntimeError("python-osc is not installed. Run: uv sync")
    if not address.startswith("/"):
        address = f"/{address}"
    client = SimpleUDPClient(host, int(port))
    payload = values if values is not None else []
    client.send_message(address, payload)
    logger.info("OSC sent %s:%s %s %s", host, port, address, payload)
    return {
        "success": True,
        "host": host,
        "port": port,
        "address": address,
        "values": payload,
    }
