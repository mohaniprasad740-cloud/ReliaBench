"""
Entrypoint for Vercel and production deployment.
Exposes the FastAPI application directly from app.main.
"""
from app.main import app

__all__ = ["app"]
