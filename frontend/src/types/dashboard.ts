export interface ChartPoint {
  label: string;
  value: number;
}

export interface RevenueTrendPoint {
  date: string;
  revenue: number;
  profit?: number;
}

export interface SalesCategoryPoint {
  category: string;
  sales: number;
}

export interface BranchPerformancePoint {
  branch: string;
  revenue: number;
  orders: number;
  satisfaction_score: number;
}

export interface TopProductPoint {
  product: string;
  revenue: number;
  units_sold: number;
}

export interface ForecastPoint {
  date: string;
  actual?: number;
  forecast?: number;
  lower_bound?: number;
  upper_bound?: number;
}

export interface InventoryStatusPoint {
  item: string;
  current_stock: number;
  reorder_level: number;
  status: string;
}

export interface CapabilityStatus {
  status: string; // 'supported', 'unsupported', 'empty'
  reason?: string;
  required_fields?: string[];
}

export interface ChartSeries<T> {
  series_name: string;
  data: T[];
  capability?: CapabilityStatus;
}

export interface KpiValue<T> {
  value: T;
  capability?: CapabilityStatus;
}

export interface AnalyticsDashboardOverview {
  total_revenue: KpiValue<number>;
  active_branches: KpiValue<number>;
  total_orders: KpiValue<number>;
  avg_order_value: KpiValue<number>;
  revenue_growth_pct: KpiValue<number>;
}

export interface AnalyticsDashboardCharts {
  revenueTrend: ChartSeries<RevenueTrendPoint>;
  topProducts: ChartSeries<TopProductPoint>;
  salesByCategory: ChartSeries<SalesCategoryPoint>;
  branchPerformance: ChartSeries<BranchPerformancePoint>;
  inventoryStatus: ChartSeries<InventoryStatusPoint>;
}

export interface AnalyticsDashboardInsights {
  summary: string;
  generatedAt: string;
}

export interface AnalyticsDashboardResponse {
  isDemoData?: boolean;
  demoReason?: string;
  overview: AnalyticsDashboardOverview;
  charts: AnalyticsDashboardCharts;
  insights: AnalyticsDashboardInsights;
}

export interface ForecastDashboardOverview {
  projected_revenue_30d: number;
  expected_demand_growth_pct: number;
  inventory_risk_items: number;
}

export interface ForecastDashboardCharts {
  revenueForecast: ChartSeries<ForecastPoint>;
  demandForecast: ChartSeries<ForecastPoint>;
  inventoryForecast: ChartSeries<ForecastPoint>;
}

export interface ForecastDashboardInsights {
  summary: string;
  confidence: number;
}

export interface ForecastDashboardResponse {
  isDemoData?: boolean;
  demoReason?: string;
  overview: ForecastDashboardOverview;
  charts: ForecastDashboardCharts;
  insights: ForecastDashboardInsights;
}
