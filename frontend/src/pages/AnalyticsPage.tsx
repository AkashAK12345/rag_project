// src/pages/AnalyticsPage.tsx
import { useState } from 'react';
import { Box, Button, Grid, Stack, CircularProgress } from '@mui/material';
import {
  Analytics,
  AutoAwesome,
  Refresh,
  Assessment,
  TrendingUp,
  PriceChange,
  ShowChart,
  Inventory2,
  Psychology,
} from '@mui/icons-material';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';
import { AnswerCard } from '@/components/analytics/AnswerCard';
import {
  useKpiSummary,
  useRevenueTrend,
  useCostAnalysis,
  useForecastRevenue,
  useForecastInventory,
  useRisksAndOpportunities,
  useRefreshAnalytics,
} from '@/hooks/useAnalytics';

/**
 * AnalyticsPage — Phase 3 implementation.
 *
 * Workflow:
 *   1. Page loads instantly with an EmptyState + "Generate Insights" CTA.
 *   2. On click, `enabled` flips to true, firing all 6 RAG queries in parallel.
 *   3. Each section card transitions from skeleton → answer independently.
 *   4. "Refresh Insights" invalidates all cached analytics queries and re-fetches.
 *   5. On return visits within staleTime (5 min), cached data is shown without
 *      re-fetching — the Generate button is not shown again until cache expires.
 *
 * Design decisions:
 *   - No auto-fire on page load (avoids unnecessary LLM invocations).
 *   - No answer parsing — backend text is displayed verbatim.
 *   - No charts — information cards only; charts deferred to a future phase.
 *   - Section layout is inline (no separate section component files) per the
 *     "no unnecessary abstractions" requirement.
 */
export function AnalyticsPage() {
  // When false, all queries are disabled. Flips to true on Generate or Refresh.
  const [enabled, setEnabled] = useState(false);
  const refreshAnalytics = useRefreshAnalytics();

  // ── Query hooks — all disabled until user triggers generation ───────────────
  const kpi             = useKpiSummary(enabled);
  const revenue         = useRevenueTrend(enabled);
  const cost            = useCostAnalysis(enabled);
  const forecastRevenue = useForecastRevenue(enabled);
  const forecastInv     = useForecastInventory(enabled);
  const risks           = useRisksAndOpportunities(enabled);

  const allQueries = [kpi, revenue, cost, forecastRevenue, forecastInv, risks];
  const isAnyLoading = allQueries.some((q) => q.isLoading);

  // Cache data appears even when enabled=false (TanStack Query reads from cache
  // regardless of the enabled flag). So `hasAnyData` is true on return visits.
  const hasAnyData = allQueries.some((q) => q.data !== undefined);
  const showSections = enabled || hasAnyData;

  // ── Event handlers ──────────────────────────────────────────────────────────

  const handleGenerate = () => setEnabled(true);

  const handleRefresh = () => {
    // Ensure queries are enabled before invalidating, so the re-fetch actually fires.
    setEnabled(true);
    refreshAnalytics();
  };

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <Box>
      <PageHeader
        title="Analytics"
        subtitle="AI-powered business insights generated from your indexed reports."
        action={
          showSections ? (
            <Button
              variant="outlined"
              startIcon={
                isAnyLoading ? <CircularProgress size={16} color="inherit" /> : <Refresh />
              }
              onClick={handleRefresh}
              disabled={isAnyLoading}
            >
              Refresh Insights
            </Button>
          ) : undefined
        }
      />

      {/* ── Empty / Generate state ─────────────────────────────────────────── */}
      {!showSections && (
        <EmptyState
          icon={<Analytics />}
          title="No Insights Generated"
          description="Click Generate Insights to run the analytics, forecasting, and reasoning engines against your indexed business data."
          action={
            <Stack direction="row" sx={{ justifyContent: 'center', mt: 1 }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<AutoAwesome />}
                onClick={handleGenerate}
              >
                Generate Insights
              </Button>
            </Stack>
          }
        />
      )}

      {/* ── Sections (rendered once generation has been triggered) ──────────── */}
      {showSections && (
        <Stack spacing={4}>

          {/* ── KPI Summary — full width ─────────────────────────────────── */}
          <AnswerCard
            title="KPI Summary"
            icon={<Assessment />}
            data={kpi.data}
            isLoading={kpi.isLoading}
            isError={kpi.isError}
            onRetry={kpi.refetch}
            accentColor="primary"
          />

          {/* ── Revenue Trend + Cost Analysis — side by side ─────────────── */}
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <AnswerCard
                title="Revenue Trend"
                icon={<TrendingUp />}
                data={revenue.data}
                isLoading={revenue.isLoading}
                isError={revenue.isError}
                onRetry={revenue.refetch}
                accentColor="success"
              />
            </Grid>
            <Grid size={{ xs: 12, lg: 6 }}>
              <AnswerCard
                title="Cost Analysis"
                icon={<PriceChange />}
                data={cost.data}
                isLoading={cost.isLoading}
                isError={cost.isError}
                onRetry={cost.refetch}
                accentColor="warning"
              />
            </Grid>
          </Grid>

          {/* ── Revenue Forecast + Inventory Forecast — side by side ─────── */}
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <AnswerCard
                title="Revenue Forecast"
                icon={<ShowChart />}
                data={forecastRevenue.data}
                isLoading={forecastRevenue.isLoading}
                isError={forecastRevenue.isError}
                onRetry={forecastRevenue.refetch}
                accentColor="secondary"
              />
            </Grid>
            <Grid size={{ xs: 12, lg: 6 }}>
              <AnswerCard
                title="Inventory Forecast"
                icon={<Inventory2 />}
                data={forecastInv.data}
                isLoading={forecastInv.isLoading}
                isError={forecastInv.isError}
                onRetry={forecastInv.refetch}
                accentColor="secondary"
              />
            </Grid>
          </Grid>

          {/* ── Risks & Opportunities — full width ───────────────────────── */}
          <AnswerCard
            title="Risks & Opportunities"
            icon={<Psychology />}
            data={risks.data}
            isLoading={risks.isLoading}
            isError={risks.isError}
            onRetry={risks.refetch}
            accentColor="error"
          />

        </Stack>
      )}
    </Box>
  );
}

