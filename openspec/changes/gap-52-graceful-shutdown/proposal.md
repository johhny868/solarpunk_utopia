# GAP-52: Graceful Shutdown

**Status:** Draft
**Priority:** P2 - Operations
**Effort:** 2-3 hours

## Problem

SIGTERM kills process immediately, potentially corrupting data.

## Solution

Handle shutdown signals:

```python
import signal
import asyncio

shutdown_event = asyncio.Event()

async def shutdown():
    logger.info("Shutting down gracefully...")

    # Stop accepting new requests
    # (handled by uvicorn)

    # Finish in-progress requests (30s timeout)
    await asyncio.sleep(30)

    # Close database connections
    await db.close()

    # Drain queues
    await bundle_queue.drain()

    # Cancel background tasks
    for task in background_tasks:
        task.cancel()

    logger.info("Shutdown complete")

def handle_sigterm(signum, frame):
    asyncio.create_task(shutdown())

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)
```

## Tasks

1. Add signal handlers
2. Implement graceful queue drain
3. Close DB connections cleanly
4. Test with SIGTERM

## Success Criteria

- [ ] SIGTERM triggers graceful shutdown
- [ ] In-flight requests complete
- [ ] DB connections closed
- [ ] Queues drained
