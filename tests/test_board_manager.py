"""Board manager tests (synthetic board)."""

from __future__ import annotations

import pytest

from openbci_mcp.board_manager import get_board_manager


@pytest.fixture(autouse=True)
def _reset_manager() -> None:
    mgr = get_board_manager()
    mgr.disconnect()


def test_supported_boards() -> None:
    mgr = get_board_manager()
    boards = mgr.supported_boards()
    keys = {b["key"] for b in boards}
    assert "cyton" in keys
    assert "synthetic" in keys


def test_synthetic_probe() -> None:
    mgr = get_board_manager()
    result = mgr.probe(board_key="synthetic")
    assert result.get("success") is True
