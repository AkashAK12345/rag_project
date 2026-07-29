// src/pages/ForecastingPage.tsx
//
// Phase 5 — Forecasting Dashboard
//
// Architecture:
//   - This page is the orchestrator. It owns state and wires components together.
//   - It has NO business logic — all intelligence is delegated:
//       * Question building → forecastQuestionBuilder.ts
//       * API mutation      → useForecast hook
//       * Form rendering    → ForecastRequestForm component
//       * Result rendering  → ForecastResultCard component
//       * Header/layout     → PageHeader (shared)
//
// Lifecycle (per implementation requirements):
//   - Initial state: form visible, no result panel.
//   - Pending: form disabled + loading state shown; previous result stays visible.
//   - Success: ForecastResultCard renders/replaces with new data.
//   - Error: inline error replaces the result area; form stays enabled.
//   - Retry: re-submits last params; form stays enabled during retry.
//
// Result preservation:
//   - Previous results are NOT cleared when the user changes form selections.
//   - Results are replaced only when a new request completes.
//   - This is achieved by storing the last successful/error state in local
//     component state, separate from the mutation state.

import { useState, useCallback, useRef } from 'react';
import { Box, Button, CircularProgress, Stack, Chip, alpha } from '@mui/material';
import {
  ShowChart,
  TrendingUp,
  Refresh,
  QueryStats,
} from '@mui/icons-material';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';
import { ForecastRequestForm } from '@/components/forecasting/ForecastRequestForm';
import { ForecastResultCard } from '@/components/forecasting/ForecastResultCard';
import { useForecast } from '@/hooks/useForecast';
import { buildForecastQuestion } from '@/utils/forecastQuestionBuilder';
import type { ForecastMetricKey, ForecastHorizonKey } from '@/types/forecastingTypes';
import type { QueryResponse } from '@/types/query';

// ── Types for committed result state ─────────────────────────────────────────

interface CommittedForecast {
  data: QueryResponse | null;
  isError: boolean;
  errorMessage: string | undefined;
  metrics: ForecastMetricKey[];
  horizon: ForecastHorizonKey;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function ForecastingPage() {
  const mutation = useForecast();

  // Committed result — updated only when a request completes (success or error).
  // This is what keeps the previous forecast visible while a new one is running.
  const [committed, setCommitted] = useState<CommittedForecast | null>(null);

  // Store the last params so Retry can re-submit without the user re-selecting.
  const lastParamsRef = useRef<{ metrics: ForecastMetricKey[]; horizon: ForecastHorizonKey } | null>(null);

  // ── Submit handler ──────────────────────────────────────────────────────────

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

  // ── Retry handler ─────────────────────────────────────────────────────────

  const handleRetry = useCallback(() => {
    if (lastParamsRef.current) {
      const { metrics, horizon } = lastParamsRef.current;
      runForecast(metrics, horizon);
    }
  }, [runForecast]);

  // ── Refresh handler (page header action) ─────────────────────────────────

  const handleRefresh = useCallback(() => {
    handleRetry();
  }, [handleRetry]);

  // ── Derived display state ─────────────────────────────────────────────────

  const isPending = mutation.isPending;
  const hasResult = committed !== null;

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <Box>
      {/* ── Page Header ─────────────────────────────────────────────────── */}
      <PageHeader
        title="Forecasting"
        subtitle="Select business metrics and a time horizon to generate AI-powered forecasts from your indexed data."
        action={
          hasResult && !isPending ? (
            <Button
              id="refresh-forecast-button"
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleRefresh}
              disabled={!lastParamsRef.current}
            >
              Run Again
            </Button>
          ) : undefined
        }
      />

      <Stack spacing={3}>
        {/* ── Forecast Request Form ─────────────────────────────────────── */}
        <ForecastRequestForm
          onSubmit={runForecast}
          isLoading={isPending}
        />

        {/* ── Result / Empty State area ─────────────────────────────────── */}
        {!hasResult && !isPending ? (
          /* Initial empty state — shown only before the first request */
          <EmptyState
            icon={<QueryStats />}
            title="No Forecast Yet"
            description="Select one or more metrics above and choose a forecast horizon, then press Run Forecast to generate AI-powered predictions from your indexed business data."
            action={
              <Stack
                direction="row"
                spacing={1}
                sx={{ justifyContent: 'center', mt: 1, flexWrap: 'wrap' }}
              >
                {(['sales', 'revenue', 'inventory'] as ForecastMetricKey[]).map((key) => (
                  <Chip
                    key={key}
                    label={key.charAt(0).toUpperCase() + key.slice(1)}
                    size="small"
                    variant="outlined"
                    icon={<TrendingUp sx={{ fontSize: '14px !important' }} />}
                    sx={{
                      fontSize: '0.75rem',
                      bgcolor: (t) => alpha(t.palette.primary.main, 0.05),
                    }}
                  />
                ))}
              </Stack>
            }
          />
        ) : isPending && !hasResult ? (
          /* First-ever request loading state (no previous result to show) */
          <Box
            sx={{
              p: 6,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
              bgcolor: 'background.paper',
              borderRadius: 3,
              border: (t) => `1px solid ${t.palette.divider}`,
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
              <CircularProgress size={32} thickness={4} />
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
          /* Result card — shown once a result exists (even while next request is pending) */
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

        {/* ── Footer: when pending AND there's a previous result ─────────── */}
        {isPending && hasResult && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              p: 1.5,
              borderRadius: 2,
              bgcolor: (t) => alpha(t.palette.primary.main, 0.06),
              border: (t) => `1px solid ${alpha(t.palette.primary.main, 0.15)}`,
            }}
          >
            <CircularProgress size={16} thickness={5} />
            <Box
              component="span"
              sx={{ fontSize: '0.875rem', color: 'primary.main', fontWeight: 500 }}
            >
              Running new forecast — previous result shown below…
            </Box>
            <ShowChart sx={{ fontSize: 18, color: 'primary.main', ml: 'auto' }} />
          </Box>
        )}
      </Stack>
    </Box>
  );
}
