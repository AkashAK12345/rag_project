"""
sources/base_source.py

Abstract contract for all data source loaders.

Responsibility: acquire raw tabular data and return it as a dict of
{sheet_name: pd.DataFrame}. Sources have ZERO business knowledge.

This design means a WebsiteSource, SQLSource, or POSSource can be
added in the future without touching any report parser or business logic.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseSource(ABC):
    """
    Contract for every data source loader.

    Implementations must return a dict where:
    - keys   = logical "sheet" names (tab name, table name, endpoint name, etc.)
    - values = raw pd.DataFrame for that partition

    Sources MUST NOT:
    - Interpret or transform business meaning.
    - Create LlamaIndex Documents.
    - Call IndexingService.
    """

    @abstractmethod
    def load(self, path: str) -> dict[str, pd.DataFrame]:
        """
        Load the data from the given path (or URI / connection string).

        Returns:
            A dict mapping sheet/table/partition names to DataFrames.
            Empty frames are allowed but callers should expect and handle them.
        Raises:
            IOError: if the source cannot be read.
            ValueError: if the path is unsupported.
        """
        ...
