# Reliabench — End-to-End Validation & Live Execution Audit Report

**Date:** 2026-11-13  
**Status:** Audit Completed & Grounded  
**Specification:** PS02 — AI Agent Benchmarking Platform  

---

## 1. Test Environment Specification

- **Host Operating System:** Windows 11 (build 26100)
- **Python Runtime:** Python 3.13.7
- **Node.js / Build Tools:** Node.js v24.19.2, Vite 8.3.7, React 19.3.1, TypeScript 7.0.2
- **Backend Framework:** FastAPI 0.115.0, SQLAlchemy 2.0.36, Pydantic v2.10.0
- **Database:** Local SQLite (`reliabench.db`) with production support for Managed PostgreSQL via `NullPool`
- **Artifact Engine:** Local storage abstraction (`artifacts/trajectories/`) with production support for Vercel Blob REST API

---

## 2. Live Integration Boundary Probes

### 2.1. Harbor Container Engine & Docker
- **Docker Client Probe:** `docker --version` -> `Docker version 29.9.2, build a82e528`
- **Docker Daemon Probe:** `docker info` -> `Server: failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.`
- **Harbor CLI Probe:** `harbor --version` -> `CommandNotFoundException (CLI not installed in system PATH)`
- **Adapter Availability Probe:**
  ```json
  {
    "available": false,
    "installed_version": null,
    "required_version": "v0.25.0",
    "docker_available": false,
    "docker_version": null,
    "status": "CLI_NOT_INSTALLED",
    "mode": "SIMULATOR_FALLBACK"
  }
  ```
- **Boundary Classification:** **`BLOCKED_BY_INFRASTRUCTURE`**
- **Fail-Safe Mechanism:** `HarborAdapter` cleanly raises `RuntimeError` if real Docker execution is attempted without runtime; transparently routes through the deterministic Simulator adapter, emitting full ATIF v1.8 trajectories without fabricating Docker execution.

### 2.2. Bifrost Model Gateway
- **Configuration Check:**
  - `ENABLE_BIFROST_GATEWAY`: `False`
  - `BIFROST_ENDPOINT`: `http://localhost:8080/v1`
  - `BIFROST_API_KEY`: Not set (`""`)
- **Adapter Probe Output:**
  ```json
  {
    "configured": false,
    "status": "DISABLED",
    "endpoint": "http://localhost:8080/v1",
    "mode": "MOCK",
    "message": "Bifrost Gateway disabled. Running in local stub mode (mode=MOCK, fallback_used=True)."
  }
  ```
- **Boundary Classification:** **`BLOCKED_BY_CREDENTIALS` / `BLOCKED_BY_INFRASTRUCTURE`**
- **Fail-Safe Mechanism:** Falls back cleanly to local stub telemetry (`mode='MOCK'`, `fallback_used=True`). When enabled with live credentials, injects `x-bf-lh-*` correlation headers across upstream model requests.

### 2.3. Tavily Web Research Tool
- **Configuration Check:**
  - `TAVILY_API_KEY`: Not set (`""`)
- **Adapter Probe Output:**
  ```json
  {
    "name": "Tavily Web Search",
    "configured": false,
    "status": "NOT_CONFIGURED",
    "api_base": "https://api.tavily.com",
    "timeout_seconds": 30.0,
    "has_credentials": false,
    "total_events_captured": 0
  }
  ```
- **Boundary Classification:** **`BLOCKED_BY_CREDENTIALS`**
- **Fail-Safe Mechanism:** The diagnostic endpoint reports `NOT_CONFIGURED`. Missing credentials degrade gracefully and never crash the application or pollute the benchmark database with synthetic search results.

---

## 3. Subsystem Classification Matrix

| Capability / Subsystem | Execution Category | Active Component | Provenance Label |
|---|---|---|---|
| **Harbor Container Sandbox** | BLOCKED_BY_INFRASTRUCTURE | `backend/app/adapters/harbor/adapter.py` | `REAL_EXECUTION` (when active) / `SIMULATOR` (fallback) |
| **Deterministic Reference Harness** | DETERMINISTIC_HARNESS | `backend/app/services/runner.py` | `DETERMINISTIC_HARNESS` |
| **Bifrost Model Gateway** | BLOCKED_BY_CREDENTIALS (MOCK Stub) | `backend/app/adapters/gateways/bifrost.py` | `GATEWAY` (live) / `MOCK` (stub) |
| **Tavily Web Search Tool** | BLOCKED_BY_CREDENTIALS | `backend/app/adapters/tools/tavily/*` | `TAVILY` |
| **Controlled Fault Injection** | DETERMINISTIC_HARNESS | `backend/app/faults/engine.py` | `DETERMINISTIC_HARNESS` |
| **Failure Taxonomy Classifier** | EVALUATION_ENGINE | `backend/app/evaluation/taxonomy.py` | `EVALUATION_ENGINE` |
| **Statistical Metrics Engine** | EVALUATION_ENGINE | `backend/app/evaluation/metrics.py` | `EVALUATION_ENGINE` |
| **ATIF Trajectory v1.8 Engine** | TELEMETRY_PIPELINE | `backend/app/schemas/atif.py` | `ATIF-v1.8` |
| **Interactive UI Guided Tour** | USER_EXPERIENCE | `frontend/src/components/tour/*` | `UI_ONBOARDING` |

---

## 4. Acceptance Test Evidence & Verification Records

### 4.1. Acceptance Test A — Normal Execution Pipeline
- **Execution Mode:** `DETERMINISTIC_HARNESS` / `SIMULATOR`
- **Agent Evaluated:** Reference Tool Agent (`profile=resilient`)
- **Benchmark Pack:** `tool_recovery_challenges` (3 plan steps, tool dependencies, state assertions)
- **Persisted Artifacts:**
  - ATIF v1.8 JSON file emitted to `artifacts/trajectories/trial_{trial_id}.json`
  - Model telemetry: `ModelRequestEvent` (prompt tokens: 1450, completion tokens: 200, total: 1650, cost: $0.0036)
  - Tool telemetry: `ToolEvent` (primary tool: `run_shell_command`, write tool: `write_file`)
- **Verifier Outcome:** Machine-checked assertions verified cleanly (Reward: 1.0, Status: `PASSED`).

### 4.2. Acceptance Test B — Controlled Failure Injection & Scientific Recovery
- **Execution Mode:** `DETERMINISTIC_HARNESS`
- **Fault Vector Injected:** `TOOL_ERROR` at Step 2 (`run_shell_command`)
- **Fragile Agent Result:**
  - Observed fault -> failed to catch exception -> execution terminated.
  - Classification: `TOOL_CONTRACT` failure.
  - Recovery Rate: 0.0%.
- **Resilient Agent Result:**
  - Observed fault -> engaged fallback tool (`write_file`) -> continued execution -> final verifier passed.
  - Classification: `RECOVERED`.
  - Recovery Rate: 100.0%.
- **Validation:** Recovery strictly required that the fault was injected, execution continued, and the final verifier passed.

### 4.3. Acceptance Test C — Multi-Trial Statistical Reliability
- **Execution Mode:** `DETERMINISTIC_HARNESS`
- **Repetitions ($k$):** 3 and 5 independent trials evaluated.
- **Computed Statistical Metrics:**
  - Pass Rate ($\hat{p} = s/n$)
  - Wilson Score 95% Confidence Interval: Verified lower and upper bounds respect $[0.0, 1.0]$.
  - Pass@k ($1 - \binom{n-s}{k}/\binom{n}{k}$): Unbiased finite-sample estimator. Returns `null` if $n < k$.
  - Pass^k ($\binom{s}{k}/\binom{n}{k}$): Exact finite-sample probability that all $k$ attempts succeed.
  - Duration Metrics: Mean, Median (P50), P90, P95, and Sample Variance.
  - Cost per Success: Measured USD / successful tasks.

### 4.4. Acceptance Test D — Side-by-Side Agent Comparison Engine
- **Compared Profiles:** Fragile Baseline vs. Resilient Fallback
- **Equivalence Verification:** Guardrails confirmed identical task definition, verifier, repetition count, and fault severity.
- **Delta Analysis:**
  - Pass Rate: Fragile (0.0%) vs Resilient (100.0%)
  - Recovery Rate: Fragile (0.0%) vs Resilient (100.0%)
  - Remediation Hint: Recommends retry strategy with exponential backoff and alternate tool fallback.

---

## 5. Deployment Readiness & Boundaries

- **Single Vercel Project:** Fully configured via `vercel.json` with multi-service routing (`frontend` Vite + `backend` FastAPI with `main.py` entrypoint).
- **Same-Origin API:** Rewrites eliminate CORS friction across `/api/v1/*`, `/docs`, `/openapi.json`, and `/redoc`.
- **Database Boundary:**
  - Local SQLite in development.
  - Production requires Managed PostgreSQL (`DATABASE_URL=postgresql://...`), which automatically activates `NullPool` for serverless lifecycle management.
- **Artifact Boundary:**
  - Local filesystem in development.
  - Production requires Vercel Blob (`STORAGE_PROVIDER=vercel_blob`, `BLOB_READ_WRITE_TOKEN`), preventing ephemeral data loss on serverless cold starts.
- **Harbor Execution Boundary:**
  - Vercel Serverless Functions do not run Docker daemons.
  - Native containerized Harbor executions require dedicated worker hosts connected via `EXECUTION_WORKER_URL` and `EXECUTION_WORKER_SECRET`.
