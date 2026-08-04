// src/components/forecasting/ForecastRequestForm.tsx
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
  LineChart,
  Play,
  CheckSquare,
  Square,
  CalendarRange,
  CalendarDays,
  Calendar,
  CalendarCheck,
} from 'lucide-react';
import { FORECAST_METRIC_OPTIONS, FORECAST_HORIZON_OPTIONS, DEFAULT_FORECAST_HORIZON } from '@/constants/forecastingConstants';
import type { ForecastMetricKey, ForecastHorizonKey } from '@/types/forecastingTypes';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

const HORIZON_ICONS: Record<ForecastHorizonKey, React.ReactNode> = {
  next_week:    <CalendarRange size={28} />,
  next_month:   <CalendarDays size={28} />,
  next_quarter: <Calendar size={28} />,
  next_year:    <CalendarCheck size={28} />,
};

interface ForecastRequestFormProps {
  onSubmit: (metrics: ForecastMetricKey[], horizon: ForecastHorizonKey) => void;
  isLoading?: boolean;
}

export function ForecastRequestForm({ onSubmit, isLoading = false }: ForecastRequestFormProps) {
  const theme = useTheme();

  const [selectedMetrics, setSelectedMetrics] = useState<ForecastMetricKey[]>([]);
  const [selectedHorizon, setSelectedHorizon] = useState<ForecastHorizonKey>(DEFAULT_FORECAST_HORIZON);

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

  const handleSubmit = useCallback(() => {
    if (selectedMetrics.length > 0) {
      onSubmit(selectedMetrics, selectedHorizon);
    }
  }, [selectedMetrics, selectedHorizon, onSubmit]);

  const isSubmitDisabled = isLoading || selectedMetrics.length === 0;
  const allSelected = selectedMetrics.length === FORECAST_METRIC_OPTIONS.length;

  return (
    <Card
      elevation={0}
      sx={{
        border: 'none',
        borderRadius: `${radius.card}px`,
        boxShadow: shadows.card,
        overflow: 'visible',
      }}
    >
      <CardContent sx={{ p: { xs: 3, md: 4 } }}>

        {/* ── Section: Metric Selector ──────────────────────────────────────── */}
        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 800, mb: 0.5, letterSpacing: '-0.01em' }}>
              Select Metrics
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Choose one or more business metrics to forecast
            </Typography>
          </Box>

          <Stack direction="row" spacing={1}>
            <Tooltip title="Select all metrics">
              <span>
                <Button
                  size="small"
                  variant="text"
                  startIcon={<CheckSquare size={16} />}
                  onClick={handleSelectAll}
                  disabled={isLoading || allSelected}
                  sx={{ fontSize: '0.8125rem', fontWeight: 600, borderRadius: `${radius.button}px` }}
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
                  startIcon={<Square size={16} />}
                  onClick={handleClearAll}
                  disabled={isLoading || selectedMetrics.length === 0}
                  sx={{ fontSize: '0.8125rem', fontWeight: 600, color: 'text.secondary', borderRadius: `${radius.button}px` }}
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
            gap: 1.5,
            p: 2.5,
            bgcolor: (t) => t.palette.mode === 'light' ? '#F8FAFC' : 'rgba(255,255,255,0.02)',
            borderRadius: `${radius.card}px`,
            border: (t) => `1px solid ${t.palette.mode === 'light' ? '#E2E8F0' : 'rgba(255,255,255,0.05)'}`,
            mb: 4,
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
                  fontWeight: 700,
                  fontSize: '0.875rem',
                  py: 2,
                  px: 1,
                  borderRadius: `${radius.chip}px`,
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  opacity: isLoading ? 0.6 : 1,
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  ...(isSelected && {
                    boxShadow: `0 4px 12px ${alpha(theme.palette[metric.color]?.main ?? theme.palette.primary.main, 0.25)}`,
                    transform: 'translateY(-1px)',
                  }),
                  ...(!isSelected && {
                    bgcolor: 'background.paper',
                    borderColor: 'divider',
                    '&:hover': {
                      bgcolor: 'background.paper',
                      borderColor: 'primary.main',
                      color: 'primary.main',
                    }
                  })
                }}
              />
            );
          })}
        </Box>

        {selectedMetrics.length === 0 && (
          <Typography
            variant="caption"
            color="warning.main"
            sx={{ display: 'block', mb: 3, mt: -2, fontWeight: 600 }}
          >
            ⚠ Select at least one metric to enable the forecast.
          </Typography>
        )}

        <Divider sx={{ mb: 4, opacity: 0.6 }} />

        {/* ── Section: Horizon Selector ─────────────────────────────────────── */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ fontWeight: 800, mb: 0.5, letterSpacing: '-0.01em' }}>
            Forecast Horizon
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ display: 'block', mb: 3 }}>
            Select the time window for the prediction
          </Typography>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: 2,
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
                    p: 3,
                    borderRadius: `${radius.card}px`,
                    border: (t) =>
                      `2px solid ${isSelected ? t.palette.primary.main : (t.palette.mode === 'light' ? '#E2E8F0' : 'rgba(255,255,255,0.05)')}`,
                    bgcolor: isSelected
                      ? (t) => alpha(t.palette.primary.main, 0.04)
                      : 'background.paper',
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    opacity: isLoading ? 0.6 : 1,
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    textAlign: 'center',
                    userSelect: 'none',
                    ...(isSelected && {
                      boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.12)}`,
                      transform: 'translateY(-2px)',
                    }),
                    ...(!isSelected && {
                      '&:hover': {
                        borderColor: isLoading ? undefined : alpha(theme.palette.primary.main, 0.5),
                        bgcolor: isLoading ? undefined : '#F8FAFC',
                      },
                    })
                  }}
                >
                  <Box
                    sx={{
                      color: isSelected ? 'primary.main' : 'text.disabled',
                      mb: 1.5,
                      display: 'flex',
                      justifyContent: 'center',
                      transition: 'color 0.2s ease',
                    }}
                  >
                    {HORIZON_ICONS[horizon.key]}
                  </Box>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 800,
                      color: isSelected ? 'primary.main' : 'text.primary',
                      lineHeight: 1.1,
                      mb: 0.5,
                      letterSpacing: '-0.02em',
                    }}
                  >
                    {horizon.days}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 700,
                      color: isSelected ? 'primary.main' : 'text.secondary',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    {isSelected ? horizon.label : `days`}
                  </Typography>
                </Box>
              );
            })}
          </Box>
        </Box>

        <Divider sx={{ mb: 4, opacity: 0.6 }} />

        {/* ── Submit ────────────────────────────────────────────────────────── */}
        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            {selectedMetrics.length > 0
              ? `${selectedMetrics.length} metric${selectedMetrics.length > 1 ? 's' : ''} selected`
              : 'No metrics selected'}
          </Typography>

          <Button
            id="run-forecast-button"
            variant="contained"
            size="large"
            startIcon={isLoading ? undefined : <Play size={18} fill="currentColor" />}
            onClick={handleSubmit}
            disabled={isSubmitDisabled}
            sx={{
              px: 4,
              py: 1.5,
              fontWeight: 800,
              fontSize: '0.9375rem',
              borderRadius: `${radius.button}px`,
              minWidth: 180,
              background: isSubmitDisabled
                ? undefined
                : (t) => `linear-gradient(135deg, ${t.palette.primary.main}, ${t.palette.secondary.main})`,
              boxShadow: isSubmitDisabled
                ? undefined
                : '0 8px 20px rgba(249, 115, 22, 0.25)',
              '&:hover': {
                boxShadow: '0 12px 24px rgba(249, 115, 22, 0.35)',
                transform: 'translateY(-1px)',
              },
              transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
          >
            {isLoading ? (
              <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
                <LineChart size={18} style={{ animation: 'pulse 1.5s ease-in-out infinite' }} />
                <span>Forecasting…</span>
              </Stack>
            ) : (
              'Run Forecast'
            )}
          </Button>
        </Stack>

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
