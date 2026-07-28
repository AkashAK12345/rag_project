// src/hooks/useJobs.ts
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { jobsApi } from '@/api/jobsApi';
import type { JobStatus } from '@/types/jobs';

export function useJobs() {
  return useQuery({
    queryKey: ['jobs', 'list'],
    queryFn: jobsApi.listJobs,
    refetchInterval: (query) => {
      // Poll every 5s if any job is active
      const hasActive = query.state.data?.jobs?.some(
        (j) => ['queued', 'validating', 'saving_files', 'indexing'].includes(j.status)
      );
      return hasActive ? 5000 : false;
    },
  });
}

export function useJobPolling(jobId: string | null) {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: ['jobs', 'detail', jobId],
    queryFn: () => (jobId ? jobsApi.getJob(jobId) : null),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status as JobStatus | undefined;
      // Stop polling if completed or failed
      if (status === 'completed' || status === 'failed') {
        // Also invalidate list so it updates the overall history
        queryClient.invalidateQueries({ queryKey: ['jobs', 'list'] });
        queryClient.invalidateQueries({ queryKey: ['system', 'index'] });
        return false;
      }
      return 2000; // poll every 2 seconds
    },
  });
}
