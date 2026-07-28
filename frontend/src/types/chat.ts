// src/types/chat.ts
import type { SourceDocument, ResponseMetadata } from './query';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  sources?: SourceDocument[];
  metadata?: ResponseMetadata;
  isError?: boolean;
}
