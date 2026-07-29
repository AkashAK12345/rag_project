// src/hooks/useForecast.ts
//
// TanStack Query mutation hook for the Forecasting Dashboard.
//
// Architecture:
//   - Uses useMutation (not useQuery) because each forecast is explicitly
//     user-triggered and the question changes with form selections.
//   - Follows the same pattern as ChatPage's queryMutation.
//   - The hook owns no business logic — it only wraps the API call.
//   - No caching: forecasts are on-demand and parameterised (metric + horizon
//     combinations make a stable cache key impractical and unnecessary).

import { useMutation } from '@tanstack/react-query';
import { queryApi } from '@/api/queryApi';
import type { QueryResponse } from '@/types/query';

/**
 * Mutation hook for executing a forecast query.
 *
 * The caller builds the question string (via buildForecastQuestion) and passes
 * it as the mutation variable. The hook returns the standard TanStack Query
 * mutation state.
 *
 * @returns TanStack Query UseMutationResult for POST /api/v1/query
 */
export function useForecast() {
  return useMutation<QueryResponse, Error, string>({
    mutationFn: (question: string) => queryApi.query({ question }),
  });
}
