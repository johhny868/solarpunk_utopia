# GAP-47: INSERT OR REPLACE Overwrites Bundles

**Status:** Draft
**Priority:** P2 - Data Integrity
**Effort:** 2-3 hours

## Problem

`INSERT OR REPLACE` silently overwrites existing bundles without warning.

**Location:** `app/database/queues.py:72-82`

## Solution

```python
# ❌ DANGEROUS
await db.execute(
    "INSERT OR REPLACE INTO bundles (id, data) VALUES (?, ?)",
    (bundle_id, data)
)

# ✅ SAFE
try:
    await db.execute(
        "INSERT INTO bundles (id, data) VALUES (?, ?)",
        (bundle_id, data)
    )
except IntegrityError:
    logger.warning(f"Bundle {bundle_id} already exists, skipping")
    # Or raise, or UPDATE if appropriate
```

## Tasks

1. Find all INSERT OR REPLACE usages
2. Replace with INSERT + conflict handling
3. Decide policy per table (skip/update/error)
4. Add tests for duplicate handling

## Success Criteria

- [ ] No silent overwrites
- [ ] Explicit conflict handling
- [ ] Tests for duplicate inserts
