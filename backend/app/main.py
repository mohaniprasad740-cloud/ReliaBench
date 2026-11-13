import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.db.migrations import run_additive_migrations
from app.api.routes.api_v1 import router as api_v1_router
from app.api.routes.reliability import router as reliability_router

# Initialize database schema and run additive migrations safely
try:
    Base.metadata.create_all(bind=engine)
    run_additive_migrations(engine)
except Exception as e:
    # On serverless cold starts or read-only pools, avoid crashing process
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Reliabench: AI Agent Benchmarking & Reliability Platform (Global AI Hackathon | PS02)",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Policy: Restricted in production (same-domain), permissive for local dev
is_production = bool(os.getenv("VERCEL") or os.getenv("ENVIRONMENT") == "production")
if not is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Same-origin via Vercel rewrites; wildcard safe for public GET endpoints
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    )

app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
app.include_router(reliability_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "tagline": "Same tasks. Same conditions. Measurable agent reliability.",
        "status": "operational",
        "api_docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }
