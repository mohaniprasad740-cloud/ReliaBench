import pytest
from app.adapters.tools.tavily import (
    TavilyClient,
    TavilySearchRequest,
    TavilyService,
    TavilyErrorCategory,
)


def test_tavily_not_configured_returns_safe_error():
    client = TavilyClient(api_key="")
    assert not client.is_configured
    resp = client.search(TavilySearchRequest(query="pytest test"))
    assert resp.is_error
    assert resp.error_category == TavilyErrorCategory.NOT_CONFIGURED.value
    assert resp.status_code == 401


def test_tavily_check_connection_unconfigured():
    client = TavilyClient(api_key="")
    status = client.check_connection()
    assert status["status"] == "NOT_CONFIGURED"
    assert status["configured"] is False


def test_tavily_service_telemetry_capture(monkeypatch):
    client = TavilyClient(api_key="tvly-mock-key")

    # Mock post response
    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "results": [
                    {
                        "title": "Python Docs",
                        "url": "https://docs.python.org/3/library/unittest.html",
                        "content": "Unit testing framework.",
                        "score": 0.98,
                    }
                ]
            }

    monkeypatch.setattr("httpx.Client.post", lambda *args, **kwargs: MockResponse())

    service = TavilyService(client=client)
    res = service.execute_search_tool(
        query="python unit test",
        tool_call_id="call_123",
        trial_id="trial_abc",
    )

    assert res["success"] is True
    assert res["results_count"] == 1
    assert "docs.python.org" in res["results"][0]["url"]

    # Check telemetry stored
    events = service.list_telemetry("trial_abc")
    assert len(events) == 1
    ev = events[0]
    assert ev.query == "python unit test"
    assert "docs.python.org" in ev.domains_returned
    assert ev.http_status == 200
    assert not ev.is_error


def test_tavily_error_classification(monkeypatch):
    client = TavilyClient(api_key="tvly-mock-key")

    class Mock429Response:
        status_code = 429
        text = "Rate limit exceeded"

    monkeypatch.setattr("httpx.Client.post", lambda *args, **kwargs: Mock429Response())

    resp = client.search(TavilySearchRequest(query="test rate limit"))
    assert resp.is_error
    assert resp.error_category == TavilyErrorCategory.RATE_LIMIT.value
    assert resp.status_code == 429
