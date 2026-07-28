// src/hooks/useAnalytics.ts
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { analyticsApi } from '@/api/analyticsApi';

/**
 * All analytics queries share these options.
 *
 * staleTime: 5 minutes — analytics data is expensive to compute; avoid
 *   unnecessary re-fetches when the user navigates away and returns quickly.
 *
 * gcTime: 15 minutes — keep the response in the TanStack Query cache so
 *   returning to the page within this window shows data without re-querying.
 *
 * enabled: controlled externally — queries are DISABLED by default and only
 *   fire when the user explicitly clicks "Generate Insights". This is the
 *   core of the on-demand workflow.
 */
const STALE_TIME = 5 * 60 * 1000;  // 5 minutes
const GC_TIME    = 15 * 60 * 1000; // 15 minutes

const baseOptions = (enabled: boolean) =>
  ({
    enabled,
    staleTime: STALE_TIME,
    gcTime: GC_TIME,
    retry: 1,
  }) as const;

// ── Individual section hooks ─────────────────────────────────────────────────

export function useKpiSummary(enabled: boolean) {
  return useQuery({
    queryKey: ['analytics', 'kpi_summary'],
    queryFn: analyticsApi.kpiSummary,
    ...baseOptions(enabled),
  });
}

export function useRevenueTrend(enabled: boolean) {
  return useQuery({
    queryKey: ['analytics', 'revenue_trend'],
    queryFn: analyticsApi.revenueTrend,
    ...baseOptions(enabled),
  });
}

export function useCostAnalysis(enabled: boolean) {
  return useQuery({
    queryKey: ['analytics', 'cost_analysis'],
    queryFn: analyticsApi.costAnalysis,
    ...baseOptions(enabled),
  });
}

export function useForecastRevenue(enabled: boolean) {
  return useQuery({
    queryKey: ['analytics', 'forecast_revenue'],
    queryFn: analyticsApi.forecastRevenue,
    ...baseOptions(enabled),
  });
}

export function useForecastInventory(enabled: boolean) {
  return useQuery({
    queryKey: ['analytics', 'forecast_inventory'],
    queryFn: analyticsApi.forecastInventory,
    ...baseOptions(enabled),
  });
}

export function useRisksAndOpportunities(enabled: boolean) {
  return useQuery({
    queryKey: ['analytics', 'risks_opportunities'],
    queryFn: analyticsApi.risksAndOpportunities,
    ...baseOptions(enabled),
  });
}

// ── Refresh helper ───────────────────────────────────────────────────────────

/**
 * Returns a function that invalidates every analytics query in the cache.
 *
 * Invalidation only triggers a network re-fetch for queries whose `enabled`
 * flag is currently true. The AnalyticsPage ensures `enabled` is set to true
 * before calling this, so all queries will immediately re-fire.
 */
export function useRefreshAnalytics() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ['analytics'] });
}
