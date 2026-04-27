# Production entry point - delegates to app.main for full API.
# Render start command: uvicorn app_prod:app --host 0.0.0.0 --port $PORT
# v2 - force redeploy

from app.main import app  # noqa: F401

__all__ = ["app"]
