from datetime import datetime, timezone
from schemas.dashboard import (
    AnalyticsDashboardResponse,
    AnalyticsDashboardOverview,
    AnalyticsDashboardCharts,
    AnalyticsDashboardInsights,
    ChartSeries,
    RevenueTrendPoint,
    TopProductPoint,
    SalesCategoryPoint,
    BranchPerformancePoint,
    InventoryStatusPoint,
)

def get_analytics_demo_data(reason: str = "No business reports indexed") -> AnalyticsDashboardResponse:
    overview = AnalyticsDashboardOverview(
        total_revenue=345000.0,
        active_branches=3,
        total_orders=11800,
        avg_order_value=29.23,
        revenue_growth_pct=4.2
    )
    
    trend_data = [
        RevenueTrendPoint(date="Jan", revenue=45000),
        RevenueTrendPoint(date="Feb", revenue=52000),
        RevenueTrendPoint(date="Mar", revenue=48000),
        RevenueTrendPoint(date="Apr", revenue=61000),
        RevenueTrendPoint(date="May", revenue=59000),
        RevenueTrendPoint(date="Jun", revenue=75000),
    ]
    
    branch_data = [
        BranchPerformancePoint(branch="Downtown", revenue=120000, orders=4800, satisfaction_score=4.8),
        BranchPerformancePoint(branch="Westside", revenue=95000, orders=3900, satisfaction_score=4.6),
        BranchPerformancePoint(branch="North Hills", revenue=82000, orders=3100, satisfaction_score=4.2),
    ]
    
    top_products = [
        TopProductPoint(product="Signature Burger", revenue=45000, units_sold=3200),
        TopProductPoint(product="Truffle Fries", revenue=28000, units_sold=4100),
        TopProductPoint(product="Craft IPA", revenue=22000, units_sold=2800),
        TopProductPoint(product="Avocado Salad", revenue=18500, units_sold=1500),
    ]
    
    sales_cat = [
        SalesCategoryPoint(category="Mains", sales=65000),
        SalesCategoryPoint(category="Beverages", sales=32000),
        SalesCategoryPoint(category="Sides", sales=28000),
        SalesCategoryPoint(category="Desserts", sales=15000),
    ]
    
    inventory_data = [
        InventoryStatusPoint(item="Ground Beef", current_stock=45, reorder_level=50, status="Low Stock"),
        InventoryStatusPoint(item="Burger Buns", current_stock=200, reorder_level=100, status="Healthy"),
        InventoryStatusPoint(item="Cheddar Cheese", current_stock=30, reorder_level=20, status="Healthy"),
        InventoryStatusPoint(item="Tomatoes", current_stock=15, reorder_level=25, status="Low Stock"),
        InventoryStatusPoint(item="Lettuce", current_stock=8, reorder_level=15, status="Critical"),
    ]

    charts = AnalyticsDashboardCharts(
        revenueTrend=ChartSeries(series_name="revenue_trend", data=trend_data),
        topProducts=ChartSeries(series_name="top_products", data=top_products),
        salesByCategory=ChartSeries(series_name="sales_by_category", data=sales_cat),
        branchPerformance=ChartSeries(series_name="branch_performance", data=branch_data),
        inventoryStatus=ChartSeries(series_name="inventory_status", data=inventory_data)
    )

    insights = AnalyticsDashboardInsights(
        summary="This is a demonstration dashboard using sample data. Please upload your business reports to view real analytics.",
        generatedAt=datetime.now(timezone.utc)
    )

    return AnalyticsDashboardResponse(
        isDemoData=True,
        demoReason=reason,
        overview=overview,
        charts=charts,
        insights=insights
    )
