import pytest

from openbci_mcp.trigger_engine import TriggerEngine, get_trigger_engine


@pytest.fixture(autouse=True)
def _reset_triggers(tmp_path, monkeypatch) -> None:
    path = tmp_path / "triggers.json"
    monkeypatch.setenv("OPENBCI_TRIGGERS_FILE", str(path))
    TriggerEngine._instance = None
    get_trigger_engine()


def test_add_and_list_rule() -> None:
    engine = get_trigger_engine()
    engine.add_rule(
        name="test",
        channel="*",
        band="beta",
        operator="gt",
        threshold=0.1,
        osc_address="/bci/test",
    )
    rules = engine.list_rules()
    assert len(rules) == 1
    assert rules[0]["name"] == "test"


def test_evaluate_fires_osc(monkeypatch) -> None:
    sent: list[tuple] = []

    def fake_send(host, port, address, values=None):
        sent.append((host, port, address, values))
        return {"success": True}

    monkeypatch.setattr("openbci_mcp.trigger_engine.send_osc", fake_send)
    engine = get_trigger_engine()
    engine.add_rule(
        name="beta",
        channel="CH1",
        band="beta",
        operator="gt",
        threshold=0.01,
        hold_seconds=0,
        osc_address="/bci/focus",
    )
    fired = engine.evaluate_bands({"CH1": {"beta": 1.0, "alpha": 0.1}})
    assert len(fired) == 1
    assert sent[0][2] == "/bci/focus"
