// ValueFlows API Client
import axios from 'axios';
import type {
  Agent,
  Intent,
  EconomicResource,
  ResourceSpecification,
  EconomicEvent,
  Exchange,
  Match,
  Commitment,
  CreateIntentRequest,
  CreateEventRequest,
  CreateExchangeRequest,
} from '@/types/valueflows';

const api = axios.create({
  baseURL: '/api/vf',
});

export const valueflowsApi = {
  // Agents
  getAgents: async (): Promise<Agent[]> => {
    const response = await api.get<Agent[]>('/agents');
    return response.data;
  },

  getAgent: async (id: string): Promise<Agent> => {
    const response = await api.get<Agent>(`/agents/${id}`);
    return response.data;
  },

  createAgent: async (data: Partial<Agent>): Promise<Agent> => {
    const response = await api.post<Agent>('/agents', data);
    return response.data;
  },

  // Resource Specifications
  getResourceSpecifications: async (): Promise<ResourceSpecification[]> => {
    const response = await api.get<ResourceSpecification[]>('/resource-specifications');
    return response.data;
  },

  getResourceSpecification: async (id: string): Promise<ResourceSpecification> => {
    const response = await api.get<ResourceSpecification>(`/resource-specifications/${id}`);
    return response.data;
  },

  createResourceSpecification: async (
    data: Partial<ResourceSpecification>
  ): Promise<ResourceSpecification> => {
    const response = await api.post<ResourceSpecification>('/resource-specifications', data);
    return response.data;
  },

  // Economic Resources
  getResources: async (): Promise<EconomicResource[]> => {
    const response = await api.get<EconomicResource[]>('/resources');
    return response.data;
  },

  getResource: async (id: string): Promise<EconomicResource> => {
    const response = await api.get<EconomicResource>(`/resources/${id}`);
    return response.data;
  },

  // Listings (Offers & Needs)
  getListings: async (listing_type?: 'offer' | 'need', community_id?: string): Promise<Intent[]> => {
    const params = new URLSearchParams();
    if (listing_type) params.append('listing_type', listing_type);
    if (community_id) params.append('community_id', community_id);
    const url = `/listings${params.toString() ? '?' + params.toString() : ''}`;
    const response = await api.get<{ listings: Intent[] } | Intent[]>(url);
    return Array.isArray(response.data) ? response.data : response.data.listings;
  },

  getListing: async (id: string): Promise<Intent> => {
    const response = await api.get<Intent>(`/listings/${id}`);
    return response.data;
  },

  createListing: async (data: CreateIntentRequest): Promise<Intent> => {
    const response = await api.post<Intent>('/listings', data);
    return response.data;
  },

  updateListing: async (id: string, data: Partial<Intent>): Promise<Intent> => {
    const response = await api.patch<Intent>(`/listings/${id}`, data);
    return response.data;
  },

  deleteListing: async (id: string): Promise<void> => {
    await api.delete(`/listings/${id}`);
  },

  // Legacy aliases for backward compatibility
  getIntents: async (type?: 'offer' | 'need', community_id?: string): Promise<Intent[]> => {
    return valueflowsApi.getListings(type, community_id);
  },

  getIntent: async (id: string): Promise<Intent> => {
    return valueflowsApi.getListing(id);
  },

  createIntent: async (data: CreateIntentRequest): Promise<Intent> => {
    return valueflowsApi.createListing(data);
  },

  updateIntent: async (id: string, data: Partial<Intent>): Promise<Intent> => {
    return valueflowsApi.updateListing(id, data);
  },

  deleteIntent: async (id: string): Promise<void> => {
    return valueflowsApi.deleteListing(id);
  },

  // Offers
  getOffers: async (community_id?: string): Promise<Intent[]> => {
    return valueflowsApi.getListings('offer', community_id);
  },

  // Needs
  getNeeds: async (community_id?: string): Promise<Intent[]> => {
    return valueflowsApi.getListings('need', community_id);
  },

  // Matches
  getMatches: async (community_id?: string): Promise<Match[]> => {
    const params = new URLSearchParams();
    if (community_id) params.append('community_id', community_id);
    const url = `/matches${params.toString() ? '?' + params.toString() : ''}`;
    const response = await api.get<{ matches: Match[]; count: number } | Match[]>(url);
    return Array.isArray(response.data) ? response.data : response.data.matches;
  },

  getMatch: async (id: string): Promise<Match> => {
    const response = await api.get<Match>(`/matches/${id}`);
    return response.data;
  },

  acceptMatch: async (id: string): Promise<Match> => {
    const response = await api.post<Match>(`/matches/${id}/accept`);
    return response.data;
  },

  rejectMatch: async (id: string): Promise<Match> => {
    const response = await api.post<Match>(`/matches/${id}/reject`);
    return response.data;
  },

  // Commitments
  getCommitments: async (): Promise<Commitment[]> => {
    const response = await api.get<Commitment[]>('/commitments');
    return response.data;
  },

  getCommitment: async (id: string): Promise<Commitment> => {
    const response = await api.get<Commitment>(`/commitments/${id}`);
    return response.data;
  },

  // Economic Events
  getEvents: async (): Promise<EconomicEvent[]> => {
    const response = await api.get<EconomicEvent[]>('/events');
    return response.data;
  },

  getEvent: async (id: string): Promise<EconomicEvent> => {
    const response = await api.get<EconomicEvent>(`/events/${id}`);
    return response.data;
  },

  createEvent: async (data: CreateEventRequest): Promise<EconomicEvent> => {
    const response = await api.post<EconomicEvent>('/events', data);
    return response.data;
  },

  // Exchanges
  getExchanges: async (community_id?: string): Promise<Exchange[]> => {
    const params = new URLSearchParams();
    if (community_id) params.append('community_id', community_id);
    const url = `/exchanges${params.toString() ? '?' + params.toString() : ''}`;
    const response = await api.get<{ exchanges: Exchange[]; count: number } | Exchange[]>(url);
    return Array.isArray(response.data) ? response.data : response.data.exchanges;
  },

  getExchange: async (id: string): Promise<Exchange> => {
    const response = await api.get<Exchange>(`/exchanges/${id}`);
    return response.data;
  },

  createExchange: async (data: CreateExchangeRequest): Promise<Exchange> => {
    const response = await api.post<Exchange>('/exchanges', data);
    return response.data;
  },

  updateExchange: async (id: string, data: Partial<Exchange>): Promise<Exchange> => {
    const response = await api.put<Exchange>(`/exchanges/${id}`, data);
    return response.data;
  },

  completeExchange: async (exchangeId: string, agentId: string, eventId: string): Promise<{ exchange: Exchange; fully_completed: boolean }> => {
    const response = await api.patch<{ exchange: Exchange; fully_completed: boolean }>(
      `/exchanges/${exchangeId}/complete`,
      null,
      { params: { agent_id: agentId, event_id: eventId } }
    );
    return response.data;
  },
};
