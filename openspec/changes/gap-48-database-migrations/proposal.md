# GAP-48: Database Migrations

**Status:** Already Implemented
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

- [x] Schema changes via migrations only
- [x] Migrations tracked in DB
- [x] Migrations run automatically on startup
- [x] Documented process

## Implementation Notes

**Already Implemented** - Discovered 2025-12-20

The migration system already exists in `app/database/db.py`:

### Existing Implementation:

1. **Migration Tracking Table** (lines 21-27):
   - `migrations` table tracks applied migrations
   - Stores filename and applied_at timestamp

2. **Migration Runner** (lines 18-56):
   - `_run_migrations()` function runs on every `init_db()`
   - Reads SQL files from `app/database/migrations/`
   - Applies only new migrations (checks against tracking table)
   - Logs each migration as it's applied

3. **Active Migrations**:
   - 16 migrations currently in `app/database/migrations/`
   - Numbered sequentially (001-016)
   - Cover: local cells, sanctuary, messaging, governance, economic withdrawal, etc.

### How to Create New Migration:

```bash
# Create numbered SQL file
touch app/database/migrations/017_add_your_feature.sql

# Write SQL
cat > app/database/migrations/017_add_your_feature.sql <<EOF
CREATE TABLE your_table (...);
CREATE INDEX idx_your_table ON your_table(column);
EOF

# Migration runs automatically on next app startup
```

### Result:
- ✅ Simple SQL-based migrations (no Alembic needed)
- ✅ Automatic tracking and execution
- ✅ 16 migrations successfully applied
- ✅ Production-ready system
