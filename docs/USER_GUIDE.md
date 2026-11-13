# Reliabench — Complete User Guide & Product Manual

## 1. Executive Overview

**Reliabench** is an enterprise AI Agent Benchmarking & Reliability Platform designed around the core principle:  
*Same tasks. Same conditions. Measurable agent reliability.*

Unlike standard evaluation frameworks that measure only single-turn LLM benchmark accuracy, Reliabench subjects autonomous AI agents to repeated execution trials, controlled systemic failures (network partitions, tool errors, API rate limits, model outages), and computes defensible statistical reliability metrics (Wilson 95% Confidence Intervals, $Pass@k$, $Pass^k$, Recovery Rate, and Mean Duration).

---

## 2. Interactive Product Tour & Onboarding

Reliabench includes a built-in, 14-step interactive guided tour that walks users across every major capability of the platform.

### How to Start or Restart the Tour
- **Clean Workspace Onboarding**: On a fresh install or empty database, click the **"Start Guided Tour"** button prominently displayed on the Dashboard.
- **Top Navigation Bar**: Click the **"Product Tour"** button (with the help icon) in the navigation bar from anywhere in the application.
- **Dashboard Header**: Click the **"Product Tour"** compass button in the workspace header.

### Tour Features & Controls
- **Spotlight Mask**: Highlights the target element with a high-contrast focus border (`#C7D94C` Acid Lime) while dimming the background.
- **Contextual Tooltip**: Explains what the feature does, its operational relevance, and provides action recommendations.
- **Step Navigation**: Use the **"Next"** and **"Back"** buttons, or use the **Arrow Left** / **Arrow Right** keyboard shortcuts.
- **Dismiss / Skip**: Click the close button `✕`, the **"Skip Tour"** link, or press **Escape** at any time.
- **Automatic Route Switching**: The tour seamlessly navigates across application routes (Dashboard, Agents, Benchmarks, Experiments, Regressions, Comparisons, Traces, Reports, and Settings) and scrolls target elements into view.

---

## 3. Platform Navigation & Core Workspaces

### 3.1. Operational Dashboard (`/app`)
- **Key Reliability Metrics Strip**: Displays Overall Pass Rate, Mean Execution Duration, 95% Wilson Confidence Intervals, and Recovery Rate.
- **Provenance Source Filter**: Toggle between **All Data**, **Simulator Data Only**, and **Real Verified Runs** to distinguish isolated test harness runs from production executions.
- **Recent Experiments Table**: Shows the latest trials, repetition count ($k$), pass rates, and execution status.

### 3.2. Agent Registry (`/app/agents`)
- Register autonomous agents with custom invocation endpoints, system prompts, toolsets, and architecture profiles.
- Configure agent resilience strategies (Fragile Baseline vs. Resilient Fallback).
- Track agent metadata, versioning, and execution history.

### 3.3. Benchmark Challenge Library (`/app/benchmarks`)
- Access built-in challenge packs:
  - `web_research_tavily`: Web search and multi-source research tasks under search timeouts and invalid queries.
  - `tool_recovery_challenges`: Synthetic API failures, corrupted payloads, and retry verification.
  - Core algorithmic, reasoning, and multi-step tool execution packs.
- Inspect task preconditions, deterministic ground truths, and validation criteria.

### 3.4. Experiment Runner (`/app/experiments`)
- Configure multi-repetition benchmark runs with custom repetition count ($k$).
- Select active fault injection scenarios to evaluate error-handling behavior under stress.
- Monitor real-time execution progress and step-by-step trial results.

### 3.5. Regression Testing Engine (`/app/regressions`)
- Capture failed trials into persistent regression suites.
- Replay test cases deterministically after modifying agent prompts, models, or tool schemas to prevent regressions.
- Track pass/fail deltas across iterations.

### 3.6. Comparative Analytics (`/app/comparison`)
- Side-by-side agent reliability comparison across identical benchmark tasks and fault conditions.
- Contrast fragile baseline agents against resilient multi-model fallback architectures.
- Visual metric charts comparing Pass Rates, Latency, and Recovery Rates.

### 3.7. Execution Evidence & ATIF Traces (`/app/traces`)
- Deep observability into agent decision-making using the Agent Tool Interaction Format (ATIF).
- Inspect full step-by-step logs, model requests, tool calls, fault injections, and recovery attempts.
- Download raw JSON execution traces for auditing.

### 3.8. Benchmark Reports & Exports (`/app/reports`)
- Generate comprehensive compliance and benchmarking reports.
- Export trial data, metrics summaries, and trajectories in JSON and CSV formats.
- Share defensible reliability scorecards with stakeholders.

### 3.9. System Settings & Gateway Diagnostics (`/app/settings`)
- **Execution Adapters**: View status of Harbor container runtime and Simulator fallback adapter.
- **Bifrost Model Gateway**: Test connection and model routing with microsecond-level telemetry and token accounting.
- **Tavily Web Research Tool**: Verify search API connectivity, rate limits, and live query execution.
- **Database & Data Cleanup**: Maintain data integrity and purge test artifacts while preserving verified experiment runs.

---

## 4. Single-Project Vercel Deployment Architecture

Reliabench deploys as a **unified multi-service project** on Vercel:

```
[ Domain: https://reliabench.vercel.app ]
  ├── /api/(.*)        ──> Backend Service (FastAPI / Python)
  ├── /docs, /redoc    ──> FastAPI Interactive Documentation
  ├── /openapi.json    ──> OpenAPI Specification
  └── /(.*)            ──> Frontend Service (Vite / React 19)
```

- Configured via root `vercel.json` defining both `frontend` (Vite) and `backend` (FastAPI) services.
- Internal service isolation with top-level public URL rewriting.
- Zero CORS friction in production through same-origin routing.
