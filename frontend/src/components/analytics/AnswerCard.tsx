// src/components/analytics/AnswerCard.tsx
import type { ReactNode } from 'react';
import { Card, CardContent, Typography, Box, Stack, Skeleton, Chip } from '@mui/material';
import { RefreshCw, AlertCircle } from 'lucide-react';
import { SourceDocuments } from '../common/SourceDocuments';
import { ResponseMetadata } from '../common/ResponseMetadata';
import type { QueryResponse } from '@/types/query';
import { brand, semantic } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

// ── Prop types ────────────────────────────────────────────────────────────────

interface AnswerCardProps {
  /** Section title displayed in the card header. */
  title: string;
  /** Icon node rendered in the accent badge. */
  icon: ReactNode;
  /** Response data from the RAG query, or undefined while loading/errored. */
  data: QueryResponse | undefined;
  isLoading: boolean;
  isError: boolean;
  /** Called when the user clicks the inline Retry chip on an errored card. */
  onRetry: () => void;
  /** Controls the accent strip colour. Defaults to 'primary'. */
  accentColor?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

// Accent color → visual tokens
const accentMap: Record<string, { strip: string; iconBg: string; iconColor: string }> = {
  primary:   { strip: brand.orange,    iconBg: brand.orangeSubtle,      iconColor: brand.orange },
  secondary: { strip: semantic.info,   iconBg: semantic.infoSubtle,     iconColor: semantic.info },
  success:   { strip: semantic.success, iconBg: semantic.successSubtle, iconColor: semantic.success },
  warning:   { strip: semantic.warning, iconBg: semantic.warningSubtle, iconColor: semantic.warning },
  error:     { strip: semantic.error,   iconBg: semantic.errorSubtle,   iconColor: semantic.error },
};

// ── Loading skeleton ──────────────────────────────────────────────────────────

function LoadingSkeleton() {
  return (
    <Box sx={{ pt: 0.5 }}>
      <Skeleton variant="text" width="45%" height={20} sx={{ mb: 1.5, borderRadius: 1 }} />
      {[100, 100, 92, 100, 78, 88, 65].map((w, i) => (
        <Skeleton key={i} variant="text" width={`${w}%`} sx={{ mb: 0.5, borderRadius: 1 }} />
      ))}
    </Box>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function AnswerCard({
  title,
  icon,
  data,
  isLoading,
  isError,
  onRetry,
  accentColor = 'primary',
}: AnswerCardProps) {
  const accent = accentMap[accentColor] ?? accentMap.primary;

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: `${radius.card}px`,
        boxShadow: shadows.card,
        border: 'none',
        overflow: 'hidden',
        transition: 'box-shadow 200ms ease',
        '&:hover': { boxShadow: shadows.cardHover },
      }}
    >
      {/* Orange accent strip */}
      <Box sx={{ height: 4, bgcolor: accent.strip, flexShrink: 0 }} />

      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 3 }}>
        {/* Header */}
        <Stack direction="row" spacing={2} sx={{ alignItems: 'center', mb: 3 }}>
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: `${radius.avatar}px`,
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: accent.iconBg,
              color: accent.iconColor,
              '& svg': { width: 20, height: 20 },
            }}
          >
            {icon}
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            {title}
          </Typography>
        </Stack>

        {/* Loading */}
        {isLoading && <LoadingSkeleton />}

        {/* Error */}
        {isError && !isLoading && (
          <Stack
            spacing={1.5}
            sx={{
              flexGrow: 1,
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              py: 5,
            }}
          >
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: `${radius.avatar}px`,
                bgcolor: semantic.errorSubtle,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AlertCircle size={22} color={semantic.error} />
            </Box>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
              Query failed
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ maxWidth: 300, lineHeight: 1.5 }}>
              Make sure reports are indexed and the backend is running.
            </Typography>
            <Chip
              label="Retry"
              icon={<RefreshCw size={10} />}
              onClick={onRetry}
              size="small"
              sx={{
                mt: 0.5,
                bgcolor: brand.orangeSubtle,
                color: brand.orange,
                fontWeight: 700,
                borderRadius: `${radius.full}px`,
                border: `1px solid ${brand.orange}33`,
                cursor: 'pointer',
                '& .MuiChip-icon': { color: brand.orange, ml: '6px' },
              }}
            />
          </Stack>
        )}

        {/* Data */}
        {!isLoading && !isError && data && (
          <Box sx={{ flexGrow: 1 }}>
            <Typography
              variant="body2"
              sx={{ lineHeight: 1.85, whiteSpace: 'pre-line', color: 'text.primary' }}
            >
              {data.answer}
            </Typography>

            {data.sources.length > 0 && (
              <Box sx={{ mt: 2.5, pt: 2, borderTop: (t) => `1px solid ${t.palette.divider}` }}>
                <SourceDocuments sources={data.sources} />
              </Box>
            )}

            {data.metadata && (
              <Box sx={{ mt: 1.5, pt: 1.5, borderTop: (t) => `1px solid ${t.palette.divider}` }}>
                <ResponseMetadata metadata={data.metadata} />
              </Box>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
