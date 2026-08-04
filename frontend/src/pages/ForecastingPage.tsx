// src/pages/ForecastingPage.tsx
import { useState, useCallback, useRef } from 'react';
import { Box, Button, CircularProgress, Stack, Chip, alpha } from '@mui/material';
import {
  LineChart,
  TrendingUp,
  RefreshCw,
  BarChart3,
} from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';
import { ForecastRequestForm } from '@/components/forecasting/ForecastRequestForm';
import { ForecastResultCard } from '@/components/forecasting/ForecastResultCard';
import { useForecast } from '@/hooks/useForecast';
import { buildForecastQuestion } from '@/utils/forecastQuestionBuilder';
import type { ForecastMetricKey, ForecastHorizonKey } from '@/types/forecastingTypes';
import type { QueryResponse } from '@/types/query';
import { radius } from '@/theme/radius';

interface CommittedForecast {
  data: QueryResponse | null;
  isError: boolean;
  errorMessage: string | undefined;
  metrics: ForecastMetricKey[];
  horizon: ForecastHorizonKey;
}

export function ForecastingPage() {
  const mutation = useForecast();

  const [committed, setCommitted] = useState<CommittedForecast | null>(null);

  const lastParamsRef = useRef<{ metrics: ForecastMetricKey[]; horizon: ForecastHorizonKey } | null>(null);

  const runForecast = useCallback(
    (metrics: ForecastMetricKey[], horizon: ForecastHorizonKey) => {
      lastParamsRef.current = { metrics, horizon };
      const question = buildForecastQuestion(metrics, horizon);

      mutation.mutate(question, {
        onSuccess: (data) => {
          setCommitted({
            data,
            isError: false,
            errorMessage: undefined,
            metrics,
            horizon,
          });
        },
        onError: (err) => {
          setCommitted((prev) =>
            prev
              ? { ...prev, isError: true, errorMessage: err.message }
              : {
                  data: null,
                  isError: true,
                  errorMessage: err.message,
                  metrics,
                  horizon,
                },
          );
        },
      });
    },
    [mutation],
  );

  const handleRetry = useCallback(() => {
    if (lastParamsRef.current) {
      const { metrics, horizon } = lastParamsRef.current;
      runForecast(metrics, horizon);
    }
  }, [runForecast]);

  const handleRefresh = useCallback(() => {
    handleRetry();
  }, [handleRetry]);

  const isPending = mutation.isPending;
  const hasResult = committed !== null;

  return (
    <Box>
      <PageHeader
        title="Forecasting"
        subtitle="Select business metrics and a time horizon to generate AI-powered forecasts from your indexed data."
        action={
          hasResult && !isPending ? (
            <Button
              id="refresh-forecast-button"
              variant="outlined"
              startIcon={<RefreshCw size={16} />}
              onClick={handleRefresh}
              disabled={!lastParamsRef.current}
              sx={{ borderRadius: `${radius.button}px`, px: 2, py: 1, fontWeight: 700 }}
            >
              Run Again
            </Button>
          ) : undefined
        }
      />

      <Stack spacing={4}>
        <ForecastRequestForm
          onSubmit={runForecast}
          isLoading={isPending}
        />

        {!hasResult && !isPending ? (
          <Box sx={{ mt: 2 }}>
            <EmptyState
              icon={<BarChart3 size={32} />}
              title="No Forecast Yet"
              description="Select one or more metrics above and choose a forecast horizon, then press Run Forecast to generate AI-powered predictions from your indexed business data."
              action={
                <Stack
                  direction="row"
                  spacing={1}
                  sx={{ justifyContent: 'center', mt: 2, flexWrap: 'wrap' }}
                >
                  {(['sales', 'revenue', 'inventory'] as ForecastMetricKey[]).map((key) => (
                    <Chip
                      key={key}
                      label={key.charAt(0).toUpperCase() + key.slice(1)}
                      size="small"
                      variant="outlined"
                      icon={<TrendingUp size={14} />}
                      sx={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        bgcolor: (t) => alpha(t.palette.primary.main, 0.05),
                        borderRadius: `${radius.full}px`,
                      }}
                    />
                  ))}
                </Stack>
              }
            />
          </Box>
        ) : isPending && !hasResult ? (
          <Box
            sx={{
              p: 6,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
              bgcolor: 'background.paper',
              borderRadius: `${radius.card}px`,
              border: (t) => `1px solid ${t.palette.divider}`,
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
            }}
          >
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: (t) =>
                  `linear-gradient(135deg, ${alpha(t.palette.primary.main, 0.15)}, ${alpha(t.palette.secondary.main, 0.15)})`,
              }}
            >
              <CircularProgress size={32} thickness={4} sx={{ color: 'primary.main' }} />
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Box
                component="span"
                sx={{
                  display: 'block',
                  fontWeight: 700,
                  fontSize: '1rem',
                  color: 'text.primary',
                  mb: 0.5,
                }}
              >
                Running Forecast…
              </Box>
              <Box
                component="span"
                sx={{ display: 'block', fontSize: '0.875rem', color: 'text.secondary' }}
              >
                The AI is analysing your indexed data and computing predictions.
              </Box>
            </Box>
          </Box>
        ) : (
          committed && (
            <ForecastResultCard
              data={isPending ? committed.data ?? undefined : (committed.data ?? undefined)}
              isLoading={isPending}
              isError={!isPending && committed.isError}
              errorMessage={committed.errorMessage}
              onRetry={handleRetry}
              requestedMetrics={committed.metrics}
              requestedHorizon={committed.horizon}
            />
          )
        )}

        {isPending && hasResult && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              p: 2,
              borderRadius: `${radius.card}px`,
              bgcolor: (t) => alpha(t.palette.primary.main, 0.06),
              border: (t) => `1px solid ${alpha(t.palette.primary.main, 0.15)}`,
            }}
          >
            <CircularProgress size={16} thickness={5} sx={{ color: 'primary.main' }} />
            <Box
              component="span"
              sx={{ fontSize: '0.875rem', color: 'primary.main', fontWeight: 600 }}
            >
              Running new forecast — previous result shown below…
            </Box>
            <LineChart size={18} style={{ color: 'var(--mui-palette-primary-main)', marginLeft: 'auto' }} />
          </Box>
        )}
      </Stack>
    </Box>
  );
}
