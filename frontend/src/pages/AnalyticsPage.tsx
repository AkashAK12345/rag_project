// src/pages/AnalyticsPage.tsx
import { useState } from 'react';
import { Box, Button, Grid, Stack, CircularProgress } from '@mui/material';
import {
  BarChart3,
  Sparkles,
  RefreshCw,
  BarChart,
  TrendingUp,
  CircleDollarSign,
  LineChart,
  Package,
  BrainCircuit,
} from 'lucide-react';
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
import { radius } from '@/theme/radius';

export function AnalyticsPage() {
  const [enabled, setEnabled] = useState(false);
  const refreshAnalytics = useRefreshAnalytics();

  const kpi             = useKpiSummary(enabled);
  const revenue         = useRevenueTrend(enabled);
  const cost            = useCostAnalysis(enabled);
  const forecastRevenue = useForecastRevenue(enabled);
  const forecastInv     = useForecastInventory(enabled);
  const risks           = useRisksAndOpportunities(enabled);

  const allQueries = [kpi, revenue, cost, forecastRevenue, forecastInv, risks];
  const isAnyLoading = allQueries.some((q) => q.isLoading);
  const hasAnyData = allQueries.some((q) => q.data !== undefined);
  const showSections = enabled || hasAnyData;

  const handleGenerate = () => setEnabled(true);
  const handleRefresh = () => {
    setEnabled(true);
    refreshAnalytics();
  };

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
                isAnyLoading ? <CircularProgress size={14} color="inherit" /> : <RefreshCw size={16} />
              }
              onClick={handleRefresh}
              disabled={isAnyLoading}
              sx={{ borderRadius: `${radius.button}px`, px: 2, py: 1, fontWeight: 700 }}
            >
              Refresh Insights
            </Button>
          ) : undefined
        }
      />

      {!showSections && (
        <Box sx={{ mt: 4 }}>
          <EmptyState
            icon={<BarChart3 size={32} />}
            title="No Insights Generated"
            description="Click Generate Insights to run the analytics, forecasting, and reasoning engines against your indexed business data."
            action={
              <Button
                variant="contained"
                size="large"
                startIcon={<Sparkles size={18} />}
                onClick={handleGenerate}
                sx={{ mt: 2, px: 4, py: 1.5, borderRadius: `${radius.button}px`, fontWeight: 700 }}
              >
                Generate Insights
              </Button>
            }
          />
        </Box>
      )}

      {showSections && (
        <Stack spacing={4}>
          <AnswerCard
            title="KPI Summary"
            icon={<BarChart size={20} />}
            data={kpi.data}
            isLoading={kpi.isLoading}
            isError={kpi.isError}
            onRetry={kpi.refetch}
            accentColor="primary"
          />

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <AnswerCard
                title="Revenue Trend"
                icon={<TrendingUp size={20} />}
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
                icon={<CircleDollarSign size={20} />}
                data={cost.data}
                isLoading={cost.isLoading}
                isError={cost.isError}
                onRetry={cost.refetch}
                accentColor="warning"
              />
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <AnswerCard
                title="Revenue Forecast"
                icon={<LineChart size={20} />}
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
                icon={<Package size={20} />}
                data={forecastInv.data}
                isLoading={forecastInv.isLoading}
                isError={forecastInv.isError}
                onRetry={forecastInv.refetch}
                accentColor="secondary"
              />
            </Grid>
          </Grid>

          <AnswerCard
            title="Risks & Opportunities"
            icon={<BrainCircuit size={20} />}
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
