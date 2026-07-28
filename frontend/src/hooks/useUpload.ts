// src/hooks/useUpload.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadApi } from '@/api/uploadApi';
import type { JobAcceptedResponse } from '@/types/jobs';

export function useUpload() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (variables: { files: File[]; onProgress?: (pct: number) => void }) =>
      uploadApi.uploadFiles(variables.files, variables.onProgress),
    onSuccess: (_data: JobAcceptedResponse) => {
      queryClient.invalidateQueries({ queryKey: ['jobs', 'list'] });
    },
  });
}
