"""
schemas/dashboard.py

Strongly typed DTOs and models for the Analytics and Forecast dashboards.
Includes chart-specific data models to prevent overloading BusinessMetric.
"""

from typing import List, Optional, Any, TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel

# ------------------------------------------------------------------
# Chart Models
# ------------------------------------------------------------------

class ChartPoint(BaseModel):
    """Generic base class for a chart data point."""
    label: str
    value: float

class ChartCategory(BaseModel):
    """Generic category item."""
    category: str
    value: float

class RevenueTrendPoint(BaseModel):
    date: str
    revenue: float
    profit: Optional[float] = None

class SalesCategoryPoint(BaseModel):
    category: str
    sales: float

class BranchPerformancePoint(BaseModel):
    branch: str
    revenue: float
    orders: int
    satisfaction_score: float

class TopProductPoint(BaseModel):
    product: str
    revenue: float
    units_sold: int

class ForecastPoint(BaseModel):
    date: str
    actual: Optional[float] = None
    forecast: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class InventoryStatusPoint(BaseModel):
    item: str
    current_stock: int
    reorder_level: int
    status: str

T = TypeVar('T')

class CapabilityStatus(BaseModel):
    status: str  # 'supported', 'unsupported', 'empty'
    reason: Optional[str] = None
    required_fields: Optional[List[str]] = None


class ChartSeries(BaseModel, Generic[T]):
    """Represents a structured chart dataset."""
    series_name: str
    data: List[T]
    capability: Optional[CapabilityStatus] = None

# ------------------------------------------------------------------
# Analytics Dashboard DTOs
# ------------------------------------------------------------------

class KpiValue(BaseModel, Generic[T]):
    value: T
    capability: Optional[CapabilityStatus] = None

class AnalyticsDashboardOverview(BaseModel):
    total_revenue: KpiValue[float]
    active_branches: KpiValue[int]
    total_orders: KpiValue[int]
    avg_order_value: KpiValue[float]
    revenue_growth_pct: KpiValue[float]

class AnalyticsDashboardCharts(BaseModel):
    revenueTrend: ChartSeries[RevenueTrendPoint]
    topProducts: ChartSeries[TopProductPoint]
    salesByCategory: ChartSeries[SalesCategoryPoint]
    branchPerformance: ChartSeries[BranchPerformancePoint]
    inventoryStatus: ChartSeries[InventoryStatusPoint]

class AnalyticsDashboardInsights(BaseModel):
    summary: str
    generatedAt: datetime

class AnalyticsDashboardResponse(BaseModel):
    isDemoData: bool = False
    demoReason: Optional[str] = None
    overview: AnalyticsDashboardOverview
    charts: AnalyticsDashboardCharts
    insights: AnalyticsDashboardInsights

# ------------------------------------------------------------------
# Forecast Dashboard DTOs
# ------------------------------------------------------------------

class ForecastDashboardOverview(BaseModel):
    projected_revenue_30d: float
    expected_demand_growth_pct: float
    inventory_risk_items: int

class ForecastDashboardCharts(BaseModel):
    revenueForecast: ChartSeries[ForecastPoint]
    demandForecast: ChartSeries[ForecastPoint]
    inventoryForecast: ChartSeries[ForecastPoint]

class ForecastDashboardInsights(BaseModel):
    summary: str
    confidence: float

class ForecastDashboardResponse(BaseModel):
    isDemoData: bool = False
    demoReason: Optional[str] = None
    overview: ForecastDashboardOverview
    charts: ForecastDashboardCharts
    insights: ForecastDashboardInsights
