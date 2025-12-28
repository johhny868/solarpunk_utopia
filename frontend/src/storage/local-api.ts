// Local-first API implementation for offline functionality
// Matches the ValueFlows API but operates on local SQLite database
import { getDatabase, LocalDatabase } from './sqlite';
import type {
  Listing,
  CreateListingRequest,
  Agent,
  ResourceSpecification,
  Match,
  Exchange,
  EconomicEvent,
  CreateEventRequest,
  CreateExchangeRequest,
} from '../types/valueflows';

export class LocalValueFlowsAPI {
  private db: LocalDatabase | null = null;

  async initialize(): Promise<void> {
    this.db = await getDatabase();
  }

  private ensureDb(): LocalDatabase {
    if (!this.db) {
      throw new Error('LocalValueFlowsAPI not initialized. Call initialize() first.');
    }
    return this.db;
  }

  // ============================================================================
  // AGENTS
  // ============================================================================

  async getAgents(): Promise<Agent[]> {
    const db = this.ensureDb();
    const rows = await db.query<any>(
      `SELECT id, name, agent_type as type, description as note, primary_location_id as location, created_at
       FROM agents ORDER BY created_at DESC`
    );
    return rows.map(row => ({
      id: row.id,
      name: row.name,
      type: row.type,
      note: row.note,
      location: row.location,
      created_at: row.created_at,
    }));
  }

  async getAgent(id: string): Promise<Agent> {
    const db = this.ensureDb();
    const rows = await db.query<any>(
      `SELECT id, name, agent_type as type, description as note, primary_location_id as location, created_at
       FROM agents WHERE id = ?`,
      [id]
    );
    if (rows.length === 0) {
      throw new Error(`Agent ${id} not found`);
    }
    return rows[0];
  }

  async createAgent(agent: Omit<Agent, 'created_at'>): Promise<Agent> {
    const db = this.ensureDb();
    const created_at = new Date().toISOString();

    await db.insert(
      `INSERT INTO agents (id, name, agent_type, description, primary_location_id, created_at)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [agent.id, agent.name, agent.type, agent.note || null, agent.location || null, created_at]
    );

    await db.queueSync('agents', agent.id, 'insert', { ...agent, created_at });

    return { ...agent, created_at };
  }

  // ============================================================================
  // RESOURCE SPECIFICATIONS
  // ============================================================================

  async getResourceSpecs(): Promise<ResourceSpecification[]> {
    const db = this.ensureDb();
    return db.query<ResourceSpecification>(
      `SELECT id, name, category, subcategory, default_unit as unit, description as note
       FROM resource_specs ORDER BY name`
    );
  }

  async getResourceSpec(id: string): Promise<ResourceSpecification> {
    const db = this.ensureDb();
    const rows = await db.query<ResourceSpecification>(
      `SELECT id, name, category, subcategory, default_unit as unit, description as note
       FROM resource_specs WHERE id = ?`,
      [id]
    );
    if (rows.length === 0) {
      throw new Error(`ResourceSpec ${id} not found`);
    }
    return rows[0];
  }

  async createResourceSpec(spec: ResourceSpecification): Promise<ResourceSpecification> {
    const db = this.ensureDb();
    const created_at = new Date().toISOString();

    await db.insert(
      `INSERT INTO resource_specs (id, name, category, subcategory, default_unit, description, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [spec.id, spec.name, spec.category, spec.subcategory || null, spec.unit || null, spec.note || null, created_at]
    );

    await db.queueSync('resource_specs', spec.id, 'insert', spec);

    return spec;
  }

  // ============================================================================
  // LISTINGS (Offers and Needs)
  // ============================================================================

  async getListings(type?: 'offer' | 'need'): Promise<Listing[]> {
    const db = this.ensureDb();
    const sql = type
      ? `SELECT * FROM listings WHERE listing_type = ? AND status = 'active' ORDER BY created_at DESC`
      : `SELECT * FROM listings WHERE status = 'active' ORDER BY created_at DESC`;
    const params = type ? [type] : [];

    const rows = await db.query<any>(sql, params);

    // Fetch related data
    const listings: Listing[] = [];
    for (const row of rows) {
      const agent = await this.getAgent(row.agent_id).catch(() => undefined);
      const resource_specification = await this.getResourceSpec(row.resource_spec_id).catch(() => undefined);

      listings.push({
        id: row.id,
        listing_type: row.listing_type,
        agent_id: row.agent_id,
        agent,
        resource_spec_id: row.resource_spec_id,
        resource_specification,
        quantity: row.quantity,
        unit: row.unit,
        location_id: row.location_id,
        location: row.location_id,
        available_from: row.available_from,
        available_until: row.available_until,
        title: row.title,
        description: row.description,
        note: row.description,
        image_url: row.image_url,
        status: row.status,
        created_at: row.created_at,
        updated_at: row.updated_at,
      });
    }

    return listings;
  }

  async getListing(id: string): Promise<Listing> {
    const db = this.ensureDb();
    const rows = await db.query<any>(
      `SELECT * FROM listings WHERE id = ?`,
      [id]
    );
    if (rows.length === 0) {
      throw new Error(`Listing ${id} not found`);
    }

    const row = rows[0];
    const agent = await this.getAgent(row.agent_id).catch(() => undefined);
    const resource_specification = await this.getResourceSpec(row.resource_spec_id).catch(() => undefined);

    return {
      id: row.id,
      listing_type: row.listing_type,
      agent_id: row.agent_id,
      agent,
      resource_spec_id: row.resource_spec_id,
      resource_specification,
      quantity: row.quantity,
      unit: row.unit,
      location_id: row.location_id,
      location: row.location_id,
      available_from: row.available_from,
      available_until: row.available_until,
      title: row.title,
      description: row.description,
      note: row.description,
      image_url: row.image_url,
      status: row.status,
      created_at: row.created_at,
      updated_at: row.updated_at,
    };
  }

  async createListing(request: CreateListingRequest): Promise<Listing> {
    const db = this.ensureDb();
    const id = `listing_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const created_at = new Date().toISOString();

    await db.insert(
      `INSERT INTO listings (
        id, listing_type, agent_id, resource_spec_id, quantity, unit,
        location_id, available_from, available_until, title, description,
        image_url, status, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)`,
      [
        id,
        request.listing_type,
        request.agent_id,
        request.resource_spec_id,
        request.quantity,
        request.unit,
        request.location_id || null,
        request.available_from || null,
        request.available_until || null,
        request.title || null,
        request.description || null,
        request.image_url || null,
        created_at,
        created_at,
      ]
    );

    await db.queueSync('listings', id, 'insert', { ...request, id, created_at });

    return this.getListing(id);
  }

  async updateListing(id: string, updates: Partial<Listing>): Promise<Listing> {
    const db = this.ensureDb();
    const updated_at = new Date().toISOString();

    const fields: string[] = [];
    const values: any[] = [];

    if (updates.status !== undefined) {
      fields.push('status = ?');
      values.push(updates.status);
    }
    if (updates.quantity !== undefined) {
      fields.push('quantity = ?');
      values.push(updates.quantity);
    }
    if (updates.description !== undefined) {
      fields.push('description = ?');
      values.push(updates.description);
    }

    if (fields.length === 0) {
      return this.getListing(id);
    }

    fields.push('updated_at = ?');
    values.push(updated_at);
    values.push(id);

    await db.execute(
      `UPDATE listings SET ${fields.join(', ')} WHERE id = ?`,
      values
    );

    await db.queueSync('listings', id, 'update', updates);

    return this.getListing(id);
  }

  // ============================================================================
  // MATCHES
  // ============================================================================

  async getMatches(agentId?: string): Promise<Match[]> {
    const db = this.ensureDb();
    const sql = agentId
      ? `SELECT * FROM matches WHERE (provider_id = ? OR receiver_id = ?) AND status != 'rejected' ORDER BY created_at DESC`
      : `SELECT * FROM matches WHERE status != 'rejected' ORDER BY created_at DESC`;
    const params = agentId ? [agentId, agentId] : [];

    const rows = await db.query<any>(sql, params);

    const matches: Match[] = [];
    for (const row of rows) {
      const offer = await this.getListing(row.offer_id).catch(() => undefined);
      const need = await this.getListing(row.need_id).catch(() => undefined);

      matches.push({
        id: row.id,
        offer_id: row.offer_id,
        offer,
        need_id: row.need_id,
        need,
        quantity: row.proposed_quantity,
        unit: row.proposed_unit,
        score: row.match_score,
        reason: row.match_reason,
        status: row.status,
        created_at: row.created_at,
      });
    }

    return matches;
  }

  async createMatch(match: Omit<Match, 'created_at'>): Promise<Match> {
    const db = this.ensureDb();
    const created_at = new Date().toISOString();

    await db.insert(
      `INSERT INTO matches (
        id, offer_id, need_id, provider_id, receiver_id,
        status, match_score, match_reason, proposed_quantity, proposed_unit, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        match.id,
        match.offer_id,
        match.need_id,
        // Get provider/receiver from listings
        (await this.getListing(match.offer_id)).agent_id,
        (await this.getListing(match.need_id)).agent_id,
        match.status,
        match.score,
        match.reason || null,
        match.quantity,
        match.unit,
        created_at,
      ]
    );

    await db.queueSync('matches', match.id, 'insert', { ...match, created_at });

    return { ...match, created_at };
  }

  // ============================================================================
  // EXCHANGES
  // ============================================================================

  async getExchanges(agentId?: string): Promise<Exchange[]> {
    const db = this.ensureDb();
    const sql = agentId
      ? `SELECT * FROM exchanges WHERE provider_id = ? OR receiver_id = ? ORDER BY created_at DESC`
      : `SELECT * FROM exchanges ORDER BY created_at DESC`;
    const params = agentId ? [agentId, agentId] : [];

    const rows = await db.query<any>(sql, params);

    const exchanges: Exchange[] = [];
    for (const row of rows) {
      const provider = await this.getAgent(row.provider_id).catch(() => undefined);
      const receiver = await this.getAgent(row.receiver_id).catch(() => undefined);
      const resource_specification = await this.getResourceSpec(row.resource_spec_id).catch(() => undefined);

      // Fetch events for this exchange
      const events = await db.query<any>(
        `SELECT * FROM events WHERE exchange_id = ? ORDER BY occurred_at`,
        [row.id]
      );

      const mappedEvents: EconomicEvent[] = events.map((e: any) => ({
        id: e.id,
        action: e.action,
        provider_id: e.from_agent_id,
        receiver_id: e.to_agent_id,
        resource_specification_id: e.resource_spec_id,
        quantity: e.quantity,
        unit: e.unit,
        timestamp: e.occurred_at,
        location: e.location_id,
        note: e.note,
      }));

      exchanges.push({
        id: row.id,
        name: `Exchange ${row.id}`,
        provider_id: row.provider_id,
        provider,
        receiver_id: row.receiver_id,
        receiver,
        resource_specification_id: row.resource_spec_id,
        resource_specification,
        quantity: row.quantity,
        unit: row.unit,
        status: row.status,
        events: mappedEvents,
        created_at: row.created_at,
        updated_at: row.updated_at,
      });
    }

    return exchanges;
  }

  async createExchange(request: CreateExchangeRequest): Promise<Exchange> {
    const db = this.ensureDb();
    const id = `exchange_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const created_at = new Date().toISOString();

    await db.insert(
      `INSERT INTO exchanges (
        id, provider_id, receiver_id, resource_spec_id, quantity, unit,
        status, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, 'planned', ?, ?)`,
      [
        id,
        request.provider_id,
        request.receiver_id,
        request.resource_specification_id,
        request.quantity,
        request.unit,
        created_at,
        created_at,
      ]
    );

    await db.queueSync('exchanges', id, 'insert', { ...request, id, created_at });

    const exchanges = await this.getExchanges();
    return exchanges.find(e => e.id === id)!;
  }

  async completeExchange(exchangeId: string, _agentId: string, role: 'provider' | 'receiver'): Promise<void> {
    const db = this.ensureDb();
    const field = role === 'provider' ? 'provider_completed' : 'receiver_completed';

    await db.execute(
      `UPDATE exchanges SET ${field} = 1, updated_at = ? WHERE id = ?`,
      [new Date().toISOString(), exchangeId]
    );

    // Check if both completed
    const rows = await db.query<any>(
      `SELECT provider_completed, receiver_completed FROM exchanges WHERE id = ?`,
      [exchangeId]
    );

    if (rows.length > 0 && rows[0].provider_completed && rows[0].receiver_completed) {
      await db.execute(
        `UPDATE exchanges SET status = 'completed', updated_at = ? WHERE id = ?`,
        [new Date().toISOString(), exchangeId]
      );
    }

    await db.queueSync('exchanges', exchangeId, 'update', { [field]: 1 });
  }

  // ============================================================================
  // EVENTS
  // ============================================================================

  async createEvent(request: CreateEventRequest): Promise<EconomicEvent> {
    const db = this.ensureDb();
    const id = `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const created_at = new Date().toISOString();
    const occurred_at = created_at;

    await db.insert(
      `INSERT INTO events (
        id, action, resource_spec_id, quantity, unit,
        agent_id, to_agent_id, from_agent_id, location_id,
        occurred_at, note, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        id,
        request.action,
        request.resource_specification_id || null,
        request.quantity,
        request.unit,
        request.provider_id || request.receiver_id || '',
        request.receiver_id || null,
        request.provider_id || null,
        request.location || null,
        occurred_at,
        request.note || null,
        created_at,
      ]
    );

    await db.queueSync('events', id, 'insert', { ...request, id, created_at });

    return {
      id,
      action: request.action,
      provider_id: request.provider_id,
      receiver_id: request.receiver_id,
      resource_specification_id: request.resource_specification_id,
      quantity: request.quantity,
      unit: request.unit,
      timestamp: occurred_at,
      location: request.location,
      note: request.note,
    };
  }
}

// Singleton instance
let apiInstance: LocalValueFlowsAPI | null = null;

export async function getLocalAPI(): Promise<LocalValueFlowsAPI> {
  if (!apiInstance) {
    apiInstance = new LocalValueFlowsAPI();
    await apiInstance.initialize();
  }
  return apiInstance;
}
