from __future__ import annotations

from enum import Enum


class TavilyErrorCategory(str, Enum):
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    UPSTREAM_ERROR = "UPSTREAM_ERROR"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    NOT_CONFIGURED = "NOT_CONFIGURED"


class TavilyException(Exception):
    def __init__(self, message: str, category: TavilyErrorCategory, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.category = category
        self.status_code = status_code
