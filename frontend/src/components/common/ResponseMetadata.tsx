// src/components/common/ResponseMetadata.tsx
import { Stack, Typography } from '@mui/material';
import { Speed, SmartToy, Article } from '@mui/icons-material';
import type { QueryResponse } from '@/types/query';

interface ResponseMetadataProps {
  metadata: NonNullable<QueryResponse['metadata']>;
}

/**
 * Metadata footer: latency, model name, and retrieved document count.
 */
export function ResponseMetadata({ metadata }: ResponseMetadataProps) {
  return (
    <Stack direction="row" spacing={2} sx={{ mt: 1.5, flexWrap: 'wrap', gap: 0.5 }}>
      <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
        <Speed sx={{ fontSize: 13, color: 'text.disabled' }} />
        <Typography variant="caption" color="text.disabled">
          {Math.round(metadata.latency_ms)}ms
        </Typography>
      </Stack>
      <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
        <SmartToy sx={{ fontSize: 13, color: 'text.disabled' }} />
        <Typography variant="caption" color="text.disabled">
          {metadata.model}
        </Typography>
      </Stack>
      <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
        <Article sx={{ fontSize: 13, color: 'text.disabled' }} />
        <Typography variant="caption" color="text.disabled">
          {metadata.retrieved_documents} docs retrieved
        </Typography>
      </Stack>
    </Stack>
  );
}
