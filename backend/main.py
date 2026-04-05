"""
FastAPI application entry point.
"""

import sys
import os

# Add project root to path so backend modules can import config, llm_functions, etc.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware


class NoCacheStaticMiddleware(BaseHTTPMiddleware):
    """Disable browser caching for static files during development."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith(('/js/', '/css/')):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

from backend.routes import session, test_flow, audio

app = FastAPI(title="AI English Speaking Evaluator", version="1.0.0")

# No-cache for static files in development
app.add_middleware(NoCacheStaticMiddleware)

# CORS — allow local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(session.router)
app.include_router(test_flow.router)
app.include_router(audio.router)

# Serve frontend static files
frontend_dir = os.path.join(project_root, "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
