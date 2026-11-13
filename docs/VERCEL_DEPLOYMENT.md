# VERCEL DEPLOYMENT GUIDE — RELIABENCH

**Architecture:** Single-Project Unified Deployment (One Repo → One Vercel Project → One Domain)  
**Public URL Structure:**
- Frontend Web App: `https://<project-name>.vercel.app/`
- Operational Dashboard: `https://<project-name>.vercel.app/app`
- FastAPI REST Endpoints: `https://<project-name>.vercel.app/api/v1/health`
- Interactive OpenAPI Docs: `https://<project-name>.vercel.app/docs`

---

## 1. Prerequisites

1. **Node.js 18+** & npm
2. **Python 3.10+**
3. **Vercel Account**: [https://vercel.com/signup](https://vercel.com/signup)
4. **Managed PostgreSQL Database**:
   - Free instant options: [Neon PostgreSQL](https://neon.tech/) or [Supabase](https://supabase.com/).
   - Copy the connection URI: `postgresql://user:password@host/dbname?sslmode=require`.

---

## 2. Windows PowerShell Deployment Workflow

### Step 1: Install Vercel CLI (if not installed)
```powershell
npm install -g vercel
```

### Step 2: Authenticate with Vercel
```powershell
vercel login
```
*(Follow browser prompt to authenticate).*

### Step 3: Link Project to Vercel
Run from the root repository directory (`Reliabench`):
```powershell
vercel link
```
- Select your Vercel Scope / Team.
- Link to existing project? **No** (creates a new project, or **Yes** if existing).
- Project name: `reliabench` (or desired name).

### Step 4: Configure Production Environment Variables
Set your PostgreSQL database connection string:
```powershell
vercel env add DATABASE_URL production
```
*(When prompted, paste your PostgreSQL connection URI).*

*(Optional - Attach Vercel Blob for durable artifact storage)*:
In Vercel Dashboard -> Project -> Storage -> Create Blob Store, or set:
```powershell
vercel env add STORAGE_PROVIDER production
# Enter value: vercel_blob
```

### Step 5: Deploy Preview
```powershell
vercel
```
Vercel will output a unique Preview URL (e.g. `https://reliabench-git-feature-your-team.vercel.app`).

### Step 6: Deploy to Production
```powershell
vercel --prod
```
Vercel will build and deploy directly to your production domain:
`https://reliabench.vercel.app`.

---

## 3. Continuous Deployment via GitHub (Automated)

Once linked to GitHub:
1. Push to your repository:
   ```powershell
   git add .
   git commit -m "Configure single-project Vercel deployment"
   git push origin main
   ```
2. Vercel automatically detects the push, runs `cd frontend && npm install && npm run build`, packages the Python backend via `api/index.py`, and deploys to production.

---

## 4. Verification Checklist

After deployment succeeds, verify all endpoints on your production domain:

```powershell
$DOMAIN = "https://your-project.vercel.app"

# 1. Verify Frontend Landing Page
curl.exe -I "$DOMAIN/"

# 2. Verify Frontend SPA Route (Dashboard)
curl.exe -I "$DOMAIN/app"

# 3. Verify Backend FastAPI Health
curl.exe -s "$DOMAIN/api/v1/health"

# 4. Verify Challenge Packs Catalog
curl.exe -s "$DOMAIN/api/v1/packs"

# 5. Verify Swagger UI Docs
curl.exe -I "$DOMAIN/docs"
```

---

## 5. Troubleshooting & FAQ

- **500 Internal Server Error on `/api/*`**:
  Check Vercel Runtime Logs. Ensure `DATABASE_URL` is set to a valid PostgreSQL connection string accessible from the cloud.
- **SQLite Database Locked / Transient Data**:
  Ensure you are not running in SQLite mode on production. Serverless functions do not persist local `.db` files across requests. Set `DATABASE_URL` to PostgreSQL.
- **Harbor Execution Status**:
  Vercel serverless environments do not have a Docker daemon. The backend correctly reports Harbor mode as `SIMULATOR_FALLBACK / CLI_NOT_INSTALLED` for control-plane operation. For native Docker execution, connect an external worker via `EXECUTION_WORKER_URL`.
