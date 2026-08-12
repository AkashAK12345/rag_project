from schemas.dashboard import (
    ForecastDashboardResponse,
    ForecastDashboardOverview,
    ForecastDashboardCharts,
    ForecastDashboardInsights,
    ChartSeries,
    ForecastPoint,
)

def get_forecast_demo_data(reason: str = "No business reports indexed") -> ForecastDashboardResponse:
    overview = ForecastDashboardOverview(
        projected_revenue_30d=66000.0,
        expected_demand_growth_pct=5.2,
        inventory_risk_items=12
    )

    revenue_timeline = [
        ForecastPoint(date="Mar", actual=55000),
        ForecastPoint(date="Apr", actual=58000),
        ForecastPoint(date="May", actual=62000),
        ForecastPoint(date="Jun", actual=60000, forecast=60000),
        ForecastPoint(date="Jul", forecast=63000, lower_bound=57000, upper_bound=69000),
        ForecastPoint(date="Aug", forecast=66000, lower_bound=59000, upper_bound=73000),
    ]

    demand_timeline = [
        ForecastPoint(date="Mar", actual=1200),
        ForecastPoint(date="Apr", actual=1350),
        ForecastPoint(date="May", actual=1420),
        ForecastPoint(date="Jun", actual=1500, forecast=1500),
        ForecastPoint(date="Jul", forecast=1580, lower_bound=1420, upper_bound=1740),
        ForecastPoint(date="Aug", forecast=1650, lower_bound=1490, upper_bound=1810),
    ]

    inventory_timeline = [
        ForecastPoint(date="Mar", actual=500),
        ForecastPoint(date="Apr", actual=450),
        ForecastPoint(date="May", actual=480),
        ForecastPoint(date="Jun", actual=420, forecast=420),
        ForecastPoint(date="Jul", forecast=440, lower_bound=390, upper_bound=490),
        ForecastPoint(date="Aug", forecast=460, lower_bound=410, upper_bound=510),
    ]

    charts = ForecastDashboardCharts(
        revenueForecast=ChartSeries(series_name="revenue_forecast", data=revenue_timeline),
        demandForecast=ChartSeries(series_name="demand_forecast", data=demand_timeline),
        inventoryForecast=ChartSeries(series_name="inventory_forecast", data=inventory_timeline)
    )

    insights = ForecastDashboardInsights(
        summary="This is a demonstration forecast using sample data. Please upload your business reports to generate real predictions.",
        confidence=1.0
    )

    return ForecastDashboardResponse(
        isDemoData=True,
        demoReason=reason,
        overview=overview,
        charts=charts,
        insights=insights
    )
