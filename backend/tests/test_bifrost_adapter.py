import pytest
from app.adapters.gateways.bifrost import BifrostClient, BifrostAdapter


def test_bifrost_client_disabled_by_default():
    client = BifrostClient(enabled=False)
    assert not client.enabled
    res = client.chat([{"role": "user", "content": "hello"}])
    assert res.mode == "MOCK"
    assert res.fallback_used is True
    assert res.provider == "stub-gateway"
    assert res.prompt_tokens > 0
    assert res.correlation_id is not None


def test_bifrost_health_check_disabled():
    adapter = BifrostAdapter(enabled=False)
    status = adapter.get_status()
    assert status["status"] == "DISABLED"
    assert status["mode"] == "MOCK"


def test_bifrost_chat_with_correlation_headers(monkeypatch):
    client = BifrostClient(endpoint="http://mock-bifrost:8080/v1", enabled=True)

    captured_headers = {}

    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "id": "chatcmpl-test-123",
                "choices": [{"message": {"content": "Hello from Bifrost!"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 8},
                "cost_usd": 0.000045,
            }

    def mock_post(self, url, json=None, headers=None, **kwargs):
        captured_headers.update(headers or {})
        return MockResponse()

    monkeypatch.setattr("httpx.Client.post", mock_post)

    res = client.chat(
        messages=[{"role": "user", "content": "Hi"}],
        model="gpt-4o",
        experiment_id="exp-1",
        run_id="run-1",
        trial_id="trial-1",
        agent_id="agent-1",
    )

    assert res.mode == "GATEWAY"
    assert res.fallback_used is False
    assert res.content == "Hello from Bifrost!"
    assert res.cost_usd == 0.000045
    assert captured_headers.get("x-bf-lh-experiment-id") == "exp-1"
    assert captured_headers.get("x-bf-lh-trial-id") == "trial-1"
    assert captured_headers.get("x-bf-lh-correlation-id") == res.correlation_id
