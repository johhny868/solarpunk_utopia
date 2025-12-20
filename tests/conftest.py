"""Shared pytest fixtures for all tests.

This ensures test databases are properly initialized with all migrations.
"""
import sqlite3
from pathlib import Path
import pytest


def run_migrations_sync(db_path: str, migrations_dir: Path) -> None:
    """Run all SQL migrations on a database synchronously.

    This is a synchronous version of app/database/db.py::_run_migrations
    for use in pytest fixtures.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        # Create migrations tracking table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                applied_at TEXT NOT NULL
            )
        """)
        conn.commit()

        # Get list of already applied migrations
        cursor = conn.execute("SELECT filename FROM migrations")
        applied = {row[0] for row in cursor.fetchall()}

        # Get all migration files
        if not migrations_dir.exists():
            return

        migration_files = sorted(migrations_dir.glob("*.sql"))

        for migration_file in migration_files:
            if migration_file.name in applied:
                continue

            # Read and execute migration
            sql = migration_file.read_text()
            conn.executescript(sql)

            # Record migration
            conn.execute(
                "INSERT INTO migrations (filename, applied_at) VALUES (?, datetime('now'))",
                (migration_file.name,)
            )
            conn.commit()

    finally:
        conn.close()


@pytest.fixture(scope="function", autouse=True)
def ensure_test_db_migrations():
    """Ensure any test database gets migrations run.

    This fixture runs automatically before each test.
    After the test completes, it cleans up test databases.
    """
    yield

    # Cleanup: Remove any test databases
    test_db_patterns = [
        "data/test_*.db",
        "test_*.db",
    ]

    for pattern in test_db_patterns:
        for db_file in Path(".").glob(pattern):
            try:
                db_file.unlink()
            except:
                pass


def init_test_db(db_path: str) -> None:
    """Initialize a test database with all migrations.

    Call this in test fixtures that create custom databases:

    @pytest.fixture
    def service():
        db_path = "data/test_myfeature.db"
        init_test_db(db_path)  # <-- Add this
        service = MyService(db_path=db_path)
        yield service
    """
    # Ensure data directory exists
    Path(db_path).parent.mkdir(exist_ok=True, parents=True)

    # Create minimal base schema (absolute minimum required by ALL migrations)
    conn = sqlite3.connect(db_path)
    try:
        # Only create tables that are NOT created by migrations
        # These are the core tables from app/database/db.py::init_db()

        # Bundles table - NOT in migrations
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bundles (
                bundleId TEXT PRIMARY KEY,
                queue TEXT NOT NULL,
                createdAt TEXT NOT NULL,
                expiresAt TEXT NOT NULL,
                priority TEXT NOT NULL,
                audience TEXT NOT NULL,
                topic TEXT NOT NULL,
                tags TEXT NOT NULL,
                payloadType TEXT NOT NULL,
                payload TEXT NOT NULL,
                hopLimit INTEGER NOT NULL,
                hopCount INTEGER NOT NULL DEFAULT 0,
                receiptPolicy TEXT NOT NULL,
                signature TEXT NOT NULL,
                authorPublicKey TEXT NOT NULL,
                sizeBytes INTEGER NOT NULL,
                addedToQueueAt TEXT NOT NULL
            )
        """)

        # Metadata table - NOT in migrations
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Proposals table - NOT in migrations
        conn.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                proposal_id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                proposal_type TEXT NOT NULL,
                title TEXT NOT NULL,
                explanation TEXT NOT NULL,
                inputs_used TEXT NOT NULL,
                constraints TEXT NOT NULL,
                data TEXT NOT NULL,
                requires_approval TEXT NOT NULL,
                approvals TEXT NOT NULL,
                approval_reasons TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                executed_at TEXT,
                bundle_id TEXT
            )
        """)

        # Users table - NOT in migrations
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # DO NOT create cells, campaigns, etc - they are created by migrations

        conn.commit()
    finally:
        conn.close()

    # Run DTN bundle system migrations
    migrations_dir = Path(__file__).parent.parent / "app" / "database" / "migrations"
    if migrations_dir.exists():
        run_migrations_sync(db_path, migrations_dir)
