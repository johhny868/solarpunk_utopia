// SQLite wrapper for local-first storage using Capacitor SQLite
import { CapacitorSQLite, SQLiteConnection, SQLiteDBConnection } from '@capacitor-community/sqlite';
import { Capacitor } from '@capacitor/core';

// Schema based on valueflows_node/app/database/vf_schema.sql
const SCHEMA = `
-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    agent_type TEXT NOT NULL CHECK(agent_type IN ('person', 'group', 'place')),
    description TEXT,
    image_url TEXT,
    primary_location_id TEXT,
    contact_info TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    author TEXT,
    signature TEXT
);

CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agents_created ON agents(created_at);

-- Locations table
CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL,
    parent_location_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    author TEXT,
    signature TEXT
);

-- Resource specifications table
CREATE TABLE IF NOT EXISTS resource_specs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    subcategory TEXT,
    image_url TEXT,
    default_unit TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    author TEXT,
    signature TEXT
);

CREATE INDEX IF NOT EXISTS idx_resource_specs_category ON resource_specs(category);
CREATE INDEX IF NOT EXISTS idx_resource_specs_name ON resource_specs(name);

-- Listings table (Offers and Needs)
CREATE TABLE IF NOT EXISTS listings (
    id TEXT PRIMARY KEY,
    listing_type TEXT NOT NULL CHECK(listing_type IN ('offer', 'need')),
    resource_spec_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    location_id TEXT,
    quantity REAL NOT NULL DEFAULT 1.0,
    unit TEXT NOT NULL DEFAULT 'items',
    available_from TEXT,
    available_until TEXT,
    title TEXT,
    description TEXT,
    image_url TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'fulfilled', 'expired', 'cancelled')),
    resource_instance_id TEXT,
    community_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    author TEXT,
    signature TEXT,
    FOREIGN KEY (resource_spec_id) REFERENCES resource_specs(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

CREATE INDEX IF NOT EXISTS idx_listings_type ON listings(listing_type);
CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);
CREATE INDEX IF NOT EXISTS idx_listings_agent ON listings(agent_id);

-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    id TEXT PRIMARY KEY,
    offer_id TEXT NOT NULL,
    need_id TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    receiver_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'suggested',
    provider_approved INTEGER NOT NULL DEFAULT 0,
    receiver_approved INTEGER NOT NULL DEFAULT 0,
    provider_approved_at TEXT,
    receiver_approved_at TEXT,
    match_score REAL,
    match_reason TEXT,
    proposed_quantity REAL,
    proposed_unit TEXT,
    community_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    author TEXT,
    signature TEXT,
    FOREIGN KEY (offer_id) REFERENCES listings(id),
    FOREIGN KEY (need_id) REFERENCES listings(id),
    FOREIGN KEY (provider_id) REFERENCES agents(id),
    FOREIGN KEY (receiver_id) REFERENCES agents(id)
);

CREATE INDEX IF NOT EXISTS idx_matches_offer ON matches(offer_id);
CREATE INDEX IF NOT EXISTS idx_matches_need ON matches(need_id);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status);

-- Exchanges table
CREATE TABLE IF NOT EXISTS exchanges (
    id TEXT PRIMARY KEY,
    match_id TEXT,
    provider_id TEXT NOT NULL,
    receiver_id TEXT NOT NULL,
    resource_spec_id TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    location_id TEXT,
    scheduled_start TEXT,
    scheduled_end TEXT,
    status TEXT NOT NULL DEFAULT 'planned',
    constraints TEXT,
    notes TEXT,
    provider_completed INTEGER NOT NULL DEFAULT 0,
    receiver_completed INTEGER NOT NULL DEFAULT 0,
    provider_event_id TEXT,
    receiver_event_id TEXT,
    community_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    author TEXT,
    signature TEXT,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (provider_id) REFERENCES agents(id),
    FOREIGN KEY (receiver_id) REFERENCES agents(id),
    FOREIGN KEY (resource_spec_id) REFERENCES resource_specs(id)
);

CREATE INDEX IF NOT EXISTS idx_exchanges_provider ON exchanges(provider_id);
CREATE INDEX IF NOT EXISTS idx_exchanges_receiver ON exchanges(receiver_id);
CREATE INDEX IF NOT EXISTS idx_exchanges_status ON exchanges(status);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    resource_spec_id TEXT,
    quantity REAL,
    unit TEXT,
    agent_id TEXT NOT NULL,
    to_agent_id TEXT,
    from_agent_id TEXT,
    location_id TEXT,
    occurred_at TEXT NOT NULL,
    exchange_id TEXT,
    note TEXT,
    image_url TEXT,
    created_at TEXT NOT NULL,
    author TEXT,
    signature TEXT,
    FOREIGN KEY (resource_spec_id) REFERENCES resource_specs(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (exchange_id) REFERENCES exchanges(id)
);

CREATE INDEX IF NOT EXISTS idx_events_action ON events(action);
CREATE INDEX IF NOT EXISTS idx_events_agent ON events(agent_id);

-- Sync queue for DTN bundles
CREATE TABLE IF NOT EXISTS sync_queue (
    id TEXT PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    operation TEXT NOT NULL CHECK(operation IN ('insert', 'update', 'delete')),
    data TEXT,
    created_at TEXT NOT NULL,
    synced INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_sync_queue_synced ON sync_queue(synced);
CREATE INDEX IF NOT EXISTS idx_sync_queue_table ON sync_queue(table_name);

-- Metadata table
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', '1.0');
INSERT OR REPLACE INTO metadata (key, value) VALUES ('created_at', datetime('now'));
`;

export class LocalDatabase {
  private sqlite: SQLiteConnection;
  private db: SQLiteDBConnection | null = null;
  private dbName = 'solarpunk_local.db';

  constructor() {
    this.sqlite = new SQLiteConnection(CapacitorSQLite);
  }

  async initialize(): Promise<void> {
    try {
      // Create or open database
      const ret = await this.sqlite.checkConnectionsConsistency();
      const isConn = (await this.sqlite.isConnection(this.dbName, false)).result;

      if (ret.result && isConn) {
        this.db = await this.sqlite.retrieveConnection(this.dbName, false);
      } else {
        this.db = await this.sqlite.createConnection(
          this.dbName,
          false,
          'no-encryption',
          1,
          false
        );
      }

      await this.db.open();

      // Run schema
      await this.db.execute(SCHEMA);

      console.log('Local database initialized');
    } catch (error) {
      console.error('Failed to initialize database:', error);
      throw error;
    }
  }

  async query<T>(sql: string, params: any[] = []): Promise<T[]> {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    try {
      const result = await this.db.query(sql, params);
      return result.values || [];
    } catch (error) {
      console.error('Query failed:', sql, error);
      throw error;
    }
  }

  async execute(sql: string, params: any[] = []): Promise<void> {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    try {
      await this.db.run(sql, params);
    } catch (error) {
      console.error('Execute failed:', sql, error);
      throw error;
    }
  }

  async insert(sql: string, params: any[] = []): Promise<string> {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    try {
      const result = await this.db.run(sql, params);
      return result.changes?.lastId?.toString() || '';
    } catch (error) {
      console.error('Insert failed:', sql, error);
      throw error;
    }
  }

  async close(): Promise<void> {
    if (this.db) {
      await this.db.close();
      await this.sqlite.closeConnection(this.dbName, false);
      this.db = null;
    }
  }

  // Helper: Queue change for sync
  async queueSync(tableName: string, recordId: string, operation: 'insert' | 'update' | 'delete', data?: any): Promise<void> {
    const id = `sync_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    await this.insert(
      `INSERT INTO sync_queue (id, table_name, record_id, operation, data, created_at, synced)
       VALUES (?, ?, ?, ?, ?, ?, 0)`,
      [id, tableName, recordId, operation, data ? JSON.stringify(data) : null, new Date().toISOString()]
    );
  }

  // Helper: Get pending sync items
  async getPendingSync(): Promise<any[]> {
    return this.query(
      `SELECT * FROM sync_queue WHERE synced = 0 ORDER BY created_at ASC LIMIT 100`
    );
  }

  // Helper: Mark sync item as synced
  async markSynced(syncId: string): Promise<void> {
    await this.execute(
      `UPDATE sync_queue SET synced = 1 WHERE id = ?`,
      [syncId]
    );
  }
}

// Singleton instance
let dbInstance: LocalDatabase | null = null;

export async function getDatabase(): Promise<LocalDatabase> {
  // Skip SQLite on web platform - use remote API instead
  if (Capacitor.getPlatform() === 'web') {
    throw new Error('SQLite not available on web platform. Use remote API instead.');
  }

  if (!dbInstance) {
    dbInstance = new LocalDatabase();
    await dbInstance.initialize();
  }
  return dbInstance;
}
