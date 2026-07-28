// src/types/analytics.ts

/**
 * Identifies each named analytics section.
 * Used as the TanStack Query cache key discriminant and for labelling.
 */
export type AnalyticsSectionKey =
  | 'kpi_summary'
  | 'revenue_trend'
  | 'cost_analysis'
  | 'forecast_revenue'
  | 'forecast_inventory'
  | 'risks_opportunities';
