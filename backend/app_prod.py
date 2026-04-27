"""Production entry point - delegates to app.main for full API."""

# This file exists because Render's start command is configured as:
# uvicorn app_prod:app --host 0.0.0.0 --port $PORT
# We simply re-export the full app from app.main

from app.main import app  # noqa: F401

__all__ = ["app"]
