# Reliabench Core Implementation Audit

Date: 2026-11-13  
Status: Pre-Integration Baseline Audit

---

## 1. Feature Classification Matrix

| Feature / Subsystem | Status | Relevant Files | Existing Implementation | Missing Logic / Needs | Dependencies | Tests Available | Next Action |
|---|---|---|---|---|---|---|---|
| **Clean-State Data Baseline** | IMPLEMENTED_AND_TESTED | `backend/app/main.py`, `backend/app/cli.py` | Demo seed removed, 0 records on start, CLI `clean-demo-data` | Safe FK-aware clean test for preserving real runs | SQLite / Postgres | `test_api.py`, `test_schema_smoke.py` | Add dedicated preservation test |
| **YAML Benchmark Catalog** | IMPLEMENTED_AND_TESTED | `backend/app/benchmarks/pack.py`, `benchmark_tasks/packs/*.yaml` | 6 challenge packs loaded dynamically | Web research tasks requiring real external tools | PyYAML | `test_pack_loader.py` | Add Tavily research packs |
| **Deterministic Fault Engine** | IMPLEMENTED_AND_TESTED | `backend/app/faults/engine.py`, `backend/app/faults/catalog.py` | PRNG seeded injection (`TOOL_ERROR`, `TOOL_TIMEOUT`, etc.) | Tavily & Bifrost specific fault vectors (rate limits, malformed responses) | None | `test_fault_engine.py` | Support tool-specific fault configs |
| **Taxonomy & Metrics** | IMPLEMENTED_AND_TESTED | `backend/app/evaluation/metrics.py`, `backend/app/evaluation/taxonomy.py` | Wilson score intervals, finite-sample $pass@k$, $pass^k$ | Macro vs micro task aggregation clarity | Math / scipy | `test_metrics.py`, `test_taxonomy.py` | Expose both aggregations in API |
| **Regression Gate Registry** | IMPLEMENTED_AND_TESTED | `backend/app/services/regression.py` | Clean in-memory store with `replay_case`, `replay_all` | Persistent DB storage for promoted regression gates | SQLAlchemy | `test_regressions.py` | Keep clean-state & persist |
| **Tavily Web Search Tool** | NOT_IMPLEMENTED | `backend/app/adapters/tools/tavily/*` | None | Client, schemas, error handling, telemetry, tool definition, health check | `TAVILY_API_KEY`, httpx | None | Build full Tavily adapter module |
| **Bifrost Model Gateway** | PARTIALLY_IMPLEMENTED | `backend/app/adapters/gateways/bifrost.py` | Basic mock/httpx client with fallback | Correlation headers (`x-bf-lh-*`), telemetry collector, admin/provider config, log correlation | `BIFROST_ENDPOINT` | In runner tests (stub) | Build full gateway adapter & correlation |
| **Harbor Execution Engine** | IMPLEMENTED_BUT_INFRASTRUCTURE_BLOCKED | `backend/app/adapters/harbor/adapter.py` | Subprocess command builder & availability probe | Docker container isolation requires host daemon | Docker, Harbor CLI | `test_harbor_adapter.py` | Keep cleanly separated as execution plane |
| **Unified Telemetry & Event Model** | PARTIALLY_IMPLEMENTED | `backend/app/models/entities.py`, `backend/app/schemas/atif.py` | Models for Experiment, Run, Trial, Trajectory | Direct linking of ToolEvents, ModelRequests, SearchEvents | SQLAlchemy | Entity tests | Expand DB models for granular tool/gateway events |
| **Frontend Diagnostics & Settings** | PARTIALLY_IMPLEMENTED | `frontend/src/pages/SettingsPage.tsx` | Harbor & Bifrost status display | Tavily health card, Test Connection buttons, key status | React, Lucide | Build tests | Enhance Settings with Tavily & test triggers |

---

## 2. Dependency Architecture Map

```
Control Plane (FastAPI + React):
┌─────────────────────────┐
│     React Frontend      │
│  (Vite SPA /app/*)      │
└────────────┬────────────┘
             │ HTTP /api/v1/*
             ▼
┌─────────────────────────┐
│     FastAPI Router      │
│  (api_v1 + reliability) │
└────────────┬────────────┘
             │
   ┌─────────┴───────────────────────┐
   ▼                                 ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│  Experiment Orchestrator │    │    Reliability Runner    │
│  (Durable Job / Service) │    │  (Deterministic Harness) │
└────────────┬─────────────┘    └────────────┬─────────────┘
             │                               │
             ▼                               ▼
┌──────────────────────────────────────────────────────────┐
│                     Agent Adapters                       │
│      (ReferenceAgent / CliAgent / HttpAgent / Harbor)    │
└────────────┬───────────────────────────────┬─────────────┘
             │                               │
    Model Calls (when enabled)      Tool Calls (Search)
             │                               │
             ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│  Bifrost Model Gateway   │    │      Tavily Search       │
│  - x-bf-lh-* correlation │    │  - Query & Snippets      │
│  - Token / Cost telemetry│    │  - Domain filters        │
│  - Fallback & Retries    │    │  - Latency & Errors      │
└────────────┬─────────────┘    └────────────┬─────────────┘
             │                               │
             └───────────────┬───────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│                 Unified Event Telemetry                  │
│   (Trial ──> ToolEvents / ModelRequests / ATIF Traj)     │
└────────────────────────────┬─────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│             Evaluation & Metrics Engine                  │
│       - Verifiers (Deterministic + Ground Truth)         │
│       - Wilson CI, Pass@k, Pass^k, Recovery Rate         │
└──────────────────────────────────────────────────────────┘
```
