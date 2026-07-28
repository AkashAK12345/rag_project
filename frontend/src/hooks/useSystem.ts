// src/hooks/useSystem.ts
import { useQuery } from '@tanstack/react-query';
import { systemApi } from '@/api/systemApi';

export function useSystemHealth() {
  return useQuery({
    queryKey: ['system', 'health'],
    queryFn: systemApi.health,
    refetchInterval: 60000, // Refresh every minute
  });
}

export function useIndexStats() {
  return useQuery({
    queryKey: ['system', 'index'],
    queryFn: systemApi.indexStats,
    refetchInterval: 60000,
  });
}

export function useModelConfigs() {
  return useQuery({
    queryKey: ['system', 'models'],
    queryFn: systemApi.modelConfigs,
    staleTime: Infinity, // Models don't change often
  });
}
