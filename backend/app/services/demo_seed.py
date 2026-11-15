"""
Reliabench Canonical Demo Environment & Production Seeding Service.

Provides a realistic, mathematically coherent, fully isolated demo dataset:
- 4 Seeded Reference Agents (Atlas, Nova, Sentinel, Swift)
- 5 Benchmark Challenge Packs across 14 distinct tasks
- 5 Controlled Failure Injection Scenarios
- 32 Multi-trial Experiments with exact finite-sample metrics (Wilson CI, Pass@k, Pass^k, Recovery Rate)
- Complete ATIF v1.8 trajectories with tool events & model request telemetry
- Dedicated workspace isolation with is_demo=True and source_mode='SIMULATOR'
- Idempotent, safe for PostgreSQL and SQLite, zero data loss for real user records
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import (
    Agent,
    BenchmarkTask,
    FailureScenario,
    Experiment,
    Run,
    Trial,
    Trajectory,
    ToolEvent,
    ModelRequestEvent,
)
from app.evaluation.metrics import ReliabilityMetricsCalculator

logger = logging.getLogger(__name__)

# Deterministic namespace UUID for stable demo record IDs
DEMO_NS = uuid.UUID("e7b6d19a-9e5c-4e89-8d5f-1a2b3c4d5e6f")

def demo_id(key: str) -> str:
    """Generates a stable, reproducible UUID5 for demo entities."""
    return str(uuid.uuid5(DEMO_NS, key))


# ----------------- 1. CANONICAL AGENT DEFINITIONS -----------------
DEMO_AGENTS = [
    {
        "id": demo_id("agent.atlas"),
        "name": "Atlas Research Agent",
        "description": "Specialized research and information retrieval agent. Leverages structured search query decomposition and evidence synthesis. High task completion on clean tasks, moderate latency.",
        "framework": "custom",
        "version": "2.1.0",
        "adapter_type": "simulator",
        "model_provider": "anthropic",
        "model_name": "claude-3-5-sonnet",
        "endpoint_url": "https://api.anthropic.com/v1/messages",
        "status": "AVAILABLE",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("agent.nova"),
        "name": "Nova Browser Agent",
        "description": "Autonomous web and browser navigation agent. Performs multi-step DOM interaction, form automation, and session state preservation. High tool usage; occasional transient navigation timeouts.",
        "framework": "harbor_native",
        "version": "1.4.2",
        "adapter_type": "harbor_cli",
        "model_provider": "openai",
        "model_name": "gpt-4o",
        "endpoint_url": "harbor://browser-runner:v1.4",
        "status": "AVAILABLE",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("agent.sentinel"),
        "name": "Sentinel Workflow Agent",
        "description": "Resilient multi-step operational agent. Features active exception recovery, exponential backoff policies, and fallback reasoning. Superior recovery on injected tool faults (80%+ recovery rate).",
        "framework": "autogen",
        "version": "0.7.1",
        "adapter_type": "simulator",
        "model_provider": "openai",
        "model_name": "gpt-4o",
        "endpoint_url": "http://localhost:8000/v1/sentinel",
        "status": "AVAILABLE",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("agent.swift"),
        "name": "Swift Assistant",
        "description": "Low-latency rapid execution assistant. Optimized for high throughput and single-turn task resolution. Low median duration (P50), but less consistent under multi-step injected faults.",
        "framework": "custom",
        "version": "3.0.0",
        "adapter_type": "simulator",
        "model_provider": "google",
        "model_name": "gemini-1.5-flash",
        "endpoint_url": "https://generativelanguage.googleapis.com/v1beta",
        "status": "AVAILABLE",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
]

# ----------------- 2. CANONICAL BENCHMARK SUITES & TASKS -----------------
DEMO_TASKS = [
    # Suite 1: Web Research & Information Retrieval
    {
        "id": demo_id("task.web_research.fastapi_di"),
        "name": "FastAPI Dependency Injection Pattern Verification",
        "version": "1.0.0",
        "category": "Web Research",
        "difficulty": "MEDIUM",
        "description": "Query official FastAPI documentation and extract idiomatic sub-dependency pattern with yield teardown.",
        "instruction": "Search upstream docs, verify the Depends() syntax for generator context managers, and output code snippet passing unit assertions.",
        "expected_outcome": "Valid Python snippet implementing yield dependency with clean exit 0 assertion.",
        "verification_method": "ASSERTION_SCRIPT",
        "time_limit_seconds": 120,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("task.web_research.cve_synthesis"),
        "name": "Cross-Source Vulnerability CVE-2024 Synthesis",
        "version": "1.1.0",
        "category": "Web Research",
        "difficulty": "HARD",
        "description": "Synthesize security advisory across NVD and GitHub Security Advisory databases for CVE-2024-38816.",
        "instruction": "Fetch affected package versions, CVSS v3.1 score, and recommended patch commit hash into structured JSON.",
        "expected_outcome": "JSON matching schema with CVSS score within [8.0, 9.5] and accurate patch reference.",
        "verification_method": "STRUCTURED_OUTPUT",
        "time_limit_seconds": 180,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("task.web_research.wheel_metadata"),
        "name": "Python Packaging Wheel Metadata Extraction",
        "version": "1.0.0",
        "category": "Web Research",
        "difficulty": "EASY",
        "description": "Query PyPI JSON API and retrieve wheel compatibility tags for pydantic-core on win_amd64.",
        "instruction": "Parse pypi.org/pypi/pydantic-core/json, extract release filenames, and verify Python 3.13 tag presence.",
        "expected_outcome": "Exact filename string containing cp313-cp313-win_amd64.whl.",
        "verification_method": "SCRIPT_VERIFIER",
        "time_limit_seconds": 90,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },

    # Suite 2: Multi-Step Browser Navigation
    {
        "id": demo_id("task.browser.checkout_flow"),
        "name": "Multi-Stage Checkout Flow Form Filling",
        "version": "2.0.0",
        "category": "Browser Automation",
        "difficulty": "MEDIUM",
        "description": "Navigate a 4-step e-commerce checkout flow: cart review, address verification, billing, and order confirmation.",
        "instruction": "Drive headless browser through staged modal inputs, handle asynchronous loading spinners, and confirm order ID.",
        "expected_outcome": "Confirmation receipt element visible with valid ORDER-XXXX string.",
        "verification_method": "ASSERTION_SCRIPT",
        "time_limit_seconds": 150,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("task.browser.table_pagination"),
        "name": "Dynamic Table Pagination & Row Extraction",
        "version": "1.2.0",
        "category": "Browser Automation",
        "difficulty": "HARD",
        "description": "Scrape 10 paginated pages of data grid rows while handling DOM virtualization and dynamic lazy loading.",
        "instruction": "Traverse pages 1 through 10, extract 100 total rows into CSV format, and verify no duplicates.",
        "expected_outcome": "CSV file with exactly 100 unique record IDs.",
        "verification_method": "FILE_STATE",
        "time_limit_seconds": 210,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("task.browser.auth_state"),
        "name": "Authentication Session State Preservation",
        "version": "1.0.0",
        "category": "Browser Automation",
        "difficulty": "MEDIUM",
        "description": "Authenticate via OAuth mock, capture session cookies, and perform authenticated API action without re-prompt.",
        "instruction": "Complete login form, store bearer token, reload page, and navigate directly to protected profile route.",
        "expected_outcome": "HTTP 200 on /profile with authenticated DOM element present.",
        "verification_method": "ASSERTION_SCRIPT",
        "time_limit_seconds": 120,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },

    # Suite 3: Tool Calling & Execution
    {
        "id": demo_id("task.tools.sql_n_plus_one"),
        "name": "SQL Parameterized Query Refactor (N+1)",
        "version": "1.0.0",
        "category": "Tool Execution",
        "difficulty": "MEDIUM",
        "description": "Identify and refactor N+1 query vulnerability in order summary retrieval script.",
        "instruction": "Inspect queries.py, replace loop-based queries with SQLAlchemy selectinload/joinedload, and verify execution count = 1.",
        "expected_outcome": "Query count assertion equals 1 and execution runtime reduced by >70%.",
        "verification_method": "ASSERTION_SCRIPT",
        "time_limit_seconds": 120,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("task.tools.json_transform"),
        "name": "JSON Schema Transformation & Validation",
        "version": "1.0.0",
        "category": "Tool Execution",
        "difficulty": "EASY",
        "description": "Transform nested legacy customer payload into canonical OpenAPI 3.1 entity schema.",
        "instruction": "Map legacy fields to camelCase, normalize ISO-8601 timestamps, and validate against JSON Schema definition.",
        "expected_outcome": "jsonschema.validate() completes with 0 validation errors.",
        "verification_method": "STRUCTURED_OUTPUT",
        "time_limit_seconds": 90,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("task.tools.webhook_retry"),
        "name": "REST API Webhook Error Handling",
        "version": "1.3.0",
        "category": "Tool Execution",
        "difficulty": "HARD",
        "description": "Implement robust webhook dispatch with signature verification, exponential backoff, and dead-letter queue routing.",
        "instruction": "Handle mock server 500 responses with jittered retries up to 3 attempts before queueing payload to dlq.json.",
        "expected_outcome": "All retries logged with timestamps and dlq.json populated accurately.",
        "verification_method": "FILE_STATE",
        "time_limit_seconds": 180,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },

    # Suite 4: Structured Data Extraction
    {
        "id": demo_id("task.extraction.financial_statement"),
        "name": "Financial Statement Entity & Value Extraction",
        "version": "2.0.0",
        "category": "Data Extraction",
        "difficulty": "MEDIUM",
        "description": "Extract revenue, operating margin, and EBITDA across three consecutive quarterly 10-Q report tables.",
        "instruction": "Parse PDF table fixtures into pandas DataFrame, normalize currency representations, and output tabular CSV.",
        "expected_outcome": "Data values match target financial values within 0.01% numerical tolerance.",
        "verification_method": "SCRIPT_VERIFIER",
        "time_limit_seconds": 150,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("task.extraction.logcat_crash"),
        "name": "Logcat Crash Stacktrace Normalization",
        "version": "1.0.0",
        "category": "Data Extraction",
        "difficulty": "MEDIUM",
        "description": "Parse 50,000 lines of Android logcat text, isolate Fatal Exception occurrences, and group by root cause.",
        "instruction": "Identify unique crash signatures, extract offending class and line numbers, and output deduplicated error ledger.",
        "expected_outcome": "Exactly 3 distinct crash signatures correctly classified with line numbers.",
        "verification_method": "STRUCTURED_OUTPUT",
        "time_limit_seconds": 120,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },

    # Suite 5: Failure Recovery & Resilience
    {
        "id": demo_id("task.recovery.tool_timeout"),
        "name": "Tool Timeout Recovery with Fallback Cache",
        "version": "1.0.0",
        "category": "Failure Resilience",
        "difficulty": "HARD",
        "description": "Execute multi-step calculation when primary computational tool encounters 15s subprocess timeout.",
        "instruction": "Detect tool timeout exception, switch execution strategy to precomputed local cache, and verify final output.",
        "expected_outcome": "Completed task outcome without fatal uncaught exception.",
        "verification_method": "ASSERTION_SCRIPT",
        "time_limit_seconds": 180,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("task.recovery.rate_limit_backoff"),
        "name": "Rate Limit 429 Exponential Backoff Handshake",
        "version": "1.1.0",
        "category": "Failure Resilience",
        "difficulty": "MEDIUM",
        "description": "Perform model-driven data ingestion when upstream gateway injects HTTP 429 Too Many Requests.",
        "instruction": "Read Retry-After header, calculate exponential backoff delay with jitter, and retry request successfully.",
        "expected_outcome": "Successful payload ingestion with retry attempts recorded in telemetry log.",
        "verification_method": "ASSERTION_SCRIPT",
        "time_limit_seconds": 140,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
    {
        "id": demo_id("task.recovery.schema_violation"),
        "name": "Malformed JSON Output Schema Recovery",
        "version": "1.0.0",
        "category": "Failure Resilience",
        "difficulty": "HARD",
        "description": "Correct truncated or hallucinated JSON schema output through reflection and error remediation prompt.",
        "instruction": "Detect JSONDecodeError / Pydantic ValidationError, re-prompt model with explicit error trace, and emit valid payload.",
        "expected_outcome": "Pydantic model parses final JSON without error on second iteration.",
        "verification_method": "STRUCTURED_OUTPUT",
        "time_limit_seconds": 160,
        "environment_type": "DOCKER_SANDBOX",
        "source_mode": "SIMULATOR",
        "is_demo": True,
    },
]

# ----------------- 3. CANONICAL FAILURE SCENARIOS -----------------
DEMO_FAILURES = [
    {
        "id": demo_id("failure.tool_timeout"),
        "name": "Tool Execution Timeout",
        "code": "TOOL_TIMEOUT",
        "description": "Injected delay exceeding standard 15s subprocess tool execution budget.",
        "trigger_point": "TOOL_CALL",
        "severity": "HIGH",
        "parameters": {"timeout_seconds": 15, "fail_on_attempt": 1},
    },
    {
        "id": demo_id("failure.rate_limit_429"),
        "name": "API Gateway Rate Limit (HTTP 429)",
        "code": "RATE_LIMIT_429",
        "description": "Simulates OpenAI/Bifrost upstream rate limits with Retry-After response header.",
        "trigger_point": "MODEL_REQUEST",
        "severity": "MEDIUM",
        "parameters": {"status_code": 429, "retry_after_seconds": 2, "burst_count": 2},
    },
    {
        "id": demo_id("failure.search_unavailable"),
        "name": "External Web Search Unavailable",
        "code": "SEARCH_UNAVAILABLE",
        "description": "Simulates Tavily / Google Search upstream network partition or API quota exhaustion.",
        "trigger_point": "TOOL_CALL",
        "severity": "HIGH",
        "parameters": {"status_code": 503, "tool_target": "tavily_search"},
    },
    {
        "id": demo_id("failure.nav_timeout"),
        "name": "Browser Navigation Timeout",
        "code": "NAV_TIMEOUT",
        "description": "Simulates unresponsive headless browser page navigation on heavy client-rendered SPAs.",
        "trigger_point": "TOOL_CALL",
        "severity": "MEDIUM",
        "parameters": {"timeout_ms": 30000, "page_selector": "app-root"},
    },
    {
        "id": demo_id("failure.schema_violation"),
        "name": "Malformed Structured Output",
        "code": "SCHEMA_VIOLATION",
        "description": "Simulates malformed or incomplete JSON generation violating schema contract.",
        "trigger_point": "POST_TASK",
        "severity": "HIGH",
        "parameters": {"error_type": "JSONDecodeError", "truncate_bytes": 12},
    },
]

# ----------------- 4. CANONICAL EXPERIMENT DEFINITION MATRIX -----------------
# Configures 32 experiments across the 4 agents and tasks
# Each entry defines: agent_key, task_key, failure_key, repetitions_k, and trial outcome pattern.
# Trial pattern string:
#   'P' = PASSED (clean pass)
#   'F' = FAILED (unrecovered failure)
#   'R' = RECOVERED (injected fault occurred + agent adapted + verifier passed)
EXPERIMENT_CONFIGS = [
    # --- SUITE 1: Web Research & Information Retrieval ---
    # Task 1: FastAPI Dependency Injection
    {"agent": "agent.atlas", "task": "task.web_research.fastapi_di", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.024, "dur": [7.8, 8.2, 8.5, 8.9, 9.1]},
    {"agent": "agent.nova", "task": "task.web_research.fastapi_di", "failure": None, "k": 5, "pattern": "PPPFP", "cost": 0.038, "dur": [11.2, 12.0, 12.5, 13.8, 12.1]},
    {"agent": "agent.sentinel", "task": "task.web_research.fastapi_di", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.035, "dur": [13.5, 14.2, 14.8, 15.1, 14.5]},
    {"agent": "agent.swift", "task": "task.web_research.fastapi_di", "failure": None, "k": 5, "pattern": "PPFPF", "cost": 0.006, "dur": [2.8, 3.1, 3.2, 3.5, 3.4]},

    # Task 2: CVE-2024 Synthesis
    {"agent": "agent.atlas", "task": "task.web_research.cve_synthesis", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.031, "dur": [14.2, 15.1, 15.8, 16.2, 15.5]},
    {"agent": "agent.nova", "task": "task.web_research.cve_synthesis", "failure": None, "k": 5, "pattern": "PPFPP", "cost": 0.045, "dur": [18.2, 19.5, 21.0, 19.8, 20.1]},
    {"agent": "agent.sentinel", "task": "task.web_research.cve_synthesis", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.042, "dur": [17.5, 18.0, 18.5, 19.0, 18.2]},
    {"agent": "agent.swift", "task": "task.web_research.cve_synthesis", "failure": None, "k": 5, "pattern": "PFPPF", "cost": 0.009, "dur": [4.2, 4.8, 5.1, 5.5, 5.0]},

    # Task 3: Wheel Metadata
    {"agent": "agent.atlas", "task": "task.web_research.wheel_metadata", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.015, "dur": [5.2, 5.5, 5.8, 6.0, 5.7]},
    {"agent": "agent.swift", "task": "task.web_research.wheel_metadata", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.004, "dur": [1.9, 2.1, 2.2, 2.4, 2.2]},

    # --- SUITE 2: Multi-Step Browser Navigation ---
    # Task 4: Multi-Stage Checkout Flow
    {"agent": "agent.nova", "task": "task.browser.checkout_flow", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.052, "dur": [10.5, 11.2, 11.8, 12.0, 11.5]},
    {"agent": "agent.atlas", "task": "task.browser.checkout_flow", "failure": None, "k": 5, "pattern": "PPFPP", "cost": 0.041, "dur": [14.2, 14.8, 16.0, 15.2, 15.1]},
    {"agent": "agent.sentinel", "task": "task.browser.checkout_flow", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.048, "dur": [15.5, 16.1, 16.8, 17.2, 16.5]},
    {"agent": "agent.swift", "task": "task.browser.checkout_flow", "failure": None, "k": 5, "pattern": "PFFPF", "cost": 0.012, "dur": [4.1, 4.5, 4.8, 5.2, 4.9]},

    # Task 5: Dynamic Table Pagination
    {"agent": "agent.nova", "task": "task.browser.table_pagination", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.065, "dur": [18.5, 19.2, 20.1, 21.0, 19.8]},
    {"agent": "agent.atlas", "task": "task.browser.table_pagination", "failure": None, "k": 5, "pattern": "PPPFP", "cost": 0.055, "dur": [22.0, 23.5, 25.1, 24.2, 23.8]},

    # Task 6: Authentication Session State
    {"agent": "agent.nova", "task": "task.browser.auth_state", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.044, "dur": [9.8, 10.5, 11.0, 11.4, 10.8]},
    {"agent": "agent.sentinel", "task": "task.browser.auth_state", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.040, "dur": [12.2, 12.8, 13.5, 14.0, 13.1]},

    # --- SUITE 3: Tool Calling & Execution ---
    # Task 7: SQL Parameterized Query Refactor (N+1)
    {"agent": "agent.atlas", "task": "task.tools.sql_n_plus_one", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.028, "dur": [8.2, 8.8, 9.1, 9.5, 8.9]},
    {"agent": "agent.sentinel", "task": "task.tools.sql_n_plus_one", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.032, "dur": [10.5, 11.0, 11.4, 12.0, 11.2]},
    {"agent": "agent.nova", "task": "task.tools.sql_n_plus_one", "failure": None, "k": 5, "pattern": "PPFPP", "cost": 0.036, "dur": [12.0, 12.8, 14.1, 13.2, 13.0]},
    {"agent": "agent.swift", "task": "task.tools.sql_n_plus_one", "failure": None, "k": 5, "pattern": "PPFPF", "cost": 0.008, "dur": [2.9, 3.2, 3.5, 3.8, 3.4]},

    # Task 8: JSON Schema Transformation
    {"agent": "agent.atlas", "task": "task.tools.json_transform", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.019, "dur": [6.1, 6.4, 6.8, 7.0, 6.6]},
    {"agent": "agent.swift", "task": "task.tools.json_transform", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.005, "dur": [1.8, 2.0, 2.2, 2.3, 2.1]},

    # --- SUITE 4: Structured Data Extraction ---
    # Task 10: Financial Statement Extraction
    {"agent": "agent.atlas", "task": "task.extraction.financial_statement", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.038, "dur": [11.5, 12.2, 12.8, 13.4, 12.5]},
    {"agent": "agent.sentinel", "task": "task.extraction.financial_statement", "failure": None, "k": 5, "pattern": "PPPPP", "cost": 0.041, "dur": [13.8, 14.5, 15.2, 15.8, 14.9]},

    # --- SUITE 5: Failure Recovery & Resilience (Controlled Fault Injections) ---
    # Task 12: Tool Timeout Recovery (Injected: TOOL_TIMEOUT)
    # Sentinel: 5 trials, 5 injected, 4 recovered! (Recovery rate = 80%)
    {"agent": "agent.sentinel", "task": "task.recovery.tool_timeout", "failure": "failure.tool_timeout", "k": 5, "pattern": "RRRRF", "cost": 0.049, "dur": [18.2, 19.5, 20.1, 21.0, 22.5]},
    # Atlas: 5 trials, 5 injected, 3 recovered! (Recovery rate = 60%)
    {"agent": "agent.atlas", "task": "task.recovery.tool_timeout", "failure": "failure.tool_timeout", "k": 5, "pattern": "RRRFF", "cost": 0.042, "dur": [16.8, 17.5, 18.2, 19.0, 20.4]},
    # Swift: 5 trials, 5 injected, 1 recovered! (Recovery rate = 20%)
    {"agent": "agent.swift", "task": "task.recovery.tool_timeout", "failure": "failure.tool_timeout", "k": 5, "pattern": "RFFFF", "cost": 0.014, "dur": [6.5, 7.2, 7.8, 8.0, 8.5]},

    # Task 13: Rate Limit 429 Exponential Backoff (Injected: RATE_LIMIT_429)
    # Sentinel: 5 trials, 5 injected, 5 recovered! (Recovery rate = 100%)
    {"agent": "agent.sentinel", "task": "task.recovery.rate_limit_backoff", "failure": "failure.rate_limit_429", "k": 5, "pattern": "RRRRR", "cost": 0.046, "dur": [14.5, 15.2, 15.8, 16.4, 15.6]},
    # Nova: 5 trials, 5 injected, 3 recovered! (Recovery rate = 60%)
    {"agent": "agent.nova", "task": "task.recovery.rate_limit_backoff", "failure": "failure.rate_limit_429", "k": 5, "pattern": "RRRFF", "cost": 0.050, "dur": [16.8, 17.9, 18.5, 19.2, 18.0]},
    # Swift: 5 trials, 5 injected, 2 recovered! (Recovery rate = 40%)
    {"agent": "agent.swift", "task": "task.recovery.rate_limit_backoff", "failure": "failure.rate_limit_429", "k": 5, "pattern": "RRFFF", "cost": 0.011, "dur": [5.2, 5.8, 6.2, 6.5, 6.0]},

    # Task 14: Malformed Output Schema (Injected: SCHEMA_VIOLATION)
    # Sentinel: 5 trials, 5 injected, 4 recovered! (Recovery rate = 80%)
    {"agent": "agent.sentinel", "task": "task.recovery.schema_violation", "failure": "failure.schema_violation", "k": 5, "pattern": "RRRRF", "cost": 0.053, "dur": [17.5, 18.2, 19.0, 19.8, 20.2]},
]


# ----------------- SEEDING & RESET IMPLEMENTATION -----------------

def clean_existing_demo_records(db: Session) -> int:
    """Safely purges existing demo records (is_demo=True) while strictly preserving user data."""
    demo_exps = db.query(Experiment).filter(Experiment.is_demo == True).all()
    exp_ids = [e.id for e in demo_exps]

    # Delete experiments (cascade will delete runs, trials, tool_events, model_requests, trajectories)
    deleted_exps = 0
    for exp in demo_exps:
        db.delete(exp)
        deleted_exps += 1

    # Delete demo tasks and agents
    db.query(BenchmarkTask).filter(BenchmarkTask.is_demo == True).delete(synchronize_session=False)
    db.query(Agent).filter(Agent.is_demo == True).delete(synchronize_session=False)
    db.commit()
    logger.info(f"Cleaned {deleted_exps} existing demo experiments.")
    return deleted_exps


def seed_demo_data(db: Session, force_reset: bool = False) -> Dict[str, Any]:
    """
    Idempotently populates the canonical Reliabench Demo dataset.
    Ensures mathematical consistency between runs and underlying trials.
    """
    # 1. Check if already seeded and force_reset not requested
    existing_agents = db.query(Agent).filter(Agent.is_demo == True).count()
    existing_exps = db.query(Experiment).filter(Experiment.is_demo == True).count()

    if existing_agents >= len(DEMO_AGENTS) and existing_exps >= len(EXPERIMENT_CONFIGS) and not force_reset:
        logger.info("Demo dataset is already seeded and complete.")
        return {
            "status": "ALREADY_SEEDED",
            "agents_count": existing_agents,
            "tasks_count": db.query(BenchmarkTask).filter(BenchmarkTask.is_demo == True).count(),
            "experiments_count": existing_exps,
            "message": "Demo workspace is fully populated.",
        }

    # 2. If force_reset or partial state, clean up first
    if force_reset or (existing_agents > 0 and existing_exps < len(EXPERIMENT_CONFIGS)):
        clean_existing_demo_records(db)

    logger.info("Seeding canonical Reliabench Demo dataset...")

    # 3. Seed Agents
    agents_map: Dict[str, Agent] = {}
    for a_data in DEMO_AGENTS:
        agent = db.query(Agent).filter(Agent.id == a_data["id"]).first()
        if not agent:
            agent = Agent(**a_data)
            db.add(agent)
        agents_map[a_data["name"]] = agent
        # Also map by key
        for key in ["agent.atlas", "agent.nova", "agent.sentinel", "agent.swift"]:
            if demo_id(key) == a_data["id"]:
                agents_map[key] = agent
    db.flush()

    # 4. Seed Benchmark Tasks
    tasks_map: Dict[str, BenchmarkTask] = {}
    for t_data in DEMO_TASKS:
        task = db.query(BenchmarkTask).filter(BenchmarkTask.id == t_data["id"]).first()
        if not task:
            task = BenchmarkTask(**t_data)
            db.add(task)
        tasks_map[t_data["name"]] = task
        # Also map by key
        for prefix in ["task.web_research.", "task.browser.", "task.tools.", "task.extraction.", "task.recovery."]:
            for key in ["fastapi_di", "cve_synthesis", "wheel_metadata", "checkout_flow", "table_pagination", "auth_state", "sql_n_plus_one", "json_transform", "webhook_retry", "financial_statement", "logcat_crash", "tool_timeout", "rate_limit_backoff", "schema_violation"]:
                full_key = prefix + key
                if demo_id(full_key) == t_data["id"]:
                    tasks_map[full_key] = task
    db.flush()

    # 5. Seed Failure Scenarios
    failures_map: Dict[str, FailureScenario] = {}
    for f_data in DEMO_FAILURES:
        failure = db.query(FailureScenario).filter(FailureScenario.id == f_data["id"]).first()
        if not failure:
            # Check by unique code
            existing_code = db.query(FailureScenario).filter(FailureScenario.code == f_data["code"]).first()
            if existing_code:
                failure = existing_code
            else:
                failure = FailureScenario(**f_data)
                db.add(failure)
        failures_map[f_data["name"]] = failure
        failures_map[f_data["code"]] = failure
        for key in ["failure.tool_timeout", "failure.rate_limit_429", "failure.search_unavailable", "failure.nav_timeout", "failure.schema_violation"]:
            if demo_id(key) == f_data["id"]:
                failures_map[key] = failure
    db.flush()

    # 6. Seed Experiments, Runs, Trials, Trajectories, and Telemetry Events
    base_time = datetime.now(timezone.utc) - timedelta(days=2)
    seeded_experiments = 0
    seeded_trials = 0

    for idx, cfg in enumerate(EXPERIMENT_CONFIGS):
        agent = agents_map.get(cfg["agent"])
        task = tasks_map.get(cfg["task"])
        if not agent or not task:
            logger.warning(f"Could not find agent {cfg['agent']} or task {cfg['task']}")
            continue

        failure = failures_map.get(cfg["failure"]) if cfg["failure"] else None
        exp_id = demo_id(f"exp.{cfg['agent']}.{cfg['task']}.{cfg['failure'] or 'clean'}")

        exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
        if not exp:
            exp_created_at = base_time + timedelta(hours=idx * 1.5)
            exp_title = f"{agent.name} — {task.name}"
            if failure:
                exp_title += f" [{failure.code}]"

            config_snapshot = {
                "agent": {
                    "id": agent.id,
                    "name": agent.name,
                    "framework": agent.framework,
                    "model_provider": agent.model_provider,
                    "model_name": agent.model_name,
                    "version": agent.version,
                },
                "task": {
                    "id": task.id,
                    "name": task.name,
                    "category": task.category,
                    "difficulty": task.difficulty,
                    "verification_method": task.verification_method,
                },
                "failure_scenario": {
                    "id": failure.id,
                    "code": failure.code,
                    "name": failure.name,
                    "parameters": failure.parameters,
                } if failure else None,
                "repetitions_k": cfg["k"],
                "seed": 42 + idx,
                "timeout_seconds": task.time_limit_seconds,
            }

            exp = Experiment(
                id=exp_id,
                title=exp_title,
                description=f"Standardized benchmark evaluation of {agent.name} on '{task.name}' across k={cfg['k']} repeated trials.",
                agent_id=agent.id,
                benchmark_task_id=task.id,
                failure_scenario_id=failure.id if failure else None,
                repetitions_k=cfg["k"],
                timeout_seconds=task.time_limit_seconds,
                config_snapshot=config_snapshot,
                status="COMPLETED",
                source_mode="SIMULATOR",
                is_demo=True,
                created_at=exp_created_at,
                started_at=exp_created_at + timedelta(seconds=2),
                completed_at=exp_created_at + timedelta(seconds=90),
            )
            db.add(exp)
            db.flush()

        seeded_experiments += 1

        # Check if Run exists for this experiment
        run = db.query(Run).filter(Run.experiment_id == exp.id).first()
        if not run:
            run_id = demo_id(f"run.{exp.id}")
            run = Run(
                id=run_id,
                experiment_id=exp.id,
                status="COMPLETED",
                source_mode="SIMULATOR",
                created_at=exp.created_at + timedelta(seconds=5),
            )
            db.add(run)
            db.flush()

            # Create Trials according to pattern
            pattern = cfg["pattern"]
            durations = cfg.get("dur", [8.0] * len(pattern))
            trial_objects: List[Trial] = []
            trial_durations: List[float] = []

            for t_idx, outcome_char in enumerate(pattern):
                trial_id = demo_id(f"trial.{run.id}.{t_idx + 1}")
                dur = durations[t_idx] if t_idx < len(durations) else 8.0
                trial_durations.append(dur)

                # Status mapping
                if outcome_char == "P":
                    st = "PASSED"
                    reward = 1.0
                    injected = False
                    recovered = False
                    err_msg = None
                elif outcome_char == "R":
                    st = "RECOVERED"
                    reward = 1.0
                    injected = True
                    recovered = True
                    err_msg = f"Recovered from {failure.name if failure else 'fault'}"
                else:  # 'F'
                    st = "FAILED"
                    reward = 0.0
                    injected = bool(failure is not None)
                    recovered = False
                    err_msg = f"Task verification failed: {failure.name if failure else 'AssertionError'}"

                prompt_tokens = 650 + (t_idx * 45)
                comp_tokens = 140 + (t_idx * 15)
                trial_cost = round(cfg["cost"] / len(pattern), 5)

                trial = Trial(
                    id=trial_id,
                    run_id=run.id,
                    trial_number=t_idx + 1,
                    status=st,
                    reward_score=reward,
                    duration_seconds=dur,
                    failure_injected=injected,
                    failure_recovered=recovered,
                    error_message=err_msg,
                    source_mode="SIMULATOR",
                    created_at=exp.created_at + timedelta(seconds=10 + t_idx * 15),
                )
                db.add(trial)
                db.flush()
                trial_objects.append(trial)
                seeded_trials += 1

                # Generate detailed ATIF Trajectory and Telemetry Events for each trial
                create_demo_trajectory_and_telemetry(db, trial, exp, agent, task, failure, st, recovered)

            # Compute mathematically exact run metrics using ReliabilityMetricsCalculator
            successes = sum(1 for t in trial_objects if t.status in ("PASSED", "RECOVERED"))
            failures_count = len(trial_objects) - successes
            n = len(trial_objects)
            k = cfg["k"]

            pass_rate = ReliabilityMetricsCalculator.calculate_pass_rate(successes, n)
            wilson_ci = ReliabilityMetricsCalculator.calculate_wilson_confidence_interval(successes, n)
            pass_at_k = ReliabilityMetricsCalculator.calculate_pass_at_k(n, successes, min(k, n))
            pass_to_k = ReliabilityMetricsCalculator.calculate_pass_to_k(n, successes, min(k, n))

            injected_count = sum(1 for t in trial_objects if t.failure_injected)
            recovered_count = sum(1 for t in trial_objects if t.failure_recovered)
            recovery_rate = ReliabilityMetricsCalculator.calculate_recovery_rate(recovered_count, injected_count)

            dur_metrics = ReliabilityMetricsCalculator.calculate_duration_metrics(trial_durations)

            run.total_trials = n
            run.successful_trials = successes
            run.failed_trials = failures_count
            run.pass_rate = pass_rate
            run.ci_lower = wilson_ci["lower"] if wilson_ci else None
            run.ci_upper = wilson_ci["upper"] if wilson_ci else None
            run.pass_at_k = pass_at_k
            run.pass_to_k = pass_to_k
            run.recovery_rate = recovery_rate
            run.avg_duration_seconds = dur_metrics["avg_duration"]
            run.median_duration_seconds = dur_metrics["median_duration"]
            run.duration_variance = dur_metrics["variance"]
            run.avg_cost_usd = round(cfg["cost"], 4)
            run.total_tokens = sum(800 + i * 50 for i in range(n))
            db.flush()

    db.commit()
    logger.info(f"Seeding complete: {len(DEMO_AGENTS)} agents, {len(DEMO_TASKS)} tasks, {seeded_experiments} experiments, {seeded_trials} trials.")

    return {
        "status": "SUCCESS",
        "agents_count": len(DEMO_AGENTS),
        "tasks_count": len(DEMO_TASKS),
        "failures_count": len(DEMO_FAILURES),
        "experiments_count": seeded_experiments,
        "trials_count": seeded_trials,
        "message": "Reliabench Demo Environment successfully seeded with mathematically consistent benchmark data.",
    }


def create_demo_trajectory_and_telemetry(
    db: Session,
    trial: Trial,
    exp: Experiment,
    agent: Agent,
    task: BenchmarkTask,
    failure: Optional[FailureScenario],
    status: str,
    is_recovered: bool,
) -> None:
    """Populates ATIF v1.8 trajectory steps and unified ToolEvent / ModelRequestEvent telemetry records."""
    corr_id = f"demo-bf-{trial.id[:8]}"
    step_time = trial.created_at

    # 1. Model Request Telemetry Event (Initial decomposition)
    mreq1 = ModelRequestEvent(
        id=demo_id(f"mreq1.{trial.id}"),
        trial_id=trial.id,
        correlation_id=corr_id,
        provider=agent.model_provider or "openai",
        model=agent.model_name or "gpt-4o",
        prompt_tokens=540,
        completion_tokens=95,
        total_tokens=635,
        cost_usd=0.0018,
        latency_ms=850.0,
        fallback_used=False,
        retry_count=0,
        status_code=200,
        created_at=step_time,
    )
    db.add(mreq1)

    # 2. Tool Event (Primary action, e.g. web search or shell execution)
    tool_name = "tavily_search" if "Web Research" in task.category else ("browser_navigate" if "Browser" in task.category else "run_sql")
    has_fault = bool(failure is not None)

    tevent1 = ToolEvent(
        id=demo_id(f"tevent1.{trial.id}"),
        trial_id=trial.id,
        tool_name=tool_name,
        tool_call_id=f"call_{trial.id[:6]}_1",
        args={"query": task.name, "target_url": "https://docs.fastapi.tiangolo.com"} if tool_name == "tavily_search" else {"command": "execute_plan"},
        observation="Upstream tool error: Timeout (15s)" if has_fault and not is_recovered else "Successfully retrieved documentation records.",
        is_error=(has_fault and not is_recovered),
        error_message="Subprocess execution exceeded 15s budget" if (has_fault and not is_recovered) else None,
        latency_ms=1450.0 if not has_fault else 15020.0,
        source="TAVILY" if tool_name == "tavily_search" else "LOCAL_SHELL",
        meta_info={"domain": "docs.fastapi.tiangolo.com", "results_count": 3 if not (has_fault and not is_recovered) else 0},
        created_at=step_time + timedelta(seconds=2),
    )
    db.add(tevent1)

    # 3. If recovered, emit second model request and compensatory tool event
    if is_recovered:
        mreq2 = ModelRequestEvent(
            id=demo_id(f"mreq2.{trial.id}"),
            trial_id=trial.id,
            correlation_id=corr_id,
            provider=agent.model_provider or "openai",
            model=agent.model_name or "gpt-4o",
            prompt_tokens=780,
            completion_tokens=140,
            total_tokens=920,
            cost_usd=0.0024,
            latency_ms=1100.0,
            fallback_used=True,
            retry_count=1,
            status_code=200,
            created_at=step_time + timedelta(seconds=4),
        )
        db.add(mreq2)

        tevent2 = ToolEvent(
            id=demo_id(f"tevent2.{trial.id}"),
            trial_id=trial.id,
            tool_name=tool_name,
            tool_call_id=f"call_{trial.id[:6]}_2",
            args={"query": f"{task.name} fallback cache", "mode": "cached_local"},
            observation="Compensatory fallback cache hit. Required symbols resolved.",
            is_error=False,
            error_message=None,
            latency_ms=120.0,
            source="LOCAL_SHELL",
            meta_info={"recovery_strategy": "cache_fallback", "attempts": 2},
            created_at=step_time + timedelta(seconds=5),
        )
        db.add(tevent2)

    # 4. Construct ATIF Trajectory Steps (Stored in summary_steps for serverless availability)
    atif_steps = [
        {
            "step_id": 1,
            "timestamp": step_time.isoformat(),
            "source": "user",
            "message": task.instruction,
        },
        {
            "step_id": 2,
            "timestamp": (step_time + timedelta(seconds=2)).isoformat(),
            "source": "agent",
            "message": f"Decomposing task requirement for {task.name}.",
            "reasoning_content": f"Formulating plan and invoking primary tool '{tool_name}'.",
            "tool_calls": [
                {
                    "tool_call_id": f"call_{trial.id[:6]}_1",
                    "function_name": tool_name,
                    "arguments": {"query": task.name},
                }
            ],
            "metrics": {"prompt_tokens": 540, "completion_tokens": 95, "cost": 0.0018},
        },
        {
            "step_id": 3,
            "timestamp": (step_time + timedelta(seconds=3)).isoformat(),
            "source": "system",
            "observation": {
                "results": [
                    {
                        "tool_call_id": f"call_{trial.id[:6]}_1",
                        "content": f"INJECTED FAULT: {failure.name}" if has_fault else "SUCCESS: Output matches specification.",
                        "is_error": has_fault,
                    }
                ]
            },
        },
    ]

    if is_recovered:
        atif_steps.extend([
            {
                "step_id": 4,
                "timestamp": (step_time + timedelta(seconds=5)).isoformat(),
                "source": "agent",
                "message": f"Active exception detected ({failure.name if failure else 'fault'}). Applying compensatory retry policy.",
                "reasoning_content": "Switching to alternative tool provider and re-evaluating assertions.",
                "tool_calls": [
                    {
                        "tool_call_id": f"call_{trial.id[:6]}_2",
                        "function_name": tool_name,
                        "arguments": {"mode": "recovery_retry"},
                    }
                ],
                "metrics": {"prompt_tokens": 780, "completion_tokens": 140, "cost": 0.0024},
            },
            {
                "step_id": 5,
                "timestamp": (step_time + timedelta(seconds=6)).isoformat(),
                "source": "system",
                "observation": {
                    "results": [
                        {
                            "tool_call_id": f"call_{trial.id[:6]}_2",
                            "content": "VERIFIED: Compensatory execution passed all regression assertions.",
                            "is_error": False,
                        }
                    ]
                },
            },
            {
                "step_id": 6,
                "timestamp": (step_time + timedelta(seconds=7)).isoformat(),
                "source": "system",
                "message": "Final Evaluation: RECOVERED. Reward = 1.0.",
            },
        ])
    else:
        atif_steps.append({
            "step_id": 4,
            "timestamp": (step_time + timedelta(seconds=4)).isoformat(),
            "source": "system",
            "message": f"Final Evaluation: {status}. Reward = {1.0 if status == 'PASSED' else 0.0}.",
        })

    traj_path = settings.TRAJECTORIES_DIR / f"trial_{trial.id}.json"
    
    # Save to disk when directory is writable
    try:
        with open(traj_path, "w", encoding="utf-8") as f:
            json.dump({
                "schema_version": "ATIF-v1.8",
                "trajectory_id": f"reliabench:{trial.id}",
                "metadata": {
                    "agent": agent.name,
                    "task": task.name,
                    "provenance": "SIMULATOR",
                    "status": status,
                },
                "steps": atif_steps,
            }, f, indent=2)
    except Exception:
        pass

    trajectory = Trajectory(
        id=demo_id(f"traj.{trial.id}"),
        trial_id=trial.id,
        atif_version="ATIF-v1.8",
        total_steps=len(atif_steps),
        agent_name=agent.name,
        model_name=agent.model_name,
        prompt_tokens=1320 if is_recovered else 540,
        completion_tokens=235 if is_recovered else 95,
        total_cost=0.0042 if is_recovered else 0.0018,
        storage_path=str(traj_path),
        summary_steps=atif_steps,
    )
    db.add(trajectory)


def reset_demo_data(db: Session) -> Dict[str, Any]:
    """Safely clears and re-seeds canonical demo data without touching real user records."""
    return seed_demo_data(db, force_reset=True)


def auto_seed_if_empty(engine: Engine) -> None:
    """Safe bootstrap helper called during startup to ensure live deployments have demo data available."""
    try:
        with Session(engine) as db:
            count = db.query(Agent).filter(Agent.is_demo == True).count()
            if count == 0:
                logger.info("Initializing demo data on cold bootstrap...")
                seed_demo_data(db, force_reset=False)
    except Exception as ex:
        logger.warning(f"Auto-seed check encountered non-fatal notice: {ex}")
