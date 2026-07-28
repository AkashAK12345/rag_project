// src/constants/analyticsQuestions.ts

/**
 * Centralized prompt strings for every analytics RAG query.
 *
 * These questions drive the backend's deterministic engines:
 *   - AnalyticsEngine (KPI summary, revenue trend, cost analysis)
 *   - ForecastingEngine (revenue forecast, inventory forecast)
 *   - ReasoningEngine (risks & opportunities)
 *
 * Design decisions:
 *   - `as const` ensures string literal types, preventing accidental mutation.
 *   - Questions are written to be deterministic — same input → same engine path.
 *   - All prompt engineering lives here. The API layer stays free of business logic.
 *   - To refine a prompt, edit only this file.
 */
export const ANALYTICS_QUESTIONS = {
  KPI_SUMMARY:
    'Provide a comprehensive KPI summary for the business. Include total revenue, total sales volume, ' +
    'food cost percentage, gross profit margin, and overall business health status across all available data.',

  REVENUE_TREND:
    'Analyze the revenue trends over time across all available reporting periods. ' +
    'Identify growth patterns, seasonal peaks, declines, and any significant changes.',

  COST_ANALYSIS:
    'Analyze all business costs including food costs, purchase costs, and operational expenses. ' +
    'What is the food cost percentage, cost efficiency rating, and are there any cost concerns?',

  FORECAST_REVENUE:
    'Based on historical revenue data, forecast revenue for the next month and next quarter. ' +
    'State the forecasting methodology, the predicted values, confidence levels, and key assumptions.',

  FORECAST_INVENTORY:
    'Forecast inventory demand and purchase quantities needed for the next month based on historical ' +
    'consumption patterns and current stock levels. Include confidence levels and any caveats.',

  RISKS_AND_OPPORTUNITIES:
    'Identify the top business risks and strategic opportunities across all domains including sales, ' +
    'inventory, purchases, finance, production, and operations. Prioritize by severity.',
} as const;
