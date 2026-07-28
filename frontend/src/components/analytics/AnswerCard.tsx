// src/components/analytics/AnswerCard.tsx
import type { ReactNode } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Stack,
  Skeleton,
  Divider,
  Chip,
} from '@mui/material';
import { SourceDocuments } from '../common/SourceDocuments';
import { ResponseMetadata } from '../common/ResponseMetadata';
import type { QueryResponse } from '@/types/query';

// ── Prop types ────────────────────────────────────────────────────────────────

interface AnswerCardProps {
  /** Section title displayed in the card header. */
  title: string;
  /** MUI icon node rendered in the accent badge. */
  icon: ReactNode;
  /** Response data from the RAG query, or undefined while loading/errored. */
  data: QueryResponse | undefined;
  isLoading: boolean;
  isError: boolean;
  /** Called when the user clicks the inline Retry button on an errored card. */
  onRetry: () => void;
  /** Controls the accent badge background colour. Defaults to 'primary'. */
  accentColor?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

// ── Sub-components ────────────────────────────────────────────────────────────

/**
 * Skeleton placeholder shown while the query is in flight.
 * Matches the approximate visual weight of a loaded answer.
 */
function LoadingSkeleton() {
  return (
    <Box>
      <Skeleton variant="text" width="55%" height={20} sx={{ mb: 1.5 }} />
      <Skeleton variant="text" width="100%" />
      <Skeleton variant="text" width="100%" />
      <Skeleton variant="text" width="92%" />
      <Skeleton variant="text" width="100%" />
      <Skeleton variant="text" width="78%" sx={{ mb: 2 }} />
      <Skeleton variant="text" width="88%" />
      <Skeleton variant="text" width="65%" />
    </Box>
  );
}



// ── Main component ────────────────────────────────────────────────────────────

/**
 * AnswerCard — the single reusable card used for every analytics section.
 *
 * Handles three states internally:
 *   - Loading  → skeleton lines matching the card's expected content height
 *   - Error    → inline error message + Retry chip (does not fill the page)
 *   - Data     → verbatim answer text, collapsible sources, metadata footer
 *
 * The answer text is displayed with `whiteSpace: pre-line` so that line breaks
 * produced by the LLM are preserved without treating the output as code.
 */
export function AnswerCard({
  title,
  icon,
  data,
  isLoading,
  isError,
  onRetry,
  accentColor = 'primary',
}: AnswerCardProps) {
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* ── Header ── */}
        <Stack direction="row" spacing={2} sx={{ alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: `${accentColor}.main`,
              color: `${accentColor}.contrastText`,
            }}
          >
            {icon}
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            {title}
          </Typography>
        </Stack>

        <Divider sx={{ mb: 2 }} />

        {/* ── Loading state ── */}
        {isLoading && <LoadingSkeleton />}

        {/* ── Error state ── */}
        {isError && !isLoading && (
          <Stack
            spacing={1}
            sx={{
              flexGrow: 1,
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              py: 4,
            }}
          >
            <Typography variant="body2" color="error.main" sx={{ fontWeight: 600 }}>
              Query failed
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ maxWidth: 320 }}>
              The analytics query could not be completed. Check that the backend is
              running and that reports have been indexed.
            </Typography>
            <Chip
              label="Retry"
              onClick={onRetry}
              color="primary"
              variant="outlined"
              size="small"
              clickable
              sx={{ mt: 1 }}
            />
          </Stack>
        )}

        {/* ── Data state ── */}
        {!isLoading && !isError && data && (
          <Box sx={{ flexGrow: 1 }}>
            {/* Answer text — verbatim from backend, line breaks preserved */}
            <Typography
              variant="body2"
              sx={{ lineHeight: 1.85, whiteSpace: 'pre-line', color: 'text.primary' }}
            >
              {data.answer}
            </Typography>

            {/* Sources */}
            {data.sources.length > 0 && (
              <>
                <Divider sx={{ mt: 2.5 }} />
                <SourceDocuments sources={data.sources} />
              </>
            )}

            {/* Metadata footer */}
            {data.metadata && (
              <>
                <Divider sx={{ mt: 2 }} />
                <ResponseMetadata metadata={data.metadata} />
              </>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
