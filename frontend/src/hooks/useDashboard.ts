import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/api/dashboardApi';

export function useAnalyticsDashboard() {
  return useQuery({
    queryKey: ['analytics_dashboard'],
    queryFn: () => dashboardApi.getAnalytics(),
    retry: false,
  });
}

export function useForecastDashboard(horizon: string = 'next_month') {
  return useQuery({
    queryKey: ['forecast_dashboard', horizon],
    queryFn: () => dashboardApi.getForecast(horizon),
    retry: false,
  });
}
