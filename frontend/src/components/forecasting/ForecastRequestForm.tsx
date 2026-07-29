// src/components/forecasting/ForecastRequestForm.tsx
//
// Reusable form component for composing a forecast request.
//
// Responsibilities (this component only):
//   - Render metric multi-select chips
//   - Render horizon selector cards
//   - Validate that at least one metric is selected
//   - Notify the parent via onSubmit(metrics, horizon)
//
// This component is NOT aware of:
//   - How questions are built (forecastQuestionBuilder owns that)
//   - The API or mutation state (ForecastingPage owns that)
//   - The previous forecast result (ForecastingPage owns that)

import { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Stack,
  Button,
  Divider,
  alpha,
  useTheme,
  Tooltip,
} from '@mui/material';
import {
  ShowChart,
  PlayArrow,
  SelectAll,
  ClearAll,
  CalendarViewWeek,
  CalendarViewMonth,
  DateRange,
  CalendarToday,
} from '@mui/icons-material';
import { FORECAST_METRIC_OPTIONS, FORECAST_HORIZON_OPTIONS, DEFAULT_FORECAST_HORIZON } from '@/constants/forecastingConstants';
import type { ForecastMetricKey, ForecastHorizonKey } from '@/types/forecastingTypes';

// ── Horizon icon map ──────────────────────────────────────────────────────────

const HORIZON_ICONS: Record<ForecastHorizonKey, React.ReactNode> = {
  next_week:    <CalendarViewWeek />,
  next_month:   <CalendarViewMonth />,
  next_quarter: <DateRange />,
  next_year:    <CalendarToday />,
};

// ── Props ─────────────────────────────────────────────────────────────────────

interface ForecastRequestFormProps {
  /** Called when the user submits the form with valid selections. */
  onSubmit: (metrics: ForecastMetricKey[], horizon: ForecastHorizonKey) => void;
  /** Disables the form while a forecast request is in flight. */
  isLoading?: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function ForecastRequestForm({ onSubmit, isLoading = false }: ForecastRequestFormProps) {
  const theme = useTheme();

  const [selectedMetrics, setSelectedMetrics] = useState<ForecastMetricKey[]>([]);
  const [selectedHorizon, setSelectedHorizon] = useState<ForecastHorizonKey>(DEFAULT_FORECAST_HORIZON);

  // ── Metric handlers ─────────────────────────────────────────────────────────

  const toggleMetric = useCallback((key: ForecastMetricKey) => {
    setSelectedMetrics((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key],
    );
  }, []);

  const handleSelectAll = useCallback(() => {
    setSelectedMetrics(FORECAST_METRIC_OPTIONS.map((m) => m.key));
  }, []);

  const handleClearAll = useCallback(() => {
    setSelectedMetrics([]);
  }, []);

  // ── Submit handler ──────────────────────────────────────────────────────────

  const handleSubmit = useCallback(() => {
    if (selectedMetrics.length > 0) {
      onSubmit(selectedMetrics, selectedHorizon);
    }
  }, [selectedMetrics, selectedHorizon, onSubmit]);

  const isSubmitDisabled = isLoading || selectedMetrics.length === 0;
  const allSelected = selectedMetrics.length === FORECAST_METRIC_OPTIONS.length;

  return (
    <Card
      sx={{
        border: (t) => `1px solid ${t.palette.divider}`,
        borderRadius: 3,
        overflow: 'visible',
      }}
    >
      <CardContent sx={{ p: 3 }}>

        {/* ── Section: Metric Selector ──────────────────────────────────────── */}
        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.25 }}>
              Select Metrics
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Choose one or more business metrics to forecast
            </Typography>
          </Box>

          <Stack direction="row" spacing={1}>
            <Tooltip title="Select all metrics">
              <span>
                <Button
                  size="small"
                  variant="text"
                  startIcon={<SelectAll />}
                  onClick={handleSelectAll}
                  disabled={isLoading || allSelected}
                  sx={{ fontSize: '0.75rem' }}
                >
                  All
                </Button>
              </span>
            </Tooltip>
            <Tooltip title="Clear all selections">
              <span>
                <Button
                  size="small"
                  variant="text"
                  color="inherit"
                  startIcon={<ClearAll />}
                  onClick={handleClearAll}
                  disabled={isLoading || selectedMetrics.length === 0}
                  sx={{ fontSize: '0.75rem', color: 'text.secondary' }}
                >
                  Clear
                </Button>
              </span>
            </Tooltip>
          </Stack>
        </Stack>

        <Box
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 1.25,
            p: 2,
            bgcolor: 'background.default',
            borderRadius: 2,
            border: (t) => `1px solid ${t.palette.divider}`,
            mb: 3,
          }}
        >
          {FORECAST_METRIC_OPTIONS.map((metric) => {
            const isSelected = selectedMetrics.includes(metric.key);
            return (
              <Chip
                key={metric.key}
                id={`metric-chip-${metric.key}`}
                label={metric.label}
                onClick={() => !isLoading && toggleMetric(metric.key)}
                variant={isSelected ? 'filled' : 'outlined'}
                color={isSelected ? metric.color : 'default'}
                clickable={!isLoading}
                sx={{
                  fontWeight: 600,
                  fontSize: '0.8125rem',
                  px: 0.5,
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  opacity: isLoading ? 0.6 : 1,
                  transition: 'all 0.15s ease',
                  ...(isSelected && {
                    boxShadow: `0 0 0 2px ${alpha(theme.palette[metric.color]?.main ?? theme.palette.primary.main, 0.25)}`,
                  }),
                }}
              />
            );
          })}
        </Box>

        {/* Validation hint */}
        {selectedMetrics.length === 0 && (
          <Typography
            variant="caption"
            color="warning.main"
            sx={{ display: 'block', mb: 2, mt: -1.5, fontWeight: 500 }}
          >
            ⚠ Select at least one metric to enable the forecast.
          </Typography>
        )}

        <Divider sx={{ mb: 3 }} />

        {/* ── Section: Horizon Selector ─────────────────────────────────────── */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.25 }}>
            Forecast Horizon
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
            Select the time window for the prediction
          </Typography>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
              gap: 1.5,
            }}
          >
            {FORECAST_HORIZON_OPTIONS.map((horizon) => {
              const isSelected = selectedHorizon === horizon.key;
              return (
                <Box
                  key={horizon.key}
                  id={`horizon-card-${horizon.key}`}
                  onClick={() => !isLoading && setSelectedHorizon(horizon.key)}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: (t) =>
                      `2px solid ${isSelected ? t.palette.primary.main : t.palette.divider}`,
                    bgcolor: isSelected
                      ? (t) => alpha(t.palette.primary.main, 0.08)
                      : 'background.default',
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    opacity: isLoading ? 0.6 : 1,
                    transition: 'all 0.18s ease',
                    textAlign: 'center',
                    userSelect: 'none',
                    '&:hover': {
                      borderColor: isLoading ? undefined : 'primary.main',
                      bgcolor: isLoading
                        ? undefined
                        : (t) => alpha(t.palette.primary.main, isSelected ? 0.08 : 0.04),
                    },
                  }}
                >
                  <Box
                    sx={{
                      color: isSelected ? 'primary.main' : 'text.disabled',
                      mb: 0.75,
                      display: 'flex',
                      justifyContent: 'center',
                      '& svg': { fontSize: 28 },
                      transition: 'color 0.18s ease',
                    }}
                  >
                    {HORIZON_ICONS[horizon.key]}
                  </Box>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 700,
                      color: isSelected ? 'primary.main' : 'text.primary',
                      lineHeight: 1.1,
                      mb: 0.25,
                    }}
                  >
                    {horizon.days}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 600,
                      color: isSelected ? 'primary.main' : 'text.secondary',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    {isSelected ? horizon.label : `days`}
                  </Typography>
                  {isSelected && (
                    <Typography
                      variant="caption"
                      sx={{ display: 'block', color: 'primary.main', mt: 0.25, fontWeight: 500 }}
                    >
                      {horizon.label}
                    </Typography>
                  )}
                </Box>
              );
            })}
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* ── Submit ────────────────────────────────────────────────────────── */}
        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            {selectedMetrics.length > 0
              ? `${selectedMetrics.length} metric${selectedMetrics.length > 1 ? 's' : ''} selected`
              : 'No metrics selected'}
          </Typography>

          <Button
            id="run-forecast-button"
            variant="contained"
            size="large"
            startIcon={isLoading ? undefined : <PlayArrow />}
            onClick={handleSubmit}
            disabled={isSubmitDisabled}
            sx={{
              px: 4,
              py: 1.25,
              fontWeight: 700,
              fontSize: '0.9375rem',
              borderRadius: 2,
              minWidth: 180,
              background: isSubmitDisabled
                ? undefined
                : (t) =>
                    `linear-gradient(135deg, ${t.palette.primary.main} 0%, ${t.palette.secondary.main} 100%)`,
              boxShadow: isSubmitDisabled
                ? undefined
                : '0 4px 15px rgba(99, 102, 241, 0.35)',
              '&:hover': {
                boxShadow: '0 6px 20px rgba(99, 102, 241, 0.45)',
              },
              transition: 'all 0.2s ease',
            }}
          >
            {isLoading ? (
              <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
                <ShowChart sx={{ fontSize: 18, animation: 'pulse 1.5s ease-in-out infinite' }} />
                <span>Forecasting…</span>
              </Stack>
            ) : (
              'Run Forecast'
            )}
          </Button>
        </Stack>

        {/* Pulse animation keyframe */}
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
          }
        `}</style>
      </CardContent>
    </Card>
  );
}
