import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { DashboardData, ManagedCell } from '@/types/steward';

export function useStewardDashboard(cellId: string) {
  return useQuery({
    queryKey: ['steward', 'dashboard', cellId],
    queryFn: async () => {
      const response = await apiClient.get<DashboardData>(
        `/steward/dashboard/${cellId}`
      );
      return response.data;
    },
    enabled: !!cellId,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

export function useManagedCells() {
  return useQuery({
    queryKey: ['steward', 'cells'],
    queryFn: async () => {
      const response = await apiClient.get<ManagedCell[]>('/steward/cells/managed');
      return response.data;
    },
  });
}
