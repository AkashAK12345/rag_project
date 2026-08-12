import { Box, Grid, Alert } from '@mui/material';
import { CircleDollarSign, Package, Info } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingOverlay } from '@/components/common/LoadingOverlay';
import { ErrorState } from '@/components/common/ErrorState';
import { KPICard } from '@/components/dashboard/KPICard';
import { ChartCard } from '@/components/dashboard/ChartCard';
import { InsightCard } from '@/components/dashboard/InsightCard';
import { RevenueTrendChart } from '@/components/dashboard/charts/RevenueTrendChart';
import { HorizontalBarChart } from '@/components/dashboard/charts/HorizontalBarChart';
import { DonutChart } from '@/components/dashboard/charts/DonutChart';
import { useAnalyticsDashboard } from '@/hooks/useDashboard';

export function AnalyticsPage() {
  const { data, isLoading, isError, refetch } = useAnalyticsDashboard();

  if (isLoading) {
    return (
      <Box sx={{ p: 4 }}>
        <PageHeader title="Business Analytics" subtitle="Comprehensive performance metrics" />
        <LoadingOverlay message="Loading deterministic analytics..." />
      </Box>
    );
  }

  if (isError || !data) {
    return (
      <Box sx={{ p: 4 }}>
        <PageHeader title="Business Analytics" subtitle="Comprehensive performance metrics" />
        <ErrorState message="Failed to load analytics dashboard" onRetry={() => refetch()} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1400, mx: 'auto' }}>
      <PageHeader title="Business Analytics" subtitle="Comprehensive performance metrics" />
      
      {data.isDemoData && (
        <Alert severity="info" sx={{ mb: 4 }} icon={<Info size={24} />}>
          Showing demonstration data because no business reports have been indexed yet.
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard 
            title="Total Revenue" 
            value={data.overview.total_revenue.value / 1000} 
            prefix="$"
            suffix="k"
            decimals={1}
            icon={<CircleDollarSign />} 
            trend={{ value: `${data.overview.revenue_growth_pct.value}%`, isPositive: data.overview.revenue_growth_pct.value >= 0, label: 'vs last month' }}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard 
            title="Total Orders" 
            value={data.overview.total_orders.value} 
            icon={<Package />} 
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard 
            title="Avg Order Value" 
            value={data.overview.avg_order_value.value} 
            prefix="$"
            decimals={2}
            icon={<CircleDollarSign />} 
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <InsightCard 
            summary={data.insights.summary}
            timestamp={data.insights.generatedAt}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, lg: 8 }}>
          <ChartCard title="Revenue & Profit Trend" subtitle="Monthly performance across all branches">
            <RevenueTrendChart data={data.charts.revenueTrend.data} />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <ChartCard title="Top Products" subtitle="By total revenue">
            <HorizontalBarChart data={data.charts.topProducts.data} dataKey="revenue" nameKey="product" />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <ChartCard title="Sales by Category" subtitle="Revenue distribution">
            <DonutChart data={data.charts.salesByCategory.data} dataKey="sales" nameKey="category" />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 8 }}>
          <ChartCard title="Branch Performance" subtitle="Revenue by outlet">
            <HorizontalBarChart data={data.charts.branchPerformance.data} dataKey="revenue" nameKey="branch" />
          </ChartCard>
        </Grid>
      </Grid>
    </Box>
  );
}
