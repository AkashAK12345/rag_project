// src/api/uploadApi.ts
import { axiosClient } from './axiosClient';
import type { JobAcceptedResponse } from '@/types/jobs';

export const uploadApi = {
  uploadFiles: async (
    files: File[],
    onProgress?: (pct: number) => void,
  ): Promise<JobAcceptedResponse> => {
    const form = new FormData();
    files.forEach((f) => form.append('files', f));

    const { data } = await axiosClient.post<JobAcceptedResponse>('/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (evt) => {
        if (evt.total && onProgress) {
          onProgress(Math.round((evt.loaded / evt.total) * 100));
        }
      },
    });
    return data;
  },
};
