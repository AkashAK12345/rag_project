import pandas as pd
from core.logging import get_logger
from sources.base_source import BaseSource

logger = get_logger(__name__)


class ExcelSource(BaseSource):
    """
    Reads all sheets from an Excel file (.xlsx / .xls) into DataFrames.
    No business logic — pure I/O.
    """

    SUPPORTED_EXTENSIONS = (".xlsx", ".xls")

    def load(self, path: str) -> dict[str, pd.DataFrame]:
        logger.info(f"ExcelSource: loading '{path}'")
        result: dict[str, pd.DataFrame] = {}

        # read_excel returns {sheet_name: DataFrame} when sheet_name=None
        raw: dict[str, pd.DataFrame] = pd.read_excel(path, sheet_name=None)

        for sheet_name, df in raw.items():
            df = df.dropna(how="all")
            if df.empty:
                logger.info(f"ExcelSource: skipping empty sheet '{sheet_name}' in '{path}'")
                continue
            result[sheet_name] = df.reset_index(drop=True)
            logger.info(f"ExcelSource: loaded sheet '{sheet_name}' ({len(df)} rows)")

        logger.info(f"ExcelSource: finished — {len(result)} non-empty sheet(s) from '{path}'")
        return result
