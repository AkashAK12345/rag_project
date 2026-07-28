// src/api/analyticsApi.ts
import { axiosClient } from './axiosClient';
import type { QueryResponse } from '@/types/query';
import { ANALYTICS_QUESTIONS } from '@/constants/analyticsQuestions';

/**
 * Posts a focused natural-language question to POST /api/v1/query.
 *
 * All question strings are sourced from @/constants/analyticsQuestions.ts —
 * this function is purely a transport layer with no embedded business logic.
 */
const ask = async (question: string): Promise<QueryResponse> => {
  const { data } = await axiosClient.post<QueryResponse>('/query', { question });
  return data;
};

export const analyticsApi = {
  kpiSummary:           (): Promise<QueryResponse> => ask(ANALYTICS_QUESTIONS.KPI_SUMMARY),
  revenueTrend:         (): Promise<QueryResponse> => ask(ANALYTICS_QUESTIONS.REVENUE_TREND),
  costAnalysis:         (): Promise<QueryResponse> => ask(ANALYTICS_QUESTIONS.COST_ANALYSIS),
  forecastRevenue:      (): Promise<QueryResponse> => ask(ANALYTICS_QUESTIONS.FORECAST_REVENUE),
  forecastInventory:    (): Promise<QueryResponse> => ask(ANALYTICS_QUESTIONS.FORECAST_INVENTORY),
  risksAndOpportunities:(): Promise<QueryResponse> => ask(ANALYTICS_QUESTIONS.RISKS_AND_OPPORTUNITIES),
};

