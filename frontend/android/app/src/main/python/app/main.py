"""
DTN Bundle System Backend for Solarpunk Mesh Network

This is the core DTN (Delay-Tolerant Networking) bundle transport layer.
All payloads (offers, needs, files, indexes, queries) move as signed bundles
with TTL, priority, audience controls, and hop limits.

Key features:
- Content-addressed bundles with Ed25519 signing
- 6-queue lifecycle management (inbox, outbox, pending, delivered, expired, quarantine)
- TTL enforcement with automatic expiration
- Cache budget management with eviction policy
- Priority-based forwarding (emergency first)
- Audience enforcement (public, local, trusted, private)
- Hop limit tracking to prevent loops

API Endpoints:
- POST /bundles - Create new bundle
- GET /bundles - List bundles in queue
- POST /bundles/receive - Receive bundle from peer
- GET /sync/index - Get bundle index for sync
- POST /sync/push - Receive multiple bundles
- GET /sync/pull - Pull bundles for forwarding

Background Services:
- TTL enforcement (runs every 60 seconds)
- Cache budget enforcement (on-demand)
"""

import asyncio
import logging
import os
import signal
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .logging_config import configure_logging, get_logger
from .database import init_db, close_db
from .api import bundles_router, sync_router, agents_router
from .api.auth import router as auth_router
from .api.vouch import router as vouch_router
from .api.attestation import router as attestation_router
from .api.event_onboarding import router as onboarding_router
from .api.cells import router as cells_router
from .api.messages import router as messages_router
from .api.block import router as block_router
from .api.steward_dashboard import router as steward_router
from .api.panic import router as panic_router
from .api.sanctuary import router as sanctuary_router
from .api.rapid_response import router as rapid_response_router
from .api.economic_withdrawal import router as economic_withdrawal_router
from .api.resilience_metrics import router as resilience_router
from .api.saturnalia import router as saturnalia_router
from .api.ancestor_voting import router as ancestor_voting_router
from .api.mycelial_strike import router as mycelial_strike_router
from .api.knowledge_osmosis import router as knowledge_osmosis_router
from .api.algorithmic_transparency import router as algorithmic_transparency_router
from .api.temporal_justice import router as temporal_justice_router
from .api.accessibility import router as accessibility_router
from .api.language_justice import router as language_justice_router
from .api.care_outreach import router as care_outreach_router
from .api.mycelial_health import router as mycelial_health_router
from .api.group_formation import router as group_formation_router
from .api.fork_rights import router as fork_rights_router
from .api.security_status import router as security_status_router
from .api.mourning import router as mourning_router
from .api.node_config import router as node_config_router
from .services import TTLService, CryptoService, CacheService
from .services.node_config_service import get_node_config_service
from .middleware import CSRFMiddleware, PrometheusMetricsMiddleware, metrics_endpoint, init_metrics
from .middleware.correlation_id import CorrelationIdMiddleware
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mesh_naming.mesh_dns import get_mesh_naming

# Configure structured logging
configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)
logger = get_logger(__name__)

# Global services
ttl_service: TTLService = None
crypto_service: CryptoService = None
cache_service: CacheService = None

# Shutdown coordination (GAP-52)
shutdown_event = asyncio.Event()
_shutdown_initiated = False


def handle_shutdown_signal(signum, frame):
    """
    Signal handler for graceful shutdown (GAP-52).

    Called when SIGTERM or SIGINT is received.
    Sets the shutdown event to trigger graceful shutdown.
    """
    global _shutdown_initiated

    if _shutdown_initiated:
        logger.warning("Shutdown already initiated, ignoring repeated signal")
        return

    signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
    logger.info(f"Received {signal_name}, initiating graceful shutdown...")
    _shutdown_initiated = True
    shutdown_event.set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Handles startup and shutdown of background services.
    """
    global ttl_service, crypto_service, cache_service

    # Startup
    logger.info("Starting DTN Bundle System...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize crypto service (loads or generates keypair)
    crypto_service = CryptoService()
    fingerprint = crypto_service.get_public_key_fingerprint()
    logger.info(f"Crypto service initialized (fingerprint: {fingerprint})")

    # Initialize cache service (use config for budget)
    cache_budget_bytes = settings.cache_budget_mb * 1024 * 1024
    cache_service = CacheService(storage_budget_bytes=cache_budget_bytes)
    cache_stats = await cache_service.get_cache_stats()
    logger.info(f"Cache service initialized (budget: {cache_stats['budget_bytes']} bytes)")

    # Start TTL enforcement service (use config for interval)
    ttl_service = TTLService(check_interval_seconds=settings.ttl_check_interval_seconds)
    await ttl_service.start()

    # Register signal handlers for graceful shutdown (GAP-52)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    logger.info("Signal handlers registered for graceful shutdown")

    # Initialize Prometheus metrics (GAP-54)
    init_metrics(version="1.0.0", node_id=fingerprint)
    logger.info("Prometheus metrics initialized")

    # Initialize mesh naming if node is configured
    try:
        node_config_service = get_node_config_service()
        node_config = node_config_service.get_config()

        if node_config:
            # Initialize mesh naming with node config
            mesh_naming = get_mesh_naming(
                node_name=node_config.mesh_name,
                community_name=node_config.community_name,
            )

            # Announce on the network if AI inference or bridge mode enabled
            if node_config.enable_ai_inference or node_config.enable_bridge_mode:
                mesh_naming.announce(
                    dtn_port=settings.port,
                    valueflows_port=8001,
                    ai_port=8005,
                )
                logger.info(
                    "mesh_announced",
                    mesh_name=node_config.mesh_fqdn,
                    ai_enabled=node_config.enable_ai_inference,
                    bridge_enabled=node_config.enable_bridge_mode,
                )
    except Exception as e:
        logger.warning("mesh_naming_initialization_failed", error=str(e))
        # Continue startup even if mesh naming fails

    logger.info("DTN Bundle System started successfully")
    logger.info("=" * 60)
    logger.info(f"API available at http://{settings.host}:{settings.port}")
    logger.info(f"Docs available at http://{settings.host}:{settings.port}/docs")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("=" * 60)

    yield

    # Shutdown (GAP-52: Enhanced graceful shutdown)
    logger.info("Shutting down DTN Bundle System...")

    # Give in-flight requests a chance to complete (up to 30 seconds)
    # Uvicorn will stop accepting new connections automatically
    logger.info("Waiting for in-flight requests to complete (max 30s)...")
    try:
        await asyncio.wait_for(asyncio.sleep(0.1), timeout=30.0)
    except asyncio.TimeoutError:
        logger.warning("Timed out waiting for requests, proceeding with shutdown")

    # Stop background services
    logger.info("Stopping background services...")
    if ttl_service:
        await ttl_service.stop()
        logger.info("TTL service stopped")

    # Shutdown mesh naming if active
    try:
        mesh_naming = get_mesh_naming()
        if mesh_naming:
            mesh_naming.shutdown()
            logger.info("Mesh naming service stopped")
    except:
        pass

    # Close database connections
    logger.info("Closing database connections...")
    await close_db()
    logger.info("Database connections closed")

    logger.info("DTN Bundle System shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="DTN Bundle System",
    description="Delay-Tolerant Networking bundle transport for Solarpunk mesh network",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (GAP-41: Secure CORS configuration)
# Use config-managed allowed origins
allowed_origins = settings.allowed_origins
logger.info(f"CORS: Configured origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Correlation ID middleware (GAP-53: Request Tracing)
# Must be added before other middleware to ensure correlation IDs are available
app.add_middleware(CorrelationIdMiddleware)

# Prometheus Metrics middleware (GAP-54: Metrics Collection)
# Tracks HTTP requests, durations, and in-progress counts
app.add_middleware(PrometheusMetricsMiddleware)

# CSRF Protection middleware (GAP-56)
app.add_middleware(
    CSRFMiddleware,
    exempt_paths={
        "/",
        "/docs",
        "/openapi.json",
        "/health",
        "/node/info",
        "/node/config",  # Node configuration must be accessible before users exist
        "/node/config/status",
        "/auth/csrf-token",  # CSRF token endpoint must be exempt
        "/auth/register",  # Registration should be exempt
        "/auth/login",  # Login should be exempt
    }
)

# Register routers
app.include_router(bundles_router)
app.include_router(sync_router)
app.include_router(agents_router)
app.include_router(auth_router)
app.include_router(vouch_router)
app.include_router(attestation_router)
app.include_router(onboarding_router)
app.include_router(cells_router)
app.include_router(messages_router)
app.include_router(block_router)
app.include_router(steward_router)
app.include_router(panic_router)
app.include_router(sanctuary_router)
app.include_router(rapid_response_router)
app.include_router(economic_withdrawal_router)
app.include_router(resilience_router)
app.include_router(saturnalia_router)
app.include_router(ancestor_voting_router)
app.include_router(mycelial_strike_router)
app.include_router(knowledge_osmosis_router)
app.include_router(mycelial_health_router)
app.include_router(group_formation_router)
app.include_router(algorithmic_transparency_router)
app.include_router(temporal_justice_router)
app.include_router(accessibility_router)
app.include_router(language_justice_router)
app.include_router(care_outreach_router)
app.include_router(fork_rights_router)
app.include_router(security_status_router)
app.include_router(mourning_router)
app.include_router(node_config_router)


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "service": "DTN Bundle System",
        "version": "1.0.0",
        "description": "Delay-Tolerant Networking bundle transport for Solarpunk mesh network",
        "docs": "/docs",
        "endpoints": {
            "bundles": "/bundles",
            "sync": "/sync",
            "agents": "/agents",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """
    Health check endpoint (GAP-51).
    Returns 503 if any dependency is unhealthy, 200 otherwise.
    """
    from .services.health_check import HealthCheckService, HealthStatus
    from fastapi import Response
    import json

    health_result = await HealthCheckService.health_check()

    # Return 503 if unhealthy
    status_code = 200 if health_result["status"] == HealthStatus.HEALTHY else 503

    return Response(
        content=json.dumps(health_result),
        status_code=status_code,
        media_type="application/json"
    )


@app.get("/ready")
async def readiness():
    """
    Kubernetes readiness probe endpoint (GAP-51).
    Returns 503 if service is not ready to accept traffic.
    """
    from .services.health_check import HealthCheckService
    from fastapi import Response
    import json

    ready_result = await HealthCheckService.readiness_check()
    status_code = 200 if ready_result["ready"] else 503

    return Response(
        content=json.dumps(ready_result),
        status_code=status_code,
        media_type="application/json"
    )


@app.get("/live")
async def liveness():
    """
    Kubernetes liveness probe endpoint (GAP-51).
    Returns 200 if service is alive and responsive.
    """
    from .services.health_check import HealthCheckService

    return await HealthCheckService.liveness_check()


@app.get("/node/info")
async def node_info():
    """Get information about this node"""
    global crypto_service

    fingerprint = crypto_service.get_public_key_fingerprint()
    public_key = crypto_service.get_public_key_pem()

    return {
        "node_id": fingerprint,
        "public_key_fingerprint": fingerprint,
        "public_key": public_key,
        "version": "1.0.0"
    }


@app.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint (GAP-54).

    Returns metrics in Prometheus text format for scraping.
    Includes HTTP request metrics, bundle metrics, and service health.

    Example prometheus.yml:
        scrape_configs:
          - job_name: 'dtn-bundle-system'
            static_configs:
              - targets: ['localhost:8000']
            metrics_path: '/metrics'
            scrape_interval: 15s
    """
    return await metrics_endpoint()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
