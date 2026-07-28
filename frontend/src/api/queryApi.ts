// src/api/queryApi.ts
import { axiosClient } from './axiosClient';
import type { QueryRequest, QueryResponse } from '@/types/query';

export const queryApi = {
  query: async (body: QueryRequest): Promise<QueryResponse> => {
    const { data } = await axiosClient.post<QueryResponse>('/query', body);
    return data;
  },
};
