from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel
from app.faults.engine import FaultKind
from app.evaluation.taxonomy import TaxonomyCategory


class FailureScenarioCatalogEntry(BaseModel):
    id: str
    name: str
    code: str
    failure_kind: str
    description: str
    trigger_point: str
    severity: str
    default_parameters: Dict[str, Any]
    applicable_taxonomy: str


# System-defined catalog of supported controlled fault injection scenarios
SYSTEM_FAILURE_CATALOG: List[FailureScenarioCatalogEntry] = [
    FailureScenarioCatalogEntry(
        id="scen-tool-error",
        name="Tool Execution Error",
        code="TOOL_ERROR",
        failure_kind=FaultKind.TOOL_ERROR.value,
        description="Tool returns an exit-code 1 or exception payload to evaluate agent error-contract handling.",
        trigger_point="TOOL_CALL",
        severity="MEDIUM",
        default_parameters={"http_status": 500, "error_type": "ToolExecutionError"},
        applicable_taxonomy=TaxonomyCategory.TOOL_CONTRACT.value,
    ),
    FailureScenarioCatalogEntry(
        id="scen-tool-timeout",
        name="Tool Execution Timeout",
        code="TOOL_TIMEOUT",
        failure_kind=FaultKind.TOOL_TIMEOUT.value,
        description="Tool execution hangs past the configured threshold to test timeout handling and async aborts.",
        trigger_point="TOOL_CALL",
        severity="HIGH",
        default_parameters={"timeout_seconds": 15},
        applicable_taxonomy=TaxonomyCategory.TIMEOUT.value,
    ),
    FailureScenarioCatalogEntry(
        id="scen-model-unavailable",
        name="Model / Provider Outage (HTTP 5xx)",
        code="MODEL_UNAVAILABLE",
        failure_kind=FaultKind.MODEL_UNAVAILABLE.value,
        description="Model gateway or provider endpoint returns 503 Service Unavailable or 429 rate limit.",
        trigger_point="PROVIDER_RESPONSE",
        severity="CRITICAL",
        default_parameters={"status_code": 503, "retry_after": 2},
        applicable_taxonomy=TaxonomyCategory.MODEL_OUTAGE.value,
    ),
    FailureScenarioCatalogEntry(
        id="scen-misleading-instruction",
        name="Contradictory / Misleading Context",
        code="MISLEADING_INSTRUCTION",
        failure_kind=FaultKind.MISLEADING_INSTRUCTION.value,
        description="Injects contradictory environmental or prompt directives to test goal resilience and planning fidelity.",
        trigger_point="ENVIRONMENT_OBSERVATION",
        severity="LOW",
        default_parameters={"contradiction_scope": "file_lock"},
        applicable_taxonomy=TaxonomyCategory.INSTRUCTION_CONFLICT.value,
    ),
]


def get_system_failure_catalog() -> List[FailureScenarioCatalogEntry]:
    return SYSTEM_FAILURE_CATALOG

