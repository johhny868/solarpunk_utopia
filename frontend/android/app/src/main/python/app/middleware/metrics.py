"""
Prometheus Metrics Middleware (GAP-54)

Collects aggregate metrics about the DTN Bundle System:
- HTTP request counts and durations
- Bundle operations (created, received, forwarded, expired)
- Database query performance
- Background service health

Privacy: All metrics are AGGREGATE ONLY.
No individual user tracking, bundle contents, or PII.
"""

import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware


# === HTTP Request Metrics ===

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint']
)


# === DTN Bundle Metrics ===

bundles_created_total = Counter(
    'bundles_created_total',
    'Total bundles created',
    ['priority', 'audience']
)

bundles_received_total = Counter(
    'bundles_received_total',
    'Total bundles received from peers'
)

bundles_forwarded_total = Counter(
    'bundles_forwarded_total',
    'Total bundles forwarded to peers'
)

bundles_expired_total = Counter(
    'bundles_expired_total',
    'Total bundles expired due to TTL'
)

bundles_quarantined_total = Counter(
    'bundles_quarantined_total',
    'Total bundles quarantined',
    ['reason']
)

bundle_queue_size = Gauge(
    'bundle_queue_size',
    'Current number of bundles in each queue',
    ['queue']
)

bundle_storage_bytes = Gauge(
    'bundle_storage_bytes',
    'Total bytes used by bundle storage'
)


# === Database Metrics ===

db_queries_total = Counter(
    'db_queries_total',
    'Total database queries executed',
    ['operation']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    buckets=(.001, .0025, .005, .01, .025, .05, .1, .25, .5, 1.0)
)

db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Number of database connections in pool'
)


# === Background Service Metrics ===

background_service_runs_total = Counter(
    'background_service_runs_total',
    'Total background service runs',
    ['service']
)

background_service_errors_total = Counter(
    'background_service_errors_total',
    'Total background service errors',
    ['service']
)

background_service_duration_seconds = Histogram(
    'background_service_duration_seconds',
    'Background service run duration in seconds',
    ['service']
)

background_service_last_success_timestamp = Gauge(
    'background_service_last_success_timestamp',
    'Unix timestamp of last successful run',
    ['service']
)


# === Application Info ===

app_info = Info(
    'app',
    'Application information'
)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware that collects Prometheus metrics for HTTP requests.

    Tracks:
    - Request count by method, endpoint, and status code
    - Request duration by method and endpoint
    - Requests in progress by method and endpoint

    Privacy: Only tracks aggregate counts and durations.
    No user IDs, bundle contents, or PII.
    """

    def __init__(self, app, exclude_paths: set = None):
        """
        Initialize metrics middleware.

        Args:
            app: FastAPI application
            exclude_paths: Set of paths to exclude from metrics (e.g., /metrics, /health)
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or {'/metrics', '/health', '/live', '/ready'}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics"""

        # Skip metrics collection for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Simplify endpoint path for metrics (remove IDs)
        endpoint = self._simplify_path(request.url.path)
        method = request.method

        # Track requests in progress
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Measure request duration
        start_time = time.time()

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            # Track failed requests
            status = 500
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

            # Increment request counter
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()

            # Observe request duration
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

        return response

    def _simplify_path(self, path: str) -> str:
        """
        Simplify URL path for metrics by removing dynamic segments.

        Examples:
            /bundles/123abc -> /bundles/{id}
            /agents/settings/matchmaker -> /agents/settings/{name}
            /api/users/456/offers -> /api/users/{id}/offers

        This prevents metric cardinality explosion from unique IDs.
        """
        # Split path into segments
        segments = path.split('/')

        # Replace segments that look like IDs with placeholders
        simplified = []
        for segment in segments:
            if not segment:
                continue

            # Check if segment looks like an ID (hex, uuid, numeric)
            if self._looks_like_id(segment):
                simplified.append('{id}')
            else:
                simplified.append(segment)

        return '/' + '/'.join(simplified)

    def _looks_like_id(self, segment: str) -> bool:
        """Check if URL segment looks like a dynamic ID"""
        # UUIDs (with or without hyphens)
        if len(segment) >= 32 and all(c in '0123456789abcdef-' for c in segment.lower()):
            return True

        # Numeric IDs
        if segment.isdigit():
            return True

        # Short hex IDs (6+ chars, all hex)
        if len(segment) >= 6 and all(c in '0123456789abcdef' for c in segment.lower()):
            return True

        return False


async def metrics_endpoint():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format.
    Should be scraped by Prometheus server.

    Example prometheus.yml:
        scrape_configs:
          - job_name: 'dtn-bundle-system'
            static_configs:
              - targets: ['localhost:8000']
            metrics_path: '/metrics'
            scrape_interval: 15s
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def init_metrics(version: str = "1.0.0", node_id: str = "unknown"):
    """
    Initialize application info metrics.

    Should be called once at startup with application metadata.
    """
    app_info.info({
        'version': version,
        'node_id': node_id,
        'service': 'dtn-bundle-system'
    })
