import pandas as pd
from typing import Type, Any

from core.logging import get_logger
from reports.base_report import BaseReport, MIN_DETECTION_CONFIDENCE
from reports.generic_report import GenericReport

# Register all domain parsers here
from reports.purchases.purchase_report import PurchaseReport
from reports.sales.sales_report import SalesReport
from reports.sales.outlet_sales_report import OutletSalesReport
from reports.inventory.inventory_report import InventoryReport
from reports.inventory.expiry_report import ExpiryReport
from reports.inventory.stock_report import StockReport
from reports.finance.financial_report import FinancialReport
from reports.employees.attendance_report import AttendanceReport
from reports.employees.employee_report import EmployeeReport
from reports.production.production_report import ProductionReport
from reports.wastage.wastage_report import WastageReport

logger = get_logger(__name__)

# Order doesn't strictly matter because we take the max score, 
# but it's good practice to list them logically.
REGISTERED_PARSERS: list[Type[BaseReport]] = [
    OutletSalesReport,
    SalesReport,
    PurchaseReport,
    ExpiryReport,
    StockReport,
    InventoryReport,
    FinancialReport,
    AttendanceReport,
    EmployeeReport,
    ProductionReport,
    WastageReport,
]


class ReportFactory:
    """
    Evaluates incoming raw DataFrames against all registered parsers.
    Selects the parser with the highest detection score above MIN_DETECTION_CONFIDENCE,
    falling back to GenericReport if none match.
    """

    @classmethod
    def evaluate_workbook(cls, df_map: dict[str, pd.DataFrame], workbook_name: str = "Unknown") -> Any:
        from schemas.report import WorkbookCapabilityGraph, SheetCapability, MetricCapability, ChartCapability
        
        logger.info(f"ReportFactory: evaluating capabilities for workbook '{workbook_name}'...")
        
        sheets_cap: list[SheetCapability] = []
        all_metrics: list[MetricCapability] = []
        all_charts: list[ChartCapability] = []
        all_domains: set = set()
        
        for sheet_name, df in df_map.items():
            rankings = []
            accepted_parsers = []
            sheet_metrics: list[MetricCapability] = []
            sheet_charts: list[ChartCapability] = []
            sheet_domains = []
            
            for parser_cls in REGISTERED_PARSERS:
                try:
                    diag = parser_cls.evaluate_sheet_confidence(sheet_name, df)
                    rankings.append(diag)
                    
                    if diag.accepted or diag.score >= MIN_DETECTION_CONFIDENCE:
                        accepted_parsers.append(parser_cls.__name__)
                        
                        # Build metric lineages
                        for metric_name in parser_cls.COVERAGE.get("metrics", []):
                            metric_cap = MetricCapability(
                                name=metric_name,
                                business_domain=parser_cls.BUSINESS_DOMAIN,
                                source_sheet=sheet_name,
                                source_parser=parser_cls.__name__,
                                required_fields=parser_cls.REQUIRED_FIELDS,
                                optional_fields=parser_cls.OPTIONAL_FIELDS,
                                confidence=diag.score
                            )
                            sheet_metrics.append(metric_cap)
                            
                        # Build chart lineages
                        for chart_name in parser_cls.COVERAGE.get("charts", []):
                            chart_cap = ChartCapability(
                                name=chart_name,
                                business_domain=parser_cls.BUSINESS_DOMAIN,
                                source_sheet=sheet_name,
                                source_parser=parser_cls.__name__,
                                required_fields=parser_cls.REQUIRED_FIELDS,
                                optional_fields=parser_cls.OPTIONAL_FIELDS,
                                confidence=diag.score
                            )
                            sheet_charts.append(chart_cap)
                            
                        sheet_domains.append(parser_cls.BUSINESS_DOMAIN)
                except Exception as e:
                    logger.warning(f"Error evaluating sheet '{sheet_name}' with {parser_cls.__name__}: {e}")
                    
            # Sort rankings by score descending
            rankings.sort(key=lambda x: x.score, reverse=True)
            
            # Deduplicate domains for this sheet
            sheet_domains = list(set(sheet_domains))
            
            # Update workbook totals
            all_metrics.extend(sheet_metrics)
            all_charts.extend(sheet_charts)
            all_domains.update(sheet_domains)
            
            sheets_cap.append(SheetCapability(
                sheet_name=sheet_name,
                accepted_parsers=accepted_parsers,
                candidate_rankings=rankings,
                supported_metrics=sheet_metrics,
                supported_charts=sheet_charts,
                supported_domains=sheet_domains
            ))
            
        return WorkbookCapabilityGraph(
            workbook_name=workbook_name,
            sheets=sheets_cap,
            supported_metrics=all_metrics,
            supported_charts=all_charts,
            supported_domains=all_domains
        )

    @classmethod
    def get_parser_class(cls, df_map: dict[str, pd.DataFrame]) -> Type[BaseReport]:
        """Legacy wrapper to maintain compatibility with IngestionService."""
        graph = cls.evaluate_workbook(df_map)
        
        best_parser_name = None
        best_score = 0.0
        
        for sheet in graph.sheets:
            if sheet.candidate_rankings:
                top_diag = sheet.candidate_rankings[0]
                if top_diag.score > best_score:
                    best_score = top_diag.score
                    best_parser_name = top_diag.parser_name
                    
        if best_parser_name and best_score >= MIN_DETECTION_CONFIDENCE:
            logger.info(f"ReportFactory: legacy fallback selected '{best_parser_name}' (score: {best_score:.2f})")
            for p in REGISTERED_PARSERS:
                if p.__name__ == best_parser_name:
                    return p
                    
        logger.info(f"ReportFactory: no parser met threshold ({MIN_DETECTION_CONFIDENCE}). Falling back to GenericReport.")
        return GenericReport
