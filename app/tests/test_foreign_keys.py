"""
Tests for GAP-45: Foreign Key Enforcement

Verifies that:
1. Foreign keys are enforced at runtime
2. Orphan records are prevented
3. CASCADE rules work correctly
"""

import pytest
import pytest_asyncio
import aiosqlite
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.db import init_db, get_db, close_db, DB_PATH


@pytest_asyncio.fixture
async def test_db():
    """Create a test database"""
    # Use a temporary database for testing
    original_db_path = DB_PATH

    # Create temp db
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()

    # Monkey patch DB_PATH
    import app.database.db as db_module
    db_module.DB_PATH = Path(temp_db.name)

    # Initialize test database
    await init_db()

    yield await get_db()

    # Cleanup
    await close_db()
    db_module.DB_PATH = original_db_path
    os.unlink(temp_db.name)


@pytest.mark.asyncio
async def test_foreign_keys_enabled(test_db):
    """Test that foreign keys are enabled"""
    cursor = await test_db.execute("PRAGMA foreign_keys")
    result = await cursor.fetchone()
    assert result[0] == 1, "Foreign keys should be enabled"


@pytest.mark.asyncio
async def test_cascade_delete_sessions(test_db):
    """Test that deleting a user cascades to sessions"""
    # Create a user
    user_id = "test-user-123"
    await test_db.execute(
        "INSERT INTO users (id, name, email, created_at) VALUES (?, ?, ?, datetime('now'))",
        (user_id, "Test User", "test@example.com")
    )
    await test_db.commit()

    # Create a session for this user
    session_id = "test-session-123"
    await test_db.execute(
        "INSERT INTO sessions (id, user_id, token, expires_at, created_at) VALUES (?, ?, ?, datetime('now', '+1 day'), datetime('now'))",
        (session_id, user_id, "test-token-123")
    )
    await test_db.commit()

    # Verify session exists
    cursor = await test_db.execute("SELECT COUNT(*) FROM sessions WHERE id = ?", (session_id,))
    count = (await cursor.fetchone())[0]
    assert count == 1, "Session should exist"

    # Delete user - should cascade to session
    await test_db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    await test_db.commit()

    # Verify session was deleted (CASCADE)
    cursor = await test_db.execute("SELECT COUNT(*) FROM sessions WHERE id = ?", (session_id,))
    count = (await cursor.fetchone())[0]
    assert count == 0, "Session should be deleted due to CASCADE"


@pytest.mark.asyncio
async def test_cascade_delete_community_memberships(test_db):
    """Test that deleting a community cascades to memberships"""
    # Create user
    user_id = "test-user-456"
    await test_db.execute(
        "INSERT INTO users (id, name, created_at) VALUES (?, ?, datetime('now'))",
        (user_id, "Test User 2")
    )

    # Create community
    community_id = "test-community-123"
    await test_db.execute(
        "INSERT INTO communities (id, name, created_at) VALUES (?, ?, datetime('now'))",
        (community_id, "Test Community")
    )
    await test_db.commit()

    # Create membership
    membership_id = "test-membership-123"
    await test_db.execute(
        "INSERT INTO community_memberships (id, user_id, community_id, joined_at) VALUES (?, ?, ?, datetime('now'))",
        (membership_id, user_id, community_id)
    )
    await test_db.commit()

    # Verify membership exists
    cursor = await test_db.execute("SELECT COUNT(*) FROM community_memberships WHERE id = ?", (membership_id,))
    count = (await cursor.fetchone())[0]
    assert count == 1, "Membership should exist"

    # Delete community - should cascade to membership
    await test_db.execute("DELETE FROM communities WHERE id = ?", (community_id,))
    await test_db.commit()

    # Verify membership was deleted (CASCADE)
    cursor = await test_db.execute("SELECT COUNT(*) FROM community_memberships WHERE id = ?", (membership_id,))
    count = (await cursor.fetchone())[0]
    assert count == 0, "Membership should be deleted due to CASCADE"


@pytest.mark.asyncio
async def test_orphan_prevention(test_db):
    """Test that orphaned records are prevented"""
    # Try to create a session for a non-existent user
    with pytest.raises(aiosqlite.IntegrityError):
        await test_db.execute(
            "INSERT INTO sessions (id, user_id, token, expires_at, created_at) VALUES (?, ?, ?, datetime('now', '+1 day'), datetime('now'))",
            ("orphan-session", "non-existent-user", "orphan-token")
        )
        await test_db.commit()


@pytest.mark.asyncio
async def test_unique_constraint_community_membership(test_db):
    """Test that a user can't join the same community twice"""
    # Create user and community
    user_id = "test-user-789"
    community_id = "test-community-456"

    await test_db.execute(
        "INSERT INTO users (id, name, created_at) VALUES (?, ?, datetime('now'))",
        (user_id, "Test User 3")
    )
    await test_db.execute(
        "INSERT INTO communities (id, name, created_at) VALUES (?, ?, datetime('now'))",
        (community_id, "Test Community 2")
    )
    await test_db.commit()

    # Create first membership
    await test_db.execute(
        "INSERT INTO community_memberships (id, user_id, community_id, joined_at) VALUES (?, ?, ?, datetime('now'))",
        ("membership-1", user_id, community_id)
    )
    await test_db.commit()

    # Try to create duplicate membership - should fail due to UNIQUE(user_id, community_id)
    with pytest.raises(aiosqlite.IntegrityError):
        await test_db.execute(
            "INSERT INTO community_memberships (id, user_id, community_id, joined_at) VALUES (?, ?, ?, datetime('now'))",
            ("membership-2", user_id, community_id)
        )
        await test_db.commit()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
