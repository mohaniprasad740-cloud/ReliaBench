# Reliabench Demo Environment Specification

## 1. Overview & Architecture

The **Reliabench Demo Environment** delivers an out-of-the-box, zero-credential demonstration experience for evaluators, hackathon judges, and team presenters. Anyone opening the deployed Vercel application can explore complete benchmarking telemetry, agent comparisons, fault recovery dynamics, and verifiable execution evidence without needing external API keys or local container infrastructure.

```
+-------------------------------------------------------------------------+
|                         Vercel Edge / Static CDN                        |
|   Landing Page ("Explore Demo") ----> Dashboard / Comparisons / Traces  |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|               Vercel Serverless Function (FastAPI API)                  |
|  /api/v1/demo/status | /api/v1/demo/seed | /api/v1/demo/reset           |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|               Database Persistence Layer (Postgres / SQLite)            |
| - 4 Canonical Demo Agents (Atlas, Nova, Sentinel, Swift)                |
| - 14 Tasks across 5 Suites (Web Research, Browser, Tools, Extract, Rec) |
| - 32 Multi-Trial Experiments (~160 Trials, exact Wilson CIs, Pass@k)   |
| - 160 ATIF v1.8 Trajectories persisted in summary_steps JSON           |
| - ToolEvent & ModelRequestEvent unified telemetry                      |
| - Safe Isolation: is_demo=True, source_mode="SIMULATOR"                |
+-------------------------------------------------------------------------+
```

---

## 2. Key Product Capabilities Demonstrated

1. **Persistent Visual Identification**:
   - Navigation header prominently features the `DEMO ENVIRONMENT · CANONICAL DATA` badge.
   - Clean indicators differentiate synthetic baseline runs (`SIMULATOR`) from native containerized executions (`REAL_EXECUTION`).

2. **One-Click Workspace Reset**:
   - Evaluators can reset the demo environment via the UI button in the Navbar or the REST endpoint `POST /api/v1/demo/reset`.
   - Idempotent UUID generation (`uuid.uuid5` with DNS namespace) guarantees deterministic IDs and prevents state accumulation.

3. **Serverless-Resilient Execution Traces**:
   - In ephemeral serverless environments (e.g., AWS Lambda, Vercel Functions), disk storage is read-only or ephemeral.
   - Reliabench persists complete ATIF v1.8 trajectory step arrays in the `trajectories.summary_steps` database column, ensuring trace exploration functions seamlessly anywhere.

4. **Safety & Zero Data Loss**:
   - All demo data is strictly partitioned by `is_demo = True`.
   - Production operations and reset commands filter solely on `is_demo == True`, guaranteeing zero data loss for user-registered agents or benchmark runs.

---

## 3. Entry Points

- **Landing Page**: Top navigation link and primary editorial showcase card with direct action button.
- **Navbar**: Persistent badge with tooltip description and one-click `Reset Demo` button.
- **Dashboard Clean State**: "Load Demo Workspace" button if the database is initially unpopulated.
- **REST API**: `/api/v1/demo/status`, `/api/v1/demo/seed`, `/api/v1/demo/reset`.
- **CLI**: `python -m app.cli seed-demo` and `python -m app.cli reset-demo`.

