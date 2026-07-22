import pandas as pd
from core.logging import get_logger
from sources.base_source import BaseSource

logger = get_logger(__name__)


class CSVSource(BaseSource):
    """
    Reads a single CSV file into a DataFrame.
    Uses the filename stem as the "sheet" name for API consistency.
    No business logic — pure I/O.
    """

    SUPPORTED_EXTENSIONS = (".csv",)

    def load(self, path: str) -> dict[str, pd.DataFrame]:
        import os

        logger.info(f"CSVSource: loading '{path}'")
        stem = os.path.splitext(os.path.basename(path))[0]

        df = pd.read_csv(path)
        df = df.dropna(how="all").reset_index(drop=True)

        if df.empty:
            logger.warning(f"CSVSource: file '{path}' produced an empty DataFrame.")
            return {}

        logger.info(f"CSVSource: loaded {len(df)} rows from '{path}'")
        return {stem: df}
