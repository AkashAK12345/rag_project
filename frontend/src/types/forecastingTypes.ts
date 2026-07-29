// src/types/forecastingTypes.ts
//
// TypeScript domain types for the Forecasting Dashboard.
//
// These types mirror the backend's ForecastMetric and ForecastHorizon enums
// (schemas/forecast_context.py) but exist independently in the frontend.
// They are used only for UI state and question-building — no business logic.

// ── Metric ────────────────────────────────────────────────────────────────────

export type ForecastMetricKey =
  | 'sales'
  | 'revenue'
  | 'inventory'
  | 'demand'
  | 'expenses'
  | 'profit'
  | 'branch_performance'
  | 'purchase';

export interface ForecastMetricOption {
  /** Canonical key matching backend ForecastMetric enum value. */
  key: ForecastMetricKey;
  /** Human-readable display label used in the UI. */
  label: string;
  /** Keyword(s) used in natural-language question construction. */
  triggerPhrase: string;
  /** MUI colour token for the chip accent. */
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
}

// ── Horizon ───────────────────────────────────────────────────────────────────

export type ForecastHorizonKey =
  | 'next_week'
  | 'next_month'
  | 'next_quarter'
  | 'next_year';

export interface ForecastHorizonOption {
  /** Canonical key matching backend ForecastHorizon enum value. */
  key: ForecastHorizonKey;
  /** Human-readable label. */
  label: string;
  /** Duration in days — display only, never sent to backend. */
  days: number;
  /** Phrase inserted verbatim into the forecast question. */
  phrase: string;
}

// ── Form State ────────────────────────────────────────────────────────────────

export interface ForecastFormState {
  selectedMetrics: ForecastMetricKey[];
  selectedHorizon: ForecastHorizonKey;
}
