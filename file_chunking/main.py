"""
File Chunking System - Main Application

FastAPI application for file chunking with DTN integration.
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, close_db
from .api import files_router, chunks_router, downloads_router, library_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Handles startup and shutdown of background services.
    """
    # Startup
    logger.info("Starting File Chunking System...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    logger.info("File Chunking System started successfully")
    logger.info("=" * 60)
    logger.info("API available at http://localhost:8001")
    logger.info("Docs available at http://localhost:8001/docs")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Shutting down File Chunking System...")

    # Close database
    await close_db()

    logger.info("File Chunking System shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="File Chunking System",
    description="Content-addressed file chunking with DTN integration for Solarpunk mesh network",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
# Get allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS")

if not allowed_origins_str:
    # Development defaults (localhost only)
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    logger.warning("ALLOWED_ORIGINS not set, using development defaults: %s", allowed_origins)
else:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
    logger.info("CORS configured for origins: %s", allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Explicit list from env or dev defaults
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register routers
app.include_router(files_router)
app.include_router(chunks_router)
app.include_router(downloads_router)
app.include_router(library_router)


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "service": "File Chunking System",
        "version": "1.0.0",
        "description": "Content-addressed file chunking with DTN integration",
        "docs": "/docs",
        "endpoints": {
            "files": "/files",
            "chunks": "/chunks",
            "downloads": "/downloads",
            "library": "/library",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    from .services import ChunkStorageService, LibraryCacheService

    chunk_storage = ChunkStorageService()
    library_cache = LibraryCacheService(chunk_storage)

    # Get storage stats
    storage_stats = await chunk_storage.get_storage_stats()

    # Get cache stats
    cache_stats = await library_cache.get_cache_stats()

    return {
        "status": "healthy",
        "storage": {
            "total_chunks": storage_stats["total_chunks"],
            "total_size_mb": storage_stats["total_size_mb"]
        },
        "cache": {
            "total_files": cache_stats.get("total_files", 0),
            "total_size_gb": cache_stats.get("total_size_gb", 0.0),
            "usage_percentage": cache_stats.get("usage_percentage", 0.0)
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "file_chunking.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
