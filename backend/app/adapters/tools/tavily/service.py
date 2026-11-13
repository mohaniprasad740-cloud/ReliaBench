from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from app.adapters.tools.tavily.client import TavilyClient
from app.adapters.tools.tavily.schemas import TavilySearchRequest, TavilySearchResponse, TavilyTelemetryEvent


class TavilyService:
    """Service wrapping Tavily client with telemetry capture and tool definition formatting."""

    def __init__(self, client: Optional[TavilyClient] = None):
        self.client = client or TavilyClient()
        self._telemetry_store: List[TavilyTelemetryEvent] = []

    def get_status(self) -> Dict[str, Any]:
        has_key = bool(self.client.api_key and self.client.api_key.strip())
        return {
            "name": "Tavily Web Search",
            "configured": has_key,
            "status": "READY" if has_key else "NOT_CONFIGURED",
            "api_base": self.client.api_base,
            "timeout_seconds": self.client.timeout,
            "has_credentials": has_key,
            "total_events_captured": len(self._telemetry_store),
        }

    def execute_search_tool(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        tool_call_id: Optional[str] = None,
        experiment_id: Optional[str] = None,
        run_id: Optional[str] = None,
        trial_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Callable tool interface for agents to execute real web research."""
        req = TavilySearchRequest(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
        )

        resp = self.client.search(req)

        # Extract domains
        domains = []
        for r in resp.results:
            try:
                domain = urlparse(r.url).netloc
                if domain:
                    domains.append(domain)
            except Exception:
                pass

        # Record telemetry event
        event = TavilyTelemetryEvent(
            event_id=str(uuid.uuid4()),
            tool_call_id=tool_call_id,
            experiment_id=experiment_id,
            run_id=run_id,
            trial_id=trial_id,
            agent_id=agent_id,
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            domains_included=include_domains,
            result_count=len(resp.results),
            domains_returned=domains,
            latency_ms=resp.response_time,
            http_status=resp.status_code,
            is_error=resp.is_error,
            error_category=resp.error_category,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        self._telemetry_store.append(event)

        # Return standardized agent tool response
        if resp.is_error:
            return {
                "success": False,
                "error": resp.error_message,
                "error_category": resp.error_category,
                "status_code": resp.status_code,
                "latency_ms": resp.response_time,
                "results": [],
            }

        return {
            "success": True,
            "query": resp.query,
            "results_count": len(resp.results),
            "latency_ms": resp.response_time,
            "results": [
                {
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.content,
                    "score": r.score,
                    "published_date": r.published_date,
                }
                for r in resp.results
            ],
            "answer": resp.answer,
        }

    def list_telemetry(self, trial_id: Optional[str] = None) -> List[TavilyTelemetryEvent]:
        if trial_id:
            return [e for e in self._telemetry_store if e.trial_id == trial_id]
        return list(self._telemetry_store)


tavily_service = TavilyService()
