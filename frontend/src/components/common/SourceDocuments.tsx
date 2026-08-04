// src/components/common/SourceDocuments.tsx
import { useState } from 'react';
import { Box, Stack, Collapse, IconButton, Typography, Chip } from '@mui/material';
import { ChevronDown, FileSearch, FileSpreadsheet } from 'lucide-react';
import type { QueryResponse } from '@/types/query';
import { brand, neutral, semantic } from '@/theme/colors';
import { radius } from '@/theme/radius';

interface SourceDocumentsProps {
  sources: QueryResponse['sources'];
}

export function SourceDocuments({ sources }: SourceDocumentsProps) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <Box sx={{ mt: 2.5, pt: 2, borderTop: '1px solid rgba(0,0,0,0.06)' }}>
      {/* Toggle row */}
      <Stack
        direction="row"
        sx={{ alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', mb: expanded ? 1.5 : 0 }}
        onClick={() => setExpanded((p) => !p)}
      >
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
          <FileSearch size={13} color={neutral[400]} />
          <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
            {sources.length} source{sources.length !== 1 ? 's' : ''} retrieved
          </Typography>
        </Stack>
        <IconButton size="small" tabIndex={-1} sx={{ p: 0.25, color: 'text.disabled' }}>
          <ChevronDown
            size={14}
            style={{
              transition: 'transform 200ms ease',
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            }}
          />
        </IconButton>
      </Stack>

      <Collapse in={expanded} timeout="auto">
        <Stack spacing={1.25}>
          {sources.map((src, idx) => (
            <Box
              key={idx}
              sx={{
                p: 1.75,
                borderRadius: `${radius.chip}px`,
                bgcolor: (t) => t.palette.mode === 'light' ? neutral[50] : 'rgba(255,255,255,0.04)',
                border: (t) => `1px solid ${t.palette.mode === 'light' ? neutral[100] : 'rgba(255,255,255,0.08)'}`,
                transition: 'border-color 150ms ease',
                '&:hover': { borderColor: `${brand.orange}55` },
              }}
            >
              <Stack direction="row" sx={{ alignItems: 'flex-start', gap: 1.5 }}>
                {/* File icon */}
                <Box
                  sx={{
                    width: 34,
                    height: 34,
                    borderRadius: `${radius.chip}px`,
                    bgcolor: brand.orangeSubtle,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: brand.orange,
                    flexShrink: 0,
                  }}
                >
                  <FileSpreadsheet size={16} />
                </Box>

                {/* File metadata */}
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 0.25, gap: 1 }}>
                    <Typography variant="caption" sx={{ fontWeight: 700, color: 'text.primary' }} noWrap>
                      {src.file}
                    </Typography>
                    <Chip
                      label={`${(src.score * 100).toFixed(0)}% match`}
                      size="small"
                      sx={{
                        height: 18,
                        fontSize: '0.6rem',
                        fontWeight: 700,
                        flexShrink: 0,
                        bgcolor: src.score >= 0.8 ? semantic.successSubtle : brand.orangeSubtle,
                        color: src.score >= 0.8 ? semantic.successDark : brand.orange,
                        border: `1px solid ${src.score >= 0.8 ? semantic.success : brand.orange}33`,
                        borderRadius: `${radius.full}px`,
                      }}
                    />
                  </Stack>
                  {src.sheet && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.75 }}>
                      Sheet: {src.sheet}
                    </Typography>
                  )}
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ display: 'block', lineHeight: 1.55, fontStyle: 'italic' }}
                  >
                    {src.preview}
                  </Typography>
                </Box>
              </Stack>
            </Box>
          ))}
        </Stack>
      </Collapse>
    </Box>
  );
}
