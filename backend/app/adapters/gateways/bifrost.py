from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import httpx

from app.core.config import settings


class GatewayChatResponse(BaseModel):
    id: str
    provider: str
    model: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: Optional[float] = None  # None if unmeasured/unavailable
    latency_ms: float
    fallback_used: bool = False
    retry_count: int = 0
    mode: str = "MOCK"  # GATEWAY or MOCK
    correlation_id: Optional[str] = None


class GatewayTelemetryEvent(BaseModel):
    request_id: str
    experiment_id: Optional[str] = None
    run_id: Optional[str] = None
    trial_id: Optional[str] = None
    agent_id: Optional[str] = None
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: Optional[float] = None
    latency_ms: float
    status_code: int = 200
    fallback_used: bool = False
    retry_count: int = 0
    timestamp: str


class BifrostClient:
    """Client for Maxim Bifrost / OpenAI-compatible model gateway.

    Routes model calls, measures latency, calculates token usage, and
    performs cost and fallback attribution using x-bf-lh-* correlation headers.
    If not configured or unreachable, degrades cleanly to a clearly labelled local stub (mode=MOCK, fallback_used=True).
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        admin_api_key: Optional[str] = None,
        enabled: Optional[bool] = None,
        timeout_seconds: Optional[float] = None,
    ):
        self.endpoint = (endpoint or getattr(settings, "BIFROST_ENDPOINT", "http://localhost:8080/v1")).rstrip("/")
        self.api_key = api_key or getattr(settings, "BIFROST_API_KEY", "")
        self.admin_api_key = admin_api_key or getattr(settings, "BIFROST_ADMIN_API_KEY", "")
        self.enabled = enabled if enabled is not None else getattr(settings, "ENABLE_BIFROST_GATEWAY", False)
        self.timeout = timeout_seconds or getattr(settings, "BIFROST_REQUEST_TIMEOUT", 10.0)
        self._telemetry_store: List[GatewayTelemetryEvent] = []

    def check_health(self) -> Dict[str, Any]:
        """Checks gateway reachability and operational readiness."""
        if not self.enabled:
            return {
                "configured": False,
                "status": "DISABLED",
                "endpoint": self.endpoint,
                "mode": "MOCK",
                "message": "Bifrost Gateway disabled. Running in local stub mode (mode=MOCK, fallback_used=True).",
            }

        start = time.perf_counter()
        try:
            with httpx.Client(timeout=3.0) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                res = client.get(f"{self.endpoint}/models", headers=headers)
                latency = round((time.perf_counter() - start) * 1000, 2)
                if res.status_code == 200:
                    return {
                        "configured": True,
                        "status": "READY",
                        "endpoint": self.endpoint,
                        "mode": "GATEWAY",
                        "latency_ms": latency,
                        "message": "Bifrost gateway reachable and healthy.",
                    }
                return {
                    "configured": True,
                    "status": "ERROR",
                    "endpoint": self.endpoint,
                    "mode": "GATEWAY",
                    "status_code": res.status_code,
                    "latency_ms": latency,
                    "message": f"Gateway responded with HTTP {res.status_code}.",
                }
        except Exception as ex:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "configured": True,
                "status": "UNREACHABLE",
                "endpoint": self.endpoint,
                "mode": "GATEWAY",
                "latency_ms": latency,
                "message": f"Gateway unreachable: {str(ex)}",
            }

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        allow_fallback: bool = True,
        experiment_id: Optional[str] = None,
        run_id: Optional[str] = None,
        trial_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> GatewayChatResponse:
        start = time.perf_counter()
        correlation_id = str(uuid.uuid4())

        # If gateway is disabled or not configured, return labeled stub
        if not self.enabled or not self.endpoint:
            elapsed_ms = round((time.perf_counter() - start) * 1000 + 45.0, 2)
            prompt_toks = sum(len(m.get("content", "")) // 4 for m in messages) + 120
            completion_toks = 65
            total_toks = prompt_toks + completion_toks
            cost = round((prompt_toks * 0.00000015) + (completion_toks * 0.00000060), 6)

            resp = GatewayChatResponse(
                id=f"mock-bifrost-{correlation_id[:8]}",
                provider="stub-gateway",
                model=model,
                content="Executed successfully via local fallback stub.",
                prompt_tokens=prompt_toks,
                completion_tokens=completion_toks,
                total_tokens=total_toks,
                cost_usd=cost,
                latency_ms=elapsed_ms,
                fallback_used=True,
                mode="MOCK",
                correlation_id=correlation_id,
            )
            return resp

        # In production mode when endpoint is active, we attempt gateway call with correlation headers
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "x-bf-lh-correlation-id": correlation_id,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if experiment_id:
            headers["x-bf-lh-experiment-id"] = experiment_id
        if run_id:
            headers["x-bf-lh-run-id"] = run_id
        if trial_id:
            headers["x-bf-lh-trial-id"] = trial_id
        if agent_id:
            headers["x-bf-lh-agent-id"] = agent_id

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(
                    f"{self.endpoint}/chat/completions",
                    json={"model": model, "messages": messages, "temperature": temperature},
                    headers=headers,
                )
                if res.status_code == 200:
                    data = res.json()
                    usage = data.get("usage", {})
                    p_tok = usage.get("prompt_tokens", 100)
                    c_tok = usage.get("completion_tokens", 50)
                    # Cost is only set if gateway reports it or can be determined
                    cost = data.get("cost_usd")
                    if cost is None and "cost" in data:
                        cost = float(data["cost"])

                    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
                    chat_res = GatewayChatResponse(
                        id=data.get("id", f"gw-{correlation_id[:8]}"),
                        provider="bifrost",
                        model=model,
                        content=data["choices"][0]["message"]["content"],
                        prompt_tokens=p_tok,
                        completion_tokens=c_tok,
                        total_tokens=p_tok + c_tok,
                        cost_usd=cost,
                        latency_ms=elapsed_ms,
                        fallback_used=False,
                        mode="GATEWAY",
                        correlation_id=correlation_id,
                    )
                    return chat_res
        except Exception:
            pass

        # Fallback if call fails
        elapsed_ms = round((time.perf_counter() - start) * 1000 + 50.0, 2)
        prompt_toks = sum(len(m.get("content", "")) // 4 for m in messages) + 120
        completion_toks = 50
        return GatewayChatResponse(
            id=f"mock-bifrost-fallback-{correlation_id[:8]}",
            provider="stub-gateway",
            model=model,
            content="Degraded to local fallback stub due to gateway timeout.",
            prompt_tokens=prompt_toks,
            completion_tokens=completion_toks,
            total_tokens=prompt_toks + completion_toks,
            cost_usd=None,
            latency_ms=elapsed_ms,
            fallback_used=True,
            mode="MOCK",
            correlation_id=correlation_id,
        )


class BifrostAdapter:
    """Adapter for Maxim Bifrost Model Gateway (OpenAI-compatible)."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):
        self.endpoint = endpoint or settings.BIFROST_ENDPOINT
        self.enabled = enabled if enabled is not None else settings.ENABLE_BIFROST_GATEWAY
        self.client = BifrostClient(endpoint=self.endpoint, enabled=self.enabled)

    def get_status(self) -> Dict[str, Any]:
        return self.client.check_health()
