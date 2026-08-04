// src/hooks/useSystem.ts
import { useQuery } from '@tanstack/react-query';
import { systemApi } from '@/api/systemApi';

export function useSystemHealth() {
  return useQuery({
    queryKey: ['system', 'health'],
    queryFn: systemApi.health,
    refetchInterval: 10000, // Refresh every 10 seconds
  });
}

export function useIndexStats() {
  return useQuery({
    queryKey: ['system', 'index'],
    queryFn: systemApi.indexStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

export function useModelConfigs() {
  return useQuery({
    queryKey: ['system', 'models'],
    queryFn: systemApi.modelConfigs,
    refetchInterval: 300000, // Refresh every 5 minutes
    staleTime: 300000,
  });
}
