# Reliabench Architecture & System Design

## 1. System Overview

**Reliabench** is a framework-independent benchmarking and reliability platform for autonomous AI agents. Unlike standard single-turn accuracy leaderboards, Reliabench rigorously assesses reliability through **repeated execution trials ($k$)**, **controlled failure injection**, **statistical recovery analysis**, **evidence-backed trace inspection (ATIF v1.8)**, and **unified event telemetry**.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       LAYER C — EVIDENCE & PRODUCT EXPERIENCE                    │
│  React 19 + Vite + TypeScript + Tailwind CSS                                    │
│                                                                                 │
│  [Dashboard] [Agents] [Benchmarks] [Experiments] [Traces] [Comparisons]         │
│  [Reports]   [Settings & Diagnostics] [14-Step Interactive Guided Tour]         │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                        │ HTTP / JSON REST APIs (/api/v1/*)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                  LAYER B — EVALUATION, RELIABILITY & TELEMETRY                  │
│  Python 3.13 + FastAPI + Pydantic v2 + SQLAlchemy + SQLite / Managed PostgreSQL │
│                                                                                 │
│  [API Routing & Configuration]                                                  │
│    |-- /api/v1 (health, agents, benchmarks, experiments, runs, events, export)  │
│    |-- /api/v1/reliability (challenge packs, taxonomy, regression suites)       │
│    |-- /api/v1/diagnostics (Bifrost & Tavily probe and connection tests)        │
│                                                                                 │
│  [Statistical Evaluation Engine]                                                │
│    |-- Wilson 95% Confidence Intervals, Pass@k, Pass^k, Recovery Rate           │
│    |-- Latency Percentiles (P50, P90, P95), Duration Variance, Cost per Success │
│    |-- Macro (unweighted per-task) & Micro (pooled trial) Task Aggregation      │
│                                                                                 │
│  [Controlled Failure Engine & Taxonomy]                                         │
│    |-- PRNG Seeded Injection (Tool errors, timeouts, rate limits, model outages)│
│    |-- 6-Tier Hierarchical Taxonomy Classifier with Remediation Hints           │
│                                                                                 │
│  [Unified Event Telemetry Pipeline]                                             │
│    |-- ToolEvent: Tool name, call ID, args, observation, latency, error status  │
│    |-- ModelRequestEvent: Provider, model, tokens, latency, fallback, headers   │
└───────────────────┬───────────────────────────────────┬─────────────────────────┘
                    │                                   │
                    ▼                                   ▼
┌───────────────────────────────────────┐   ┌─────────────────────────────────────┐
│          LAYER A — EXECUTION          │   │         PERSISTENT STORAGE          │
│  [Adapters]                           │   │  [Database]                         │
│    |-- HarborAdapter (CLI / Docker)   │   │    |-- Agents, BenchmarkTasks       │
│    |-- SimulatorAdapter (Fail-safe)   │   │    |-- Experiments (config_snapshot)│
│    |-- BifrostGateway (x-bf-lh-*)     │   │    |-- Runs, Trials                 │
│    |-- TavilySearch (Web Research)    │   │    |-- ToolEvents, ModelRequests    │
│  [Artifacts]                          │   │  [Artifact Storage]                 │
│    |-- ATIF v1.8 Trajectories         │   │    |-- artifacts/trajectories/*.json│
│    |-- Verifier & Stdout Logs         │   │    |-- artifacts/reports/*.csv      │
└───────────────────────────────────────┘   └─────────────────────────────────────┘
```

---

## 2. Layer Responsibilities & Architectural Boundaries

### Layer A — Execution Plane
- **Harbor Adapter (`app/adapters/harbor/adapter.py`)**: Subprocess argument array execution (`harbor run -p <task> -a <agent>`) in isolated Docker containers. Gracefully falls back to Simulator when Docker daemon or Harbor CLI is absent.
- **Bifrost Model Gateway (`app/adapters/gateways/bifrost.py`)**: Attaches `x-bf-lh-*` correlation headers, captures token and cost telemetry, and attributes model provider fallback events.
- **Tavily Web Research (`app/adapters/tools/tavily/`)**: Server-side client executing authenticated web research with query/domain metadata and HTTP error classification.

### Layer B — Evaluation & Telemetry
- **Failure Engine (`app/faults/engine.py`)**: Deterministic injection based on random seeds, steps, and tool filters.
- **Taxonomy Classifier (`app/evaluation/taxonomy.py`)**: Classifies failures by priority: `TIMEOUT` → `PLANNING_DEVIATION` → `VERIFIER_MISMATCH` → `RECOVERY_EXHAUSTED` → `TOOL_CONTRACT` → `UNKNOWN`.
- **Metrics Engine (`app/evaluation/metrics.py`)**: Pure mathematical functions for Wilson score confidence intervals, unbiased $Pass@k$, finite-sample $Pass^k$, macro/micro aggregation, latency percentiles (P50, P90, P95), and measured cost per success.

### Layer C — Evidence & Product Experience
- **Interactive Tour (`frontend/src/components/tour/`)**: 14-step spotlight walkthrough with SVG cutout masks, keyboard navigation, and auto-scrolling across all 9 workspaces.
- **Workspace Navigation**: Dashboard, Agents, Benchmarks, Experiments, Regressions, Comparisons, Traces, Reports, Settings.
- **Reproducibility**: Immutable configuration snapshot stored in `experiments.config_snapshot` with cloning and replay support.

---

## 3. Single-Project Deployment Architecture (Vercel)

Reliabench deploys from one GitHub repository as a **unified multi-service project** on Vercel:
- **`frontend` service**: Vite React 19 application (`root: "frontend"`, `framework: "vite"`).
- **`backend` service**: Python FastAPI server (`root: "backend"`, `framework: "fastapi"`, `entrypoint: "main.py"`).
- **Top-Level Rewrites**: Public routes `/api/*`, `/docs`, `/openapi.json`, and `/redoc` route directly to the backend service; all application paths (`/*`) route to the frontend SPA.
