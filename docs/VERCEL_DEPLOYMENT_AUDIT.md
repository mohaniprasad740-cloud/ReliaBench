# VERCEL DEPLOYMENT AUDIT — RELIABENCH

**Project:** Reliabench (Global AI Hackathon | PS02: AI Agent Benchmarking Platform)  
**Date:** November 2026  
**Target:** Single Vercel Project Deployment (One Repo → One Project → One Domain → One Production Deployment)

---

## 1. Current Frontend Build Process

- **Framework**: React 19 (`^19.3.1`) + TypeScript (`~7.0.2`) + Vite (`^8.3.6`) + Tailwind CSS v4 (`@tailwindcss/vite`).
- **Build Command**: `cd frontend && npm run build` (runs `tsc -b && vite build`).
- **Output Directory**: `frontend/dist`.
- **Bundle Analysis**:
  - `dist/index.html` (~0.45 kB)
  - `dist/assets/index-*.css` (~29.6 kB)
  - `dist/assets/index-*.js` (~756.8 kB)
- **Status**: Tested and building cleanly with zero errors in ~1.5s.

---

## 2. Current Backend Application Entrypoint

- **Framework**: Python 3.10+ / FastAPI (`>=0.115.0`) with ASGI server Uvicorn (`>=0.32.0`).
- **Entrypoint**: `backend/app/main.py:app`.
- **Application Structure**:
  - `app.main:app` mounts:
    - `api_v1_router` at prefix `/api/v1` (`backend/app/api/routes/api_v1.py`)
    - `reliability_router` at prefix `/api/v1` (`backend/app/api/routes/reliability.py`)
  - Direct routes on `app`:
    - `GET /` -> Platform metadata and health links.
    - `GET /docs` -> OpenAPI Swagger documentation.
    - `GET /redoc` -> OpenAPI ReDoc documentation.
- **Serverless Entrypoint**: In Vercel's standard Python runtime, functions placed in `/api/*.py` export `app`. An entrypoint at `/api/index.py` that imports `from app.main import app` or mounts `app` provides full serverless compatibility.

---

## 3. API Routing Behavior & Same-Origin Pathing

- **Frontend API Base**: `frontend/src/services/api.ts` defines `const API_BASE = '/api/v1';`.
- **Routing**: Every frontend request issues relative calls (`/api/v1/health`, `/api/v1/agents`, etc.).
- **Vite Dev Mode**: Proxies `/api` -> `http://127.0.0.1:8000` with `changeOrigin: true`.
- **Production Mode on Vercel**: All `/api/*` and `/docs` requests route to the FastAPI serverless function, while all static assets and SPA routes (`/`, `/app`, `/app/*`) route to the frontend static output. No separate API domain or hardcoded localhost URLs.

---

## 4. Database Compatibility

- **Current State**: Defaults to local SQLite (`sqlite:///./reliabench.db`) via `DATABASE_URL`.
- **Serverless Limitation**: Vercel Functions are stateless and ephemeral. Any write to a local `.db` file in serverless is discarded across cold starts and instances.
- **Production Solution**: Managed PostgreSQL (e.g., Neon PostgreSQL, Supabase, AWS RDS).
- **Driver**: `psycopg2-binary>=2.9.9` added to `requirements.txt`.
- **Connection Pooling**: SQLAlchemy `NullPool` configured for serverless execution to prevent connection exhaustion.
- **Migrations**: Existing `run_additive_migrations()` previously relied on SQLite-specific `PRAGMA table_info`. Updated to use dialect-agnostic `sqlalchemy.inspect(engine)` so additive migrations run safely on both SQLite and PostgreSQL.

---

## 5. Artifact Storage Behavior

- **Current State**: Wrote ATIF trajectories and run logs directly to local filesystem (`artifacts/trajectories/`).
- **Serverless Limitation**: Vercel does not provide durable writable filesystem storage (only transient, limited `/tmp` during execution).
- **Solution**: Pluggable storage abstraction (`backend/app/storage/`):
  - `LocalStorageProvider`: Uses local filesystem for development.
  - `VercelBlobStorageProvider` / `S3StorageProvider`: Stores ATIF trajectories and reports in durable cloud object storage.
  - Database fallback: Trajectory metadata and summary steps stored in PostgreSQL `trajectories` table.

---

## 6. Harbor & Docker Execution Compatibility

- **Current State**: `HarborAdapter` executes `harbor run` CLI subcommands inside Docker sandboxes.
- **Critical Architectural Limitation**: Vercel Functions have NO Docker daemon, NO container privilege, and execution timeouts (15s on Hobby, 60-300s on Pro).
- **Separation of Planes**:
  - **Control Plane (Vercel)**: Serves UI, registers candidate agents, browses challenge packs, queries telemetry, replays regression gates with deterministic agents.
  - **Execution Plane (Worker)**:
    - Deterministic harness execution runs within Vercel function limits.
    - Native Harbor Docker execution requires an external worker. If no external worker is configured, Harbor is cleanly reported as `CLI_NOT_INSTALLED / SIMULATOR_FALLBACK`, never fabricating execution results.

---

## 7. Bifrost Gateway Integration Requirements

- Controlled via `ENABLE_BIFROST_GATEWAY` and `BIFROST_ENDPOINT`.
- When disabled or unreachable, seamlessly operates in mock/stub attribution mode without breaking.

---

## 8. Runtime Dependencies & Function Limits

- Python 3.12 / 3.11 explicitly supported by Vercel's Python runtime.
- Lean production dependencies: `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `psycopg2-binary`, `PyYAML`, `httpx`, `python-dotenv`.
- Total uncompressed package footprint is well within Vercel's 250MB unzipped limit.

---

## 9. Environment Variables Audit

| Variable | Required | Secret | Purpose |
| :--- | :---: | :---: | :--- |
| `DATABASE_URL` | Yes (in Prod) | Yes | PostgreSQL connection URI (`postgresql://...`) |
| `PROJECT_NAME` | No | No | Platform branding (defaults to `Reliabench`) |
| `API_V1_PREFIX` | No | No | API route prefix (defaults to `/api/v1`) |
| `BLOB_READ_WRITE_TOKEN` | Optional | Yes | Vercel Blob token for durable artifact storage |
| `STORAGE_PROVIDER` | No | No | `local` (default) or `vercel_blob` |
| `ENABLE_BIFROST_GATEWAY`| No | No | Model gateway routing flag |
| `BIFROST_ENDPOINT` | No | No | Bifrost gateway URL |
| `HARBOR_BIN_PATH` | No | No | Path to harbor binary |

---

## 10. Recommended Deployment Architecture

**Single-Project Unified Vercel Deployment with Python Serverless Function (`api/index.py`) + Vite Frontend (`frontend/dist`)**:
- Build Phase: Builds frontend into `frontend/dist`.
- Route `/api/*` -> Python serverless function running FastAPI.
- Route `/docs`, `/openapi.json`, `/redoc` -> Python serverless function.
- Route static assets (`/assets/*`, `/favicon.svg`) -> `frontend/dist`.
- Route SPA fallback `/(.*)` -> `frontend/dist/index.html`.
- Result: **1 Repository -> 1 Vercel Project -> 1 Public Domain -> 0 CORS issues**.
