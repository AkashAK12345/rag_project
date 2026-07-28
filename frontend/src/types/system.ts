// src/types/system.ts
export interface HealthResponse {
  status: string;
  uptime_seconds: number;
  server_time: string;
  version: string;
  llm_loaded: boolean;
  embedding_loaded: boolean;
  index_loaded: boolean;
}

export interface IndexStatsResponse {
  indexed_files: number;
  indexed_documents: number;
  storage_directory: string;
  storage_size_bytes: number;
  last_indexing_timestamp?: number;
}

export interface ModelConfigsResponse {
  llm_provider: string;
  llm_model: string;
  embedding_model: string;
  vector_store_type: string;
}
