# GAP-46: Race Conditions in Queue/Cache

**Status:** Draft
**Priority:** P2 - Data Integrity
**Effort:** 4-6 hours

## Problem

Non-atomic check-then-act allows concurrent corruption.

**Locations:**
- `app/database/queues.py:67-83` - INSERT OR REPLACE without lock
- `app/services/cache_service.py:70-85` - check-then-delete not atomic

## Solution

Use locks or transactions:

```python
# ❌ VULNERABLE
cache_size = await get_cache_size()
if cache_size > MAX_SIZE:
    await delete_oldest()  # Race condition!

# ✅ SAFE - with lock
async with cache_lock:
    cache_size = await get_cache_size()
    if cache_size > MAX_SIZE:
        await delete_oldest()

# ✅ SAFE - with transaction
async with db.transaction():
    cache_size = await db.execute("SELECT SUM(size) FROM cache")
    if cache_size > MAX_SIZE:
        await db.execute("DELETE FROM cache WHERE ...")
```

## Tasks

1. Audit check-then-act patterns
2. Add asyncio.Lock where needed
3. Use database transactions for atomic ops
4. Add concurrency tests

## Success Criteria

- [ ] No non-atomic check-then-act
- [ ] Locks/transactions in place
- [ ] Concurrency tests pass
