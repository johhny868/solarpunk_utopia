# GAP-49: Configuration Management

**Status:** ✅ Implemented
**Priority:** P3 - Operations
**Effort:** 2-3 hours
**Completed:** 2025-12-20

## Problem

Hardcoded URLs and config scattered throughout codebase.

## Solution

Move to environment variables:

```python
# ❌ Hardcoded
VF_URL = "http://localhost:8001"

# ✅ Configurable
VF_URL = os.getenv("VF_SERVICE_URL", "http://localhost:8001")
```

Create central config:

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    vf_service_url: str = "http://localhost:8001"
    database_url: str = "sqlite:///app.db"
    jwt_secret: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

## Tasks

1. ✅ Audit hardcoded values
2. ✅ Create Settings class
3. ✅ Replace hardcoded with settings.X
4. ✅ Update .env.example

## Success Criteria

- [x] No hardcoded URLs in main.py files
- [x] Central config file (app/config.py, valueflows_node/app/config.py)
- [x] .env.example documented

## Implementation Summary

**Files Created:**
- `app/config.py` - Central configuration for DTN Bundle System using pydantic_settings
- `valueflows_node/app/config.py` - Central configuration for ValueFlows Node
- `.env.example` - Comprehensive documentation of all environment variables

**Files Modified:**
- `app/main.py` - Now uses settings for CORS origins, log level, cache budget, TTL interval
- `valueflows_node/app/main.py` - Now uses settings for CORS origins, log level

**Features:**
- Type-safe configuration with pydantic validation
- Environment variable parsing from .env file
- Comprehensive defaults for development
- Security warnings for production secrets
- Field validators for common mistakes (e.g., trust threshold bounds)
- Convenience functions for common config access
- Complete documentation in .env.example
