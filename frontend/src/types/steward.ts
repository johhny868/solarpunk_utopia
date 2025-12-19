export interface CellMetrics {
  cell_id: string;
  cell_name: string;
  member_count: number;
  active_offers: number;
  active_needs: number;
  matches_this_week: number;
  exchanges_this_week: number;
  value_kept_local: number;
  new_members_this_week: number;
}

export interface AttentionItem {
  type: 'join_request' | 'proposal' | 'inactive_member' | 'trust_issue' | 'all_clear';
  priority: 'high' | 'medium' | 'low';
  message: string;
  action_url?: string;
  count: number;
}

export interface RecentActivity {
  type: 'offer' | 'need' | 'match' | 'exchange' | 'join';
  message: string;
  timestamp: string;
  user_id?: string;
}

export interface Celebration {
  type: 'milestone' | 'achievement';
  message: string;
  user_id?: string;
}

export interface DashboardData {
  metrics: CellMetrics;
  attention_items: AttentionItem[];
  recent_activity: RecentActivity[];
  celebrations: Celebration[];
}

export interface ManagedCell {
  id: string;
  name: string;
  member_count: number;
  role: string;
}
