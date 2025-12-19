import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { valueflowsApi } from '@/api/valueflows';
import type { Exchange, CreateExchangeRequest, CreateEventRequest } from '@/types/valueflows';

export function useExchanges() {
  return useQuery({
    queryKey: ['exchanges'],
    queryFn: () => valueflowsApi.getExchanges(),
  });
}

export function useExchange(id: string) {
  return useQuery({
    queryKey: ['exchanges', id],
    queryFn: () => valueflowsApi.getExchange(id),
    enabled: !!id,
  });
}

export function useCreateExchange() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateExchangeRequest) => valueflowsApi.createExchange(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exchanges'] });
    },
  });
}

export function useUpdateExchange() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Exchange> }) =>
      valueflowsApi.updateExchange(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['exchanges'] });
      queryClient.invalidateQueries({ queryKey: ['exchanges', variables.id] });
    },
  });
}

export function useCreateEvent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateEventRequest) => valueflowsApi.createEvent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
      queryClient.invalidateQueries({ queryKey: ['exchanges'] });
    },
  });
}

export function useMatches() {
  return useQuery({
    queryKey: ['matches'],
    queryFn: () => valueflowsApi.getMatches(),
  });
}

export function useAcceptMatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => valueflowsApi.acceptMatch(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches'] });
    },
  });
}

export function useRejectMatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => valueflowsApi.rejectMatch(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches'] });
    },
  });
}

export function useCompleteExchange() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ exchangeId, agentId }: { exchangeId: string; agentId: string }) => {
      // First, create an event for the transfer
      const event = await valueflowsApi.createEvent({
        action: 'transfer',
        provider_id: agentId,
        resource_spec_id: 'placeholder', // Will be filled by backend from exchange
        quantity: 0, // Will be filled by backend from exchange
        unit: 'items',
      });

      // Then mark the exchange as complete with the event ID
      return valueflowsApi.completeExchange(exchangeId, agentId, event.id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exchanges'] });
    },
  });
}
