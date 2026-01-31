"""
FastAPI Application Entry Point
"""

import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add src to path for importing existing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from .routers import sessions, videos, content
from .websocket.handler import router as websocket_router
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"Starting AI Movie Generator API v{settings.VERSION}")
    yield
    print("Shutting down...")


app = FastAPI(
    title="AI Movie Generator API",
    description="API for AI-driven video generation workflow",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(content.router, prefix="/api/sessions", tags=["content"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(websocket_router, tags=["websocket"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.VERSION}


@app.get("/api/config")
async def get_config():
    """Get public configuration."""
    return {
        "available_platforms": settings.AVAILABLE_PLATFORMS,
        "available_genres": settings.AVAILABLE_GENRES,
        "default_platform": settings.DEFAULT_PLATFORM,
        "max_episodes": settings.MAX_EPISODES,
        "max_characters": settings.MAX_CHARACTERS,
    }
