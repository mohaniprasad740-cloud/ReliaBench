from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TavilySearchRequest(BaseModel):
    query: str
    search_depth: str = "basic"  # "basic" or "advanced"
    topic: str = "general"       # "general" or "news"
    max_results: int = Field(default=5, ge=1, le=20)
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None
    include_answer: bool = False
    include_raw_content: bool = False
    days: Optional[int] = None


class TavilySearchResultItem(BaseModel):
    title: str
    url: str
    content: str
    score: float = 0.0
    published_date: Optional[str] = None


class TavilySearchResponse(BaseModel):
    query: str
    answer: Optional[str] = None
    results: List[TavilySearchResultItem] = Field(default_factory=list)
    response_time: float = 0.0
    status_code: int = 200
    is_error: bool = False
    error_message: Optional[str] = None
    error_category: Optional[str] = None  # AUTH_ERROR, RATE_LIMIT, TIMEOUT, UPSTREAM_ERROR, NETWORK_ERROR


class TavilyExtractRequest(BaseModel):
    urls: List[str]


class TavilyExtractResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(default_factory=list)
    failed_results: List[Dict[str, Any]] = Field(default_factory=list)
    response_time: float = 0.0
    is_error: bool = False
    error_message: Optional[str] = None


class TavilyTelemetryEvent(BaseModel):
    event_id: str
    tool_call_id: Optional[str] = None
    experiment_id: Optional[str] = None
    run_id: Optional[str] = None
    trial_id: Optional[str] = None
    agent_id: Optional[str] = None
    query: str
    search_depth: str
    max_results: int
    domains_included: Optional[List[str]] = None
    result_count: int = 0
    domains_returned: List[str] = Field(default_factory=list)
    latency_ms: float = 0.0
    http_status: int = 200
    is_error: bool = False
    error_category: Optional[str] = None
    timestamp: str
