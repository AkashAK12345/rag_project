// src/components/forecasting/ForecastResultCard.tsx
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
  LineChart,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react';
import { SourceDocuments } from '@/components/common/SourceDocuments';
import { ResponseMetadata } from '@/components/common/ResponseMetadata';
import type { QueryResponse } from '@/types/query';
import type { ForecastMetricKey, ForecastHorizonKey } from '@/types/forecastingTypes';
import { FORECAST_METRIC_MAP, FORECAST_HORIZON_MAP } from '@/constants/forecastingConstants';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

interface ForecastResultCardProps {
  data: QueryResponse | undefined;
  isLoading: boolean;
  isError: boolean;
  errorMessage?: string;
  onRetry: () => void;
  requestedMetrics: ForecastMetricKey[];
  requestedHorizon: ForecastHorizonKey;
}

function ForecastLoadingSkeleton() {
  return (
    <Box>
      <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
        <Skeleton variant="rounded" width={100} height={24} sx={{ borderRadius: `${radius.full}px` }} />
        <Skeleton variant="rounded" width={80} height={24} sx={{ borderRadius: `${radius.full}px` }} />
        <Skeleton variant="rounded" width={90} height={24} sx={{ borderRadius: `${radius.full}px` }} />
      </Stack>
      <Skeleton variant="text" width="60%" height={24} sx={{ mb: 2 }} />
      <Skeleton variant="text" width="100%" height={20} />
      <Skeleton variant="text" width="100%" height={20} />
      <Skeleton variant="text" width="88%" height={20} />
      <Skeleton variant="text" width="100%" height={20} />
      <Skeleton variant="text" width="73%" height={20} sx={{ mb: 3 }} />
      <Skeleton variant="text" width="95%" height={20} />
      <Skeleton variant="text" width="80%" height={20} />
      <Skeleton variant="text" width="65%" height={20} />
    </Box>
  );
}

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
            sx={{ fontWeight: 700, fontSize: '0.75rem', borderRadius: `${radius.full}px` }}
          />
        );
      })}
      {horizonOption && (
        <Chip
          label={horizonOption.label}
          size="small"
          variant="filled"
          sx={{
            fontWeight: 800,
            fontSize: '0.75rem',
            bgcolor: (t) => alpha(t.palette.primary.main, 0.12),
            color: 'primary.main',
            border: 'none',
            borderRadius: `${radius.full}px`,
          }}
        />
      )}
    </Stack>
  );
}

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
      elevation={0}
      sx={{
        border: 'none',
        borderRadius: `${radius.card}px`,
        boxShadow: shadows.card,
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Top accent strip */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          background: (t) => `linear-gradient(90deg, ${t.palette.primary.main}, ${t.palette.secondary.main})`,
        }}
      />
      <CardContent sx={{ p: { xs: 3, md: 4 }, pt: { xs: 4, md: 5 } }}>

        {/* ── Card Header ─────────────────────────────────────────────────── */}
        <Stack direction="row" spacing={2.5} sx={{ alignItems: 'flex-start', mb: 3 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: `${radius.chip}px`,
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: (t) => alpha(t.palette.primary.main, 0.1),
              color: 'primary.main',
            }}
          >
            <LineChart size={24} />
          </Box>
          <Box sx={{ flexGrow: 1, pt: 0.5 }}>
            <Typography variant="h6" sx={{ fontWeight: 800, lineHeight: 1.2, letterSpacing: '-0.01em', mb: 0.5 }}>
              Forecast Results
            </Typography>
            {/* Show status badge when not loading */}
            {!isLoading && (
              <Box sx={{ mt: 1 }}>
                <ForecastBadgeRow metrics={requestedMetrics} horizon={requestedHorizon} />
              </Box>
            )}
          </Box>
          {/* Success indicator */}
          {!isLoading && !isError && data && (
            <Box sx={{ pt: 1 }}>
              <CheckCircle2 size={24} color="var(--mui-palette-success-main)" />
            </Box>
          )}
        </Stack>

        <Divider sx={{ mb: 3, opacity: 0.6 }} />

        {/* ── Loading state ────────────────────────────────────────────────── */}
        {isLoading && <ForecastLoadingSkeleton />}

        {/* ── Error state ──────────────────────────────────────────────────── */}
        {isError && !isLoading && (
          <Box
            sx={{
              p: 4,
              borderRadius: `${radius.card}px`,
              bgcolor: (t) => alpha(t.palette.error.main, 0.04),
              border: (t) => `1px solid ${alpha(t.palette.error.main, 0.1)}`,
            }}
          >
            <Stack spacing={2} sx={{ alignItems: 'center', textAlign: 'center' }}>
              <AlertCircle size={48} color="var(--mui-palette-error-main)" />
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 800, color: 'error.main', mb: 1 }}>
                  Forecast Failed
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 420, mx: 'auto', lineHeight: 1.6 }}>
                  {errorMessage ??
                    'The forecast query could not be completed. Ensure the backend is running and that reports have been indexed.'}
                </Typography>
              </Box>
              <Button
                id="forecast-retry-button"
                variant="outlined"
                color="error"
                startIcon={<RefreshCw size={16} />}
                onClick={onRetry}
                sx={{ mt: 1, fontWeight: 700, borderRadius: `${radius.button}px`, px: 3 }}
              >
                Retry Forecast
              </Button>
            </Stack>
          </Box>
        )}

        {/* ── Data state ───────────────────────────────────────────────────── */}
        {!isLoading && !isError && data && (
          <Box>
            <Typography
              variant="body1"
              sx={{
                lineHeight: 1.85,
                whiteSpace: 'pre-line',
                color: 'text.primary',
                fontSize: '0.9375rem',
              }}
            >
              {data.answer}
            </Typography>

            {data.sources.length > 0 && (
              <>
                <Box sx={{ mt: 4 }} />
                <SourceDocuments sources={data.sources} />
              </>
            )}

            {data.metadata && (
              <>
                <Divider sx={{ mt: 3, mb: 2, opacity: 0.6 }} />
                <ResponseMetadata metadata={data.metadata} />
              </>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
