# VERCEL DEPLOYMENT ARCHITECTURE — RELIABENCH

**Architecture Selection:** Single-Project Hybrid Architecture (Vite Frontend Static Output + FastAPI Python Serverless Function)

---

## 1. Evaluation of Approaches

### Approach A: Vercel Services (`services` in `vercel.json`)
- **Description**: Monorepo-style deployment where multiple distinct services (frontend Vite + backend Python) are declared within a single project.
- **Evaluation**: Vercel Services is currently in restricted/closed beta or enterprise feature availability. It is not generally available across all personal/team Vercel accounts and its schema specification is subject to account-tier gates. Relying strictly on `services` would cause fatal validation errors on standard Vercel deployments.

### Approach B: Unified Single-Project Serverless Deployment (Selected)
- **Description**: Standard, battle-tested Vercel architecture:
  1. Frontend is built during the Vercel build step (`cd frontend && npm install && npm run build`).
  2. Backend is deployed as a Vercel Serverless Function under `api/index.py`, which imports the unified FastAPI application (`from backend.app.main import app`).
  3. `vercel.json` configures routes:
     - `/api/*`, `/docs`, `/openapi.json`, `/redoc` route directly to `api/index.py`.
     - Static assets (`/assets/*`, etc.) are served from `frontend/dist`.
     - All other SPA routes (`/`, `/app`, `/app/agents`, etc.) rewrite to `frontend/dist/index.html`.
- **Reason for Selection**:
  - 100% compatible with all Vercel accounts (Hobby, Pro, Enterprise).
  - Guarantees **ONE Repository → ONE Vercel Project → ONE Public Domain**.
  - All frontend API calls remain relative (`/api/v1/...`), with zero CORS friction.
  - Zero application rewrites required.

---

## 2. Directory Layout on Vercel

```
Reliabench/
├── api/
│   └── index.py               # Vercel Python entrypoint exporting FastAPI app
├── backend/
│   ├── app/
│   │   ├── main.py            # Existing FastAPI app
│   │   ├── api/routes/        # api_v1, reliability routers
│   │   ├── db/                # PostgreSQL serverless connection & migrations
│   │   ├── storage/           # Local / Vercel Blob abstraction
│   │   └── ...
│   └── requirements.txt       # Production dependencies
├── benchmark_tasks/
│   └── packs/                 # Bundled YAML benchmark packs
├── frontend/
│   ├── dist/                  # Built static output
│   ├── src/                   # React 19 + TypeScript app
│   └── package.json
├── vercel.json                # Single project routes & build configuration
└── requirements.txt           # Root requirements pointing to backend
```

---

## 3. Request Lifecycle

```
[User Browser]
      │
      ▼
https://reliabench.vercel.app/
      │
      ├── GET /assets/* ──────────► Vercel Edge CDN (frontend/dist/assets)
      ├── GET /app, /app/* ──────► Vercel Edge CDN (frontend/dist/index.html - SPA fallback)
      │
      ├── GET /api/v1/health ─────► api/index.py (FastAPI Serverless Function)
      │                                   │
      │                             [PostgreSQL] (Neon / Supabase via Pool)
      │                             [Challenge Packs] (YAML in bundle)
      │                             [Storage] (Vercel Blob / Local fallback)
      │
      └── GET /docs ──────────────► api/index.py (Swagger UI)
```
