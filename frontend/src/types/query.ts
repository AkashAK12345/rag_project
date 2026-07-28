// src/types/query.ts
export interface QueryRequest {
  question: string;
}

export interface SourceDocument {
  file: string;
  sheet?: string;
  score: number;
  preview: string;
}

export interface ResponseMetadata {
  latency_ms: number;
  model: string;
  retrieved_documents: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceDocument[];
  metadata: ResponseMetadata;
}
