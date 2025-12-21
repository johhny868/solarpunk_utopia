# GAP-49: Configuration Management

**Status:** Draft
**Priority:** P3 - Operations
**Effort:** 2-3 hours

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

1. Audit hardcoded values
2. Create Settings class
3. Replace hardcoded with settings.X
4. Update .env.example

## Success Criteria

- [ ] No hardcoded URLs
- [ ] Central config file
- [ ] .env.example documented
