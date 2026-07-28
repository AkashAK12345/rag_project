// src/components/common/SourceDocuments.tsx
import { useState } from 'react';
import {
  Box,
  Stack,
  Collapse,
  IconButton,
  Typography,
  Chip,
} from '@mui/material';
import { ExpandMore, Source } from '@mui/icons-material';
import type { QueryResponse } from '@/types/query';

interface SourceDocumentsProps {
  sources: QueryResponse['sources'];
}

/**
 * Collapsible list of retrieved source documents.
 * Toggled by the user — collapsed by default to keep the UI compact.
 */
export function SourceDocuments({ sources }: SourceDocumentsProps) {
  const [expanded, setExpanded] = useState(false);

  if (!sources.length) return null;

  return (
    <Box sx={{ mt: 2 }}>
      <Stack
        direction="row"
        sx={{
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          userSelect: 'none',
        }}
        onClick={() => setExpanded((prev) => !prev)}
      >
        <Stack direction="row" spacing={0.75} sx={{ alignItems: 'center' }}>
          <Source sx={{ fontSize: 15, color: 'text.disabled' }} />
          <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600 }}>
            {sources.length} source{sources.length !== 1 ? 's' : ''}
          </Typography>
        </Stack>
        <IconButton size="small" tabIndex={-1}>
          <ExpandMore
            sx={{
              fontSize: 18,
              color: 'text.disabled',
              transition: 'transform 0.2s ease',
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            }}
          />
        </IconButton>
      </Stack>

      <Collapse in={expanded} timeout="auto">
        <Stack spacing={1} sx={{ mt: 1 }}>
          {sources.map((src, idx) => (
            <Box
              key={idx}
              sx={{
                p: 1.25,
                borderRadius: 1.5,
                bgcolor: 'action.hover',
                border: (t) => `1px solid ${t.palette.divider}`,
              }}
            >
              <Stack
                direction="row"
                sx={{ justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}
              >
                <Box sx={{ minWidth: 0, mr: 1 }}>
                  <Typography
                    variant="caption"
                    sx={{ fontWeight: 600, display: 'block' }}
                    noWrap
                  >
                    {src.file}
                  </Typography>
                  {src.sheet && (
                    <Typography variant="caption" color="text.secondary">
                      Sheet: {src.sheet}
                    </Typography>
                  )}
                </Box>
                <Chip
                  label={`${(src.score * 100).toFixed(0)}%`}
                  size="small"
                  variant="outlined"
                  sx={{ flexShrink: 0, height: 20, fontSize: '0.65rem', fontWeight: 700 }}
                />
              </Stack>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ display: 'block', lineHeight: 1.5 }}
              >
                {src.preview}
              </Typography>
            </Box>
          ))}
        </Stack>
      </Collapse>
    </Box>
  );
}
