// src/api/systemApi.ts
import { axiosClient } from './axiosClient';
import type { HealthResponse, IndexStatsResponse, ModelConfigsResponse } from '@/types/system';

export const systemApi = {
  health: async (): Promise<HealthResponse> => {
    const { data } = await axiosClient.get<HealthResponse>('/health');
    return data;
  },

  indexStats: async (): Promise<IndexStatsResponse> => {
    const { data } = await axiosClient.get<IndexStatsResponse>('/index');
    return data;
  },

  modelConfigs: async (): Promise<ModelConfigsResponse> => {
    const { data } = await axiosClient.get<ModelConfigsResponse>('/models');
    return data;
  },
};
