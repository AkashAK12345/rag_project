// src/utils/forecastQuestionBuilder.ts
//
// Single source of truth for forecast natural-language question construction.
//
// Architectural role:
//   This utility is the ONLY place in the frontend where forecast question
//   strings are assembled. The ForecastingPage passes user selections here
//   and receives a ready-to-submit question string. No string concatenation
//   lives in the page or the form component.
//
// Design constraints:
//   - Pure function — no side effects, no imports from React.
//   - Zero business logic — it maps UI selections to trigger keywords only.
//   - Trigger keywords are chosen to match _FORECAST_TRIGGER_KEYWORDS,
//     _FORECAST_METRIC_RULES, and _FORECAST_HORIZON_RULES in
//     services/intent_service.py so that the backend reliably activates the
//     ForecastingService pipeline.
//
// Keyword guarantee:
//   The word "forecast" is always present → satisfies _FORECAST_TRIGGER_KEYWORDS.
//   Each metric's triggerPhrase matches the vocabulary in _FORECAST_METRIC_RULES.
//   The horizon phrase (e.g. "next month") matches _FORECAST_HORIZON_RULES.

import type { ForecastMetricKey, ForecastHorizonKey } from '@/types/forecastingTypes';
import { FORECAST_METRIC_MAP, FORECAST_HORIZON_MAP } from '@/constants/forecastingConstants';

/**
 * Build a deterministic natural-language forecast question from UI selections.
 *
 * The returned string is passed directly to POST /api/v1/query as the
 * `question` field. The backend's IntentService will detect the forecast
 * intent, extract metrics and horizon, and activate ForecastingService.
 *
 * @param metrics  - One or more ForecastMetricKey values selected by the user.
 *                   Must be non-empty (validated by the form before calling).
 * @param horizon  - The ForecastHorizonKey selected by the user.
 * @returns        A ready-to-submit question string.
 *
 * @example
 * buildForecastQuestion(['sales', 'revenue'], 'next_month')
 * // → "Forecast sales and revenue for next month. ..."
 *
 * @example
 * buildForecastQuestion(['inventory'], 'next_week')
 * // → "Forecast inventory for next week. ..."
 */
export function buildForecastQuestion(
  metrics: ForecastMetricKey[],
  horizon: ForecastHorizonKey,
): string {
  if (metrics.length === 0) {
    throw new Error('buildForecastQuestion: metrics array must not be empty.');
  }

  const metricPhrases = metrics
    .map((key) => FORECAST_METRIC_MAP[key]?.triggerPhrase ?? key)
    .join(', ');

  const horizonOption = FORECAST_HORIZON_MAP[horizon];
  const horizonPhrase = horizonOption?.phrase ?? horizon.replace('_', ' ');

  return (
    `Forecast ${metricPhrases} for ${horizonPhrase}. ` +
    `Provide the predicted values, confidence levels, prediction intervals ` +
    `(lower and upper bounds), number of historical observations used, ` +
    `and any important caveats or assumptions about the forecast.`
  );
}
