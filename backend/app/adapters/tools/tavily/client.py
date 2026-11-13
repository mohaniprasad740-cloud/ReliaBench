from __future__ import annotations

import time
import urllib.parse
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings
from app.adapters.tools.tavily.errors import TavilyErrorCategory, TavilyException
from app.adapters.tools.tavily.schemas import (
    TavilyExtractRequest,
    TavilyExtractResponse,
    TavilySearchRequest,
    TavilySearchResponse,
    TavilySearchResultItem,
)


class TavilyClient:
    """Official HTTP Client for Tavily Web Research API.
    
    Adheres to https://docs.tavily.com/
    Uses POST /search and POST /extract.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ):
        self.api_key = api_key or getattr(settings, "TAVILY_API_KEY", "")
        self.api_base = (api_base or getattr(settings, "TAVILY_API_BASE", "https://api.tavily.com")).rstrip("/")
        self.timeout = timeout_seconds or getattr(settings, "TAVILY_REQUEST_TIMEOUT", 30.0)

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def check_connection(self) -> Dict[str, Any]:
        """Validates Tavily API key and connectivity without consuming excess search credits."""
        if not self.is_configured:
            return {
                "configured": False,
                "status": "NOT_CONFIGURED",
                "message": "Tavily API key is not configured.",
                "latency_ms": 0.0,
            }

        start = time.perf_counter()
        try:
            # Minimal probe search
            resp = self.search(TavilySearchRequest(query="health check", max_results=1))
            latency = round((time.perf_counter() - start) * 1000, 2)
            if resp.is_error:
                return {
                    "configured": True,
                    "status": "ERROR",
                    "category": resp.error_category,
                    "message": resp.error_message,
                    "latency_ms": latency,
                }
            return {
                "configured": True,
                "status": "READY",
                "message": "Tavily Web Search API reachable and validated.",
                "latency_ms": latency,
                "result_count": len(resp.results),
            }
        except Exception as e:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "configured": True,
                "status": "ERROR",
                "category": TavilyErrorCategory.NETWORK_ERROR.value,
                "message": str(e),
                "latency_ms": latency,
            }

    def search(self, req: TavilySearchRequest) -> TavilySearchResponse:
        """Executes search against POST /search."""
        if not self.is_configured:
            return TavilySearchResponse(
                query=req.query,
                is_error=True,
                status_code=401,
                error_category=TavilyErrorCategory.NOT_CONFIGURED.value,
                error_message="Tavily API key is not configured in environment.",
            )

        payload: Dict[str, Any] = {
            "api_key": self.api_key,
            "query": req.query,
            "search_depth": req.search_depth,
            "topic": req.topic,
            "max_results": req.max_results,
            "include_answer": req.include_answer,
            "include_raw_content": req.include_raw_content,
        }
        if req.include_domains:
            payload["include_domains"] = req.include_domains
        if req.exclude_domains:
            payload["exclude_domains"] = req.exclude_domains
        if req.days is not None:
            payload["days"] = req.days

        start = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.api_base}/search", json=payload)
                latency = round((time.perf_counter() - start) * 1000, 2)

                if res.status_code == 200:
                    data = res.json()
                    items = [
                        TavilySearchResultItem(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            content=item.get("content", ""),
                            score=float(item.get("score", 0.0)),
                            published_date=item.get("published_date"),
                        )
                        for item in data.get("results", [])
                    ]
                    return TavilySearchResponse(
                        query=req.query,
                        answer=data.get("answer"),
                        results=items,
                        response_time=latency,
                        status_code=200,
                        is_error=False,
                    )
                elif res.status_code == 401 or res.status_code == 403:
                    return TavilySearchResponse(
                        query=req.query,
                        is_error=True,
                        status_code=res.status_code,
                        error_category=TavilyErrorCategory.AUTH_ERROR.value,
                        error_message="Invalid or unauthorized Tavily API key.",
                        response_time=latency,
                    )
                elif res.status_code == 429:
                    return TavilySearchResponse(
                        query=req.query,
                        is_error=True,
                        status_code=429,
                        error_category=TavilyErrorCategory.RATE_LIMIT.value,
                        error_message="Tavily API rate limit exceeded.",
                        response_time=latency,
                    )
                else:
                    return TavilySearchResponse(
                        query=req.query,
                        is_error=True,
                        status_code=res.status_code,
                        error_category=TavilyErrorCategory.UPSTREAM_ERROR.value,
                        error_message=f"Tavily returned upstream error HTTP {res.status_code}: {res.text[:200]}",
                        response_time=latency,
                    )
        except httpx.TimeoutException:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return TavilySearchResponse(
                query=req.query,
                is_error=True,
                status_code=408,
                error_category=TavilyErrorCategory.TIMEOUT.value,
                error_message=f"Tavily request timed out after {self.timeout}s.",
                response_time=latency,
            )
        except Exception as ex:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return TavilySearchResponse(
                query=req.query,
                is_error=True,
                status_code=500,
                error_category=TavilyErrorCategory.NETWORK_ERROR.value,
                error_message=f"Network error connecting to Tavily: {str(ex)}",
                response_time=latency,
            )

    def extract(self, req: TavilyExtractRequest) -> TavilyExtractResponse:
        """Executes extract against POST /extract."""
        if not self.is_configured:
            return TavilyExtractResponse(
                is_error=True,
                error_message="Tavily API key not configured.",
            )

        payload = {
            "api_key": self.api_key,
            "urls": req.urls,
        }
        start = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.api_base}/extract", json=payload)
                latency = round((time.perf_counter() - start) * 1000, 2)
                if res.status_code == 200:
                    data = res.json()
                    return TavilyExtractResponse(
                        results=data.get("results", []),
                        failed_results=data.get("failed_results", []),
                        response_time=latency,
                        is_error=False,
                    )
                return TavilyExtractResponse(
                    is_error=True,
                    error_message=f"Extract error HTTP {res.status_code}: {res.text[:200]}",
                    response_time=latency,
                )
        except Exception as ex:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return TavilyExtractResponse(
                is_error=True,
                error_message=str(ex),
                response_time=latency,
            )
