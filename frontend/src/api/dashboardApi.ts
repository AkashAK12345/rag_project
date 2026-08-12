import { axiosClient } from './axiosClient';
import type { AnalyticsDashboardResponse, ForecastDashboardResponse } from '@/types/dashboard';

export const dashboardApi = {
  getAnalytics: async (): Promise<AnalyticsDashboardResponse> => {
    const { data } = await axiosClient.get<AnalyticsDashboardResponse>('/analytics/dashboard');
    return data;
  },
  getForecast: async (horizon: string = 'next_month'): Promise<ForecastDashboardResponse> => {
    const { data } = await axiosClient.get<ForecastDashboardResponse>(`/forecast/dashboard?horizon=${horizon}`);
    return data;
  },
};
