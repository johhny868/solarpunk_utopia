# GAP-50: Logging System

**Status:** Draft
**Priority:** P2 - Operations
**Effort:** 3-4 hours

## Problem

No structured logging. Debugging requires print statements.

## Solution

Add structlog:

```python
import structlog

logger = structlog.get_logger()

# Structured logging
logger.info("proposal_approved",
    proposal_id=proposal_id,
    user_id=user_id,
    agent_type=agent.type
)

# Outputs JSON for easy parsing:
# {"event": "proposal_approved", "proposal_id": "xxx", "user_id": "yyy", ...}
```

Configure levels:

```python
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.getLevelName(os.getenv("LOG_LEVEL", "INFO"))
    )
)
```

## Tasks

1. Add structlog dependency
2. Configure in app startup
3. Replace print statements with logger
4. Add request correlation IDs (ties to GAP-53)

## Success Criteria

- [ ] Structured JSON logs
- [ ] Configurable log level
- [ ] No print statements in production code
