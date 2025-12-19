// Event onboarding and batch invite API client
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/onboarding',
});

export interface EventInvite {
  id: string;
  creator_id: string;
  invite_code: string;
  event_name: string;
  event_type: 'workshop' | 'gathering' | 'meeting' | 'conference' | 'other';
  event_start: string;
  event_end: string;
  event_location: string;
  max_attendees: number;
  attendee_count: number;
  temporary_trust_level: number;
  is_active: boolean;
  created_at: string;
}

export interface CreateEventRequest {
  event_name: string;
  event_type: 'workshop' | 'gathering' | 'meeting' | 'conference' | 'other';
  event_start: string;
  event_end: string;
  event_location: string;
  max_attendees: number;
  temporary_trust_level?: number;
}

export interface JoinEventRequest {
  invite_code: string;
  user_name: string;
  location?: string;
}

export interface JoinEventResponse {
  success: boolean;
  event_name: string;
  temporary_trust_level: number;
  your_trust_score: number;
  message: string;
}

export interface BatchInvite {
  id: string;
  creator_id: string;
  invite_link: string;
  max_uses: number;
  used_count: number;
  days_valid: number;
  expires_at: string;
  context?: string;
  created_at: string;
}

export interface CreateBatchInviteRequest {
  max_uses: number;
  days_valid: number;
  context?: string;
}

export interface JoinBatchRequest {
  invite_link: string;
  user_name: string;
  location?: string;
}

export interface OnboardingAnalytics {
  total_event_invites: number;
  total_batch_invites: number;
  total_event_attendees: number;
  total_batch_members: number;
  upgrade_rate: number;
  active_events: number;
  recent_joins_24h: number;
  trust_level_distribution: Record<string, number>;
}

export const onboardingApi = {
  // Event invites
  createEvent: async (request: CreateEventRequest): Promise<EventInvite> => {
    const response = await api.post<EventInvite>('/event/create', request);
    return response.data;
  },

  getEvent: async (eventId: string): Promise<EventInvite> => {
    const response = await api.get<EventInvite>(`/event/${eventId}`);
    return response.data;
  },

  getEventByCode: async (inviteCode: string): Promise<EventInvite> => {
    const response = await api.get<EventInvite>(`/event/code/${inviteCode}`);
    return response.data;
  },

  joinEvent: async (request: JoinEventRequest): Promise<JoinEventResponse> => {
    const response = await api.post<JoinEventResponse>('/event/join', request);
    return response.data;
  },

  getMyEvents: async (): Promise<EventInvite[]> => {
    const response = await api.get<EventInvite[]>('/event/my');
    return response.data;
  },

  // Batch invites
  createBatchInvite: async (request: CreateBatchInviteRequest): Promise<BatchInvite> => {
    const response = await api.post<BatchInvite>('/batch/create', request);
    return response.data;
  },

  joinBatch: async (request: JoinBatchRequest): Promise<JoinEventResponse> => {
    const response = await api.post<JoinEventResponse>('/batch/join', request);
    return response.data;
  },

  // Analytics
  getAnalytics: async (): Promise<OnboardingAnalytics> => {
    const response = await api.get<OnboardingAnalytics>('/analytics');
    return response.data;
  },
};
