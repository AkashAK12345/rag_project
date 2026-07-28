// src/api/jobsApi.ts
import { axiosClient } from './axiosClient';
import type { JobRecord, JobListResponse } from '@/types/jobs';

export const jobsApi = {
  listJobs: async (): Promise<JobListResponse> => {
    const { data } = await axiosClient.get<JobListResponse>('/jobs');
    return data;
  },

  getJob: async (jobId: string): Promise<JobRecord> => {
    const { data } = await axiosClient.get<JobRecord>(`/jobs/${jobId}`);
    return data;
  },

  deleteJob: async (jobId: string): Promise<void> => {
    await axiosClient.delete(`/jobs/${jobId}`);
  },
};
