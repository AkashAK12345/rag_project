import { useState } from 'react';
import { Box, Grid, MenuItem, Select, Alert } from '@mui/material';
import { TrendingUp, Package, Activity, Info } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingOverlay } from '@/components/common/LoadingOverlay';
import { ErrorState } from '@/components/common/ErrorState';
import { KPICard } from '@/components/dashboard/KPICard';
import { ChartCard } from '@/components/dashboard/ChartCard';
import { InsightCard } from '@/components/dashboard/InsightCard';
import { ForecastLineChart } from '@/components/dashboard/charts/ForecastLineChart';
import { useForecastDashboard } from '@/hooks/useDashboard';

export function ForecastingPage() {
  const [horizon, setHorizon] = useState('next_month');
  const { data, isLoading, isError, error, refetch } = useForecastDashboard(horizon);

  const horizonSelector = (
    <Select
      size="small"
      value={horizon}
      onChange={(e) => setHorizon(e.target.value)}
      sx={{ minWidth: 150 }}
    >
      <MenuItem value="next_week">Next 7 Days</MenuItem>
      <MenuItem value="next_month">Next 30 Days</MenuItem>
      <MenuItem value="next_quarter">Next 90 Days</MenuItem>
    </Select>
  );

  if (isLoading) {
    return (
      <Box sx={{ p: 4 }}>
        <PageHeader title="Demand Forecasting" subtitle="Predictive business modeling" action={horizonSelector} />
        <LoadingOverlay message="Running forecast models..." />
      </Box>
    );
  }

  if (isError || !data) {
    const errorMessage = (error as any)?.response?.data?.detail?.message || "Failed to load forecast dashboard";
    return (
      <Box sx={{ p: 4 }}>
        <PageHeader title="Demand Forecasting" subtitle="Predictive business modeling" action={horizonSelector} />
        <ErrorState message={errorMessage} onRetry={() => refetch()} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1400, mx: 'auto' }}>
      <PageHeader title="Demand Forecasting" subtitle="Predictive business modeling" action={horizonSelector} />
      
      {data.isDemoData && (
        <Alert severity="info" sx={{ mb: 4 }} icon={<Info size={24} />}>
          Showing demonstration data because no business reports have been indexed yet.
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard 
            title="Projected Revenue" 
            value={data.overview.projected_revenue_30d / 1000} 
            prefix="$"
            suffix="k"
            decimals={1}
            icon={<TrendingUp />} 
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard 
            title="Expected Demand Growth" 
            value={data.overview.expected_demand_growth_pct} 
            suffix="%"
            decimals={1}
            icon={<Activity />} 
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard 
            title="Inventory Risk Items" 
            value={data.overview.inventory_risk_items} 
            icon={<Package />} 
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <InsightCard 
            summary={data.insights.summary}
            confidence={data.insights.confidence}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12 }}>
          <ChartCard title="Revenue Forecast" subtitle={`Projected timeline for ${horizon.replace('_', ' ')}`}>
            <ForecastLineChart data={data.charts.revenueForecast.data} />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 6 }}>
          <ChartCard title="Demand Forecast" subtitle="Expected order volume">
            <ForecastLineChart data={data.charts.demandForecast.data} />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 6 }}>
          <ChartCard title="Inventory Projection" subtitle="Predicted stock levels">
            <ForecastLineChart data={data.charts.inventoryForecast.data} />
          </ChartCard>
        </Grid>
      </Grid>
    </Box>
  );
}
