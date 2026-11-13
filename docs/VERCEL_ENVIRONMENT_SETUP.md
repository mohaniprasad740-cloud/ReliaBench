# VERCEL ENVIRONMENT SETUP GUIDE — RELIABENCH

This document details every environment variable used by Reliabench in both local development and Vercel serverless deployment.

---

## 1. Environment Variables Matrix

| Variable Name | Required in Prod | Contains Secret | Allowed Values / Format | Description |
| :--- | :---: | :---: | :--- | :--- |
| `DATABASE_URL` | **YES** | **YES** | `postgresql://user:pass@host/db?sslmode=require` | Connection string for production managed PostgreSQL. |
| `PROJECT_NAME` | No | No | String (`Reliabench`) | Platform name header. |
| `API_V1_PREFIX` | No | No | String (`/api/v1`) | REST API route prefix. |
| `ENVIRONMENT` | No | No | `production` / `development` | Toggles security headers and CORS strictness. |
| `STORAGE_PROVIDER` | No | No | `local` / `vercel_blob` | Trajectory artifact storage driver. |
| `BLOB_READ_WRITE_TOKEN` | If using Blob | **YES** | `vercel_blob_rw_...` | Vercel Blob access token for durable artifact storage. |
| `ENABLE_BIFROST_GATEWAY`| No | No | `true` / `false` | Enable/disable Maxim Bifrost gateway proxying. |
| `BIFROST_ENDPOINT` | No | No | `http://host:port/v1` | URL for model request gateway. |
| `EXECUTION_WORKER_URL` | No | No | `https://worker.domain.com` | Optional remote Harbor Docker worker endpoint. |
| `EXECUTION_WORKER_SECRET`| No | **YES** | String | Secret key for worker heartbeat & dispatch authentication. |

---

## 2. Setting Up Variables on Vercel

### Via Vercel Dashboard
1. Go to **Project Settings** -> **Environment Variables**.
2. Add `DATABASE_URL`:
   - Paste your Neon or Supabase PostgreSQL connection string.
   - Select **Production**, **Preview**, and **Development**.
3. (Optional) If attaching Vercel Blob:
   - Go to the **Storage** tab in your Vercel Dashboard -> Create a new **Blob Store**.
   - Vercel automatically injects `BLOB_READ_WRITE_TOKEN` into your project environment.
   - Set `STORAGE_PROVIDER=vercel_blob`.

### Via Vercel CLI
```powershell
# Add Database URL
vercel env add DATABASE_URL production
# When prompted, paste: postgresql://...

# Add Storage Provider
vercel env add STORAGE_PROVIDER production
# When prompted, type: vercel_blob
```

---

## 3. Security Guidelines
- **NEVER** prefix database credentials, worker secrets, or tokens with `VITE_`.
- All variables configured in Vercel without the `VITE_` prefix remain securely locked to the Python serverless runtime (`api/index.py`) and are never leaked to client bundles.
