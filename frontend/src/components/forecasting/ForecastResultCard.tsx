// src/components/forecasting/ForecastResultCard.tsx
//
// Displays the result of a forecast query.
//
// Reuses:
//   - AnswerCard layout/styling patterns (loading skeleton, error inline, data body)
//   - SourceDocuments component (collapsible source list)
//   - ResponseMetadata component (latency, model, doc count footer)
//
// This component does NOT duplicate any existing functionality. All state
// management (loading, error, data) is owned by the parent (ForecastingPage).
// The component only receives and renders.

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
  Button,
  alpha,
} from '@mui/material';
import {
  ShowChart,
  ErrorOutlined,
  Refresh,
  CheckCircleOutlined,
} from '@mui/icons-material';
import { SourceDocuments } from '@/components/common/SourceDocuments';
import { ResponseMetadata } from '@/components/common/ResponseMetadata';
import type { QueryResponse } from '@/types/query';
import type { ForecastMetricKey, ForecastHorizonKey } from '@/types/forecastingTypes';
import { FORECAST_METRIC_MAP, FORECAST_HORIZON_MAP } from '@/constants/forecastingConstants';

// ── Props ─────────────────────────────────────────────────────────────────────

interface ForecastResultCardProps {
  /** The forecast response from the API. Undefined while loading. */
  data: QueryResponse | undefined;
  /** True while the forecast mutation is in flight. */
  isLoading: boolean;
  /** True if the last mutation ended in an error. */
  isError: boolean;
  /** Human-readable error message (from Error.message). */
  errorMessage?: string;
  /** Callback to retry the last forecast request. */
  onRetry: () => void;
  /** The metric keys that were used in the last request — for header badges. */
  requestedMetrics: ForecastMetricKey[];
  /** The horizon key that was used in the last request — for header badge. */
  requestedHorizon: ForecastHorizonKey;
}

// ── Loading skeleton ───────────────────────────────────────────────────────────

function ForecastLoadingSkeleton() {
  return (
    <Box>
      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
        <Skeleton variant="rounded" width={100} height={24} />
        <Skeleton variant="rounded" width={80} height={24} />
        <Skeleton variant="rounded" width={90} height={24} />
      </Stack>
      <Skeleton variant="text" width="60%" height={22} sx={{ mb: 1.5 }} />
      <Skeleton variant="text" width="100%" />
      <Skeleton variant="text" width="100%" />
      <Skeleton variant="text" width="88%" />
      <Skeleton variant="text" width="100%" />
      <Skeleton variant="text" width="73%" sx={{ mb: 2 }} />
      <Skeleton variant="text" width="95%" />
      <Skeleton variant="text" width="80%" />
      <Skeleton variant="text" width="65%" />
    </Box>
  );
}

// ── Header badge row ───────────────────────────────────────────────────────────

function ForecastBadgeRow({
  metrics,
  horizon,
}: {
  metrics: ForecastMetricKey[];
  horizon: ForecastHorizonKey;
}): ReactNode {
  const horizonOption = FORECAST_HORIZON_MAP[horizon];

  return (
    <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 0.75 }}>
      {metrics.map((key) => {
        const metricOption = FORECAST_METRIC_MAP[key];
        if (!metricOption) return null;
        return (
          <Chip
            key={key}
            label={metricOption.label}
            color={metricOption.color}
            size="small"
            variant="outlined"
            sx={{ fontWeight: 600, fontSize: '0.75rem' }}
          />
        );
      })}
      {horizonOption && (
        <Chip
          label={horizonOption.label}
          size="small"
          variant="filled"
          sx={{
            fontWeight: 700,
            fontSize: '0.75rem',
            bgcolor: (t) => alpha(t.palette.primary.main, 0.12),
            color: 'primary.main',
            border: 'none',
          }}
        />
      )}
    </Stack>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────

export function ForecastResultCard({
  data,
  isLoading,
  isError,
  errorMessage,
  onRetry,
  requestedMetrics,
  requestedHorizon,
}: ForecastResultCardProps) {
  return (
    <Card
      sx={{
        border: (t) => `1px solid ${t.palette.divider}`,
        borderRadius: 3,
        overflow: 'visible',
      }}
    >
      <CardContent sx={{ p: 3 }}>

        {/* ── Card Header ─────────────────────────────────────────────────── */}
        <Stack direction="row" spacing={2} sx={{ alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: 2,
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: (t) =>
                `linear-gradient(135deg, ${t.palette.primary.main} 0%, ${t.palette.secondary.main} 100%)`,
              color: 'white',
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
            }}
          >
            <ShowChart sx={{ fontSize: 22 }} />
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
              Forecast Results
            </Typography>
            {/* Show status badge when not loading */}
            {!isLoading && (
              <Box sx={{ mt: 0.75 }}>
                <ForecastBadgeRow metrics={requestedMetrics} horizon={requestedHorizon} />
              </Box>
            )}
          </Box>
          {/* Success indicator */}
          {!isLoading && !isError && data && (
            <CheckCircleOutlined sx={{ color: 'success.main', fontSize: 22 }} />
          )}
        </Stack>

        <Divider sx={{ mb: 2.5 }} />

        {/* ── Loading state ────────────────────────────────────────────────── */}
        {isLoading && <ForecastLoadingSkeleton />}

        {/* ── Error state ──────────────────────────────────────────────────── */}
        {isError && !isLoading && (
          <Box
            sx={{
              p: 3,
              borderRadius: 2,
              bgcolor: (t) => alpha(t.palette.error.main, 0.06),
              border: (t) => `1px solid ${alpha(t.palette.error.main, 0.2)}`,
            }}
          >
            <Stack spacing={1.5} sx={{ alignItems: 'center', textAlign: 'center' }}>
              <ErrorOutlined sx={{ fontSize: 44, color: 'error.main' }} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'error.main' }}>
                Forecast Failed
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 420 }}>
                {errorMessage ??
                  'The forecast query could not be completed. Ensure the backend is running and that reports have been indexed.'}
              </Typography>
              <Button
                id="forecast-retry-button"
                variant="outlined"
                color="error"
                startIcon={<Refresh />}
                onClick={onRetry}
                sx={{ mt: 0.5, fontWeight: 600 }}
              >
                Retry Forecast
              </Button>
            </Stack>
          </Box>
        )}

        {/* ── Data state ───────────────────────────────────────────────────── */}
        {!isLoading && !isError && data && (
          <Box>
            {/* Answer narrative — verbatim from the LLM, line breaks preserved */}
            <Typography
              variant="body2"
              sx={{
                lineHeight: 1.85,
                whiteSpace: 'pre-line',
                color: 'text.primary',
              }}
            >
              {data.answer}
            </Typography>

            {/* Source documents (collapsible) */}
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
