"""
Bridge Node Application

Main FastAPI application for bridge node.
Integrates bridge services with DTN node.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router, initialize_services, shutdown_services

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown of bridge services.
    """
    # Startup
    logger.info("Starting bridge node application...")

    # Initialize bridge services
    await initialize_services(
        node_id="bridge_node_1",
        dtn_base_url="http://localhost:8000"
    )

    logger.info("Bridge node application started")

    yield

    # Shutdown
    logger.info("Shutting down bridge node application...")
    await shutdown_services()
    logger.info("Bridge node application stopped")


# Create FastAPI app
app = FastAPI(
    title="Solarpunk Bridge Node",
    description="Multi-AP mesh network bridge node management",
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

# Include bridge API router
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Solarpunk Bridge Node",
        "version": "1.0.0",
        "description": "Multi-AP mesh network bridge node",
        "endpoints": {
            "status": "/bridge/status",
            "network": "/bridge/network",
            "metrics": "/bridge/metrics",
            "sync": "/bridge/sync/stats",
            "mode": "/bridge/mode",
            "health": "/bridge/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mesh_network.bridge_node.main:app",
        host="0.0.0.0",
        port=8002,  # Different port from DTN (8000) and VF (8001)
        reload=True
    )
