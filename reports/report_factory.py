import pandas as pd
from typing import Type

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
    def get_parser_class(cls, df_map: dict[str, pd.DataFrame]) -> Type[BaseReport]:
        best_score = 0.0
        best_parser: Type[BaseReport] | None = None

        logger.info("ReportFactory: starting confidence voting...")

        for parser_cls in REGISTERED_PARSERS:
            try:
                score = parser_cls.detect(df_map)
                logger.debug(f"  {parser_cls.__name__} scored: {score:.2f}")
                if score > best_score:
                    best_score = score
                    best_parser = parser_cls
            except Exception as e:
                logger.warning(f"Error while running detect() on {parser_cls.__name__}: {e}")

        if best_parser and best_score >= MIN_DETECTION_CONFIDENCE:
            logger.info(f"ReportFactory: selected '{best_parser.__name__}' (score: {best_score:.2f})")
            return best_parser
        else:
            logger.info(f"ReportFactory: no parser met threshold ({MIN_DETECTION_CONFIDENCE}). Falling back to GenericReport.")
            return GenericReport
