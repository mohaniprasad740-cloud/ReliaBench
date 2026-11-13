import sys
import pytest
from app.adapters.agents.real_adapters import HttpAgentAdapter, CliAgentAdapter


def test_cli_adapter_probe_success():
    # Use sys.executable to ensure probe works portably on both Windows and Linux
    adapter = CliAgentAdapter(command_path=sys.executable)
    res = adapter.probe()
    assert res.status == "VALIDATED"
    assert "Python" in res.message or "3." in res.message


def test_cli_adapter_probe_missing_binary():
    adapter = CliAgentAdapter(command_path="nonexistent_binary_xyz_123")
    res = adapter.probe()
    assert res.status == "UNAVAILABLE"
    assert "not found" in res.message.lower()


def test_http_adapter_probe_unreachable():
    # Probing an invalid host should return ERROR, never faking VALIDATED
    adapter = HttpAgentAdapter(endpoint_url="http://127.0.0.1:59999", timeout_seconds=0.5)
    res = adapter.probe()
    assert res.status in ["ERROR", "UNAVAILABLE"]
    assert res.latency_ms >= 0.0
