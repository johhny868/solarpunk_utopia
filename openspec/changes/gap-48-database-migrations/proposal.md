# GAP-48: Database Migrations

**Status:** Draft
**Priority:** P2 - Operations
**Effort:** 4-6 hours

## Problem

No migration system. Schema changes require manual SQL or full recreate.

## Solution

Use Alembic:

```python
# alembic/versions/001_initial.py
def upgrade():
    op.create_table('users', ...)
    op.add_column('listings', sa.Column('community_id', ...))

def downgrade():
    op.drop_column('listings', 'community_id')
    op.drop_table('users')
```

Or simpler: numbered SQL files + tracking table:

```sql
-- migrations/001_add_users.sql
CREATE TABLE users (...);

-- Track in database
CREATE TABLE _migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Tasks

1. Choose migration approach (Alembic vs simple)
2. Create initial migration from current schema
3. Add migration runner to app startup
4. Document migration workflow

## Success Criteria

- [ ] Schema changes via migrations only
- [ ] Migrations tracked in DB
- [ ] Up/down migrations work
- [ ] Documented process
