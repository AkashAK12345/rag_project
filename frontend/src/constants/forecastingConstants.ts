// src/constants/forecastingConstants.ts
//
// Single source of truth for all forecasting UI options.
//
// Design decisions:
//   - No algorithm information is stored here (per architectural requirement:
//     the frontend must not duplicate backend business logic that is not
//     returned by the API).
//   - `triggerPhrase` values are chosen to exactly match the keyword vocabulary
//     in services/intent_service.py (_FORECAST_METRIC_RULES) so that the
//     forecastQuestionBuilder produces reliable intent detection.
//   - `phrase` values match _FORECAST_HORIZON_RULES in intent_service.py.
//   - `as const` prevents accidental mutation at runtime.

import type { ForecastMetricOption, ForecastHorizonOption, ForecastHorizonKey } from '@/types/forecastingTypes';

// ── Metric options ────────────────────────────────────────────────────────────

export const FORECAST_METRIC_OPTIONS: ForecastMetricOption[] = [
  {
    key: 'sales',
    label: 'Sales',
    triggerPhrase: 'sales',
    color: 'primary',
  },
  {
    key: 'revenue',
    label: 'Revenue',
    triggerPhrase: 'revenue',
    color: 'success',
  },
  {
    key: 'inventory',
    label: 'Inventory',
    triggerPhrase: 'inventory',
    color: 'warning',
  },
  {
    key: 'demand',
    label: 'Demand',
    triggerPhrase: 'demand',
    color: 'secondary',
  },
  {
    key: 'expenses',
    label: 'Expenses',
    triggerPhrase: 'expenses',
    color: 'error',
  },
  {
    key: 'profit',
    label: 'Profit',
    triggerPhrase: 'profit',
    color: 'success',
  },
  {
    key: 'branch_performance',
    label: 'Branch Performance',
    triggerPhrase: 'branch performance',
    color: 'info',
  },
  {
    key: 'purchase',
    label: 'Purchases',
    triggerPhrase: 'purchases',
    color: 'secondary',
  },
] as const;

// ── Horizon options ───────────────────────────────────────────────────────────

export const FORECAST_HORIZON_OPTIONS: ForecastHorizonOption[] = [
  {
    key: 'next_week',
    label: 'Next Week',
    days: 7,
    phrase: 'next week',
  },
  {
    key: 'next_month',
    label: 'Next Month',
    days: 30,
    phrase: 'next month',
  },
  {
    key: 'next_quarter',
    label: 'Next Quarter',
    days: 90,
    phrase: 'next quarter',
  },
  {
    key: 'next_year',
    label: 'Next Year',
    days: 365,
    phrase: 'next year',
  },
] as const;

// ── Lookup maps ───────────────────────────────────────────────────────────────

/** O(1) metric lookup by key. */
export const FORECAST_METRIC_MAP = Object.fromEntries(
  FORECAST_METRIC_OPTIONS.map((m) => [m.key, m]),
) as Record<string, ForecastMetricOption>;

/** O(1) horizon lookup by key. */
export const FORECAST_HORIZON_MAP = Object.fromEntries(
  FORECAST_HORIZON_OPTIONS.map((h) => [h.key, h]),
) as Record<string, ForecastHorizonOption>;

/** Default horizon applied when the page first mounts. */
export const DEFAULT_FORECAST_HORIZON: ForecastHorizonKey = 'next_month';
