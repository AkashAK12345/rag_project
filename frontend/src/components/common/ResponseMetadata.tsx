// src/components/common/ResponseMetadata.tsx
import { Stack, Box, Typography } from '@mui/material';
import { Zap, BrainCircuit, FileSearch } from 'lucide-react';
import type { QueryResponse } from '@/types/query';

interface ResponseMetadataProps {
  metadata: NonNullable<QueryResponse['metadata']>;
}

export function ResponseMetadata({ metadata }: ResponseMetadataProps) {
  const chips = [
    { icon: <Zap size={10} />, label: `${Math.round(metadata.latency_ms)}ms` },
    { icon: <BrainCircuit size={10} />, label: metadata.model },
    { icon: <FileSearch size={10} />, label: `${metadata.retrieved_documents} docs` },
  ];

  return (
    <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 0.75 }}>
      {chips.map((chip, i) => (
        <Stack key={i} direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
          <Box sx={{ color: 'text.disabled', display: 'flex' }}>{chip.icon}</Box>
          <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 500 }}>
            {chip.label}
          </Typography>
        </Stack>
      ))}
    </Stack>
  );
}
