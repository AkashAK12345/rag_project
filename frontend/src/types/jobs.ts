// src/types/jobs.ts
export type JobStatus = 'queued' | 'validating' | 'saving_files' | 'indexing' | 'completed' | 'failed';

export interface JobRecord {
  job_id: string;
  connector_id?: string;
  status: JobStatus;
  progress_percentage: number;
  uploaded_files: string[];
  indexed_documents: number;
  skipped_files: string[];
  created_at: string;
  started_at?: string;
  completed_at?: string;
  processing_time_ms?: number;
  error_message?: string;
}

export interface JobAcceptedResponse {
  job_id: string;
  status: JobStatus;
  message: string;
}

export interface JobListResponse {
  total: number;
  jobs: JobRecord[];
}
