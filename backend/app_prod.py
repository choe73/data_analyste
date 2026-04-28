# Production entry point - delegates to app.main for full API.
# Render start command: uvicorn app_prod:app --host 0.0.0.0 --port $PORT
# v7 - force redeploy with bcrypt 72-byte fix and Dataset model sync

from app.main import app  # noqa: F401

__all__ = ["app"]
