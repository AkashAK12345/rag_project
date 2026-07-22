"""
services/ingestion_service.py

Orchestrates the new Unified Business Data Ingestion Framework.

Pipeline:
1. Select SourceLoader based on file extension.
2. Load raw data into {sheet: DataFrame}.
3. Pass raw data to ReportFactory.
4. Instantiate the selected BaseReport subclass.
5. validate() -> parse().
6. Pass resulting Documents to IndexingService.
"""

import os
import time

from core.logging import get_logger
from sources.base_source import BaseSource
from sources.csv_source import CSVSource
from sources.excel_source import ExcelSource
from reports.report_factory import ReportFactory
from schemas.report import ReportResult, SourceType
from schemas.connector_result import ConnectorResult
from services.indexing_service import IndexingService

logger = get_logger(__name__)


class IngestionService:
    def __init__(self) -> None:
        self.indexing_service = IndexingService()

    def process_connector_result(self, result: ConnectorResult) -> ReportResult:
        """
        Process a standardized ConnectorResult through the ingestion pipeline.
        
        Args:
            result: The canonical payload containing dataframes from any enterprise source.
            
        Returns:
            ReportResult containing the parsed domain documents and metadata.
        """
        start_time = time.perf_counter()
        logger.info(f"IngestionService: starting ingestion for dataset '{result.dataset_name}'")

        if not result.dataframes:
            raise ValueError(f"Dataset '{result.dataset_name}' contains no readable data.")

        # 1. Detect Report Type
        parser_cls = ReportFactory.get_parser_class(result.dataframes)

        # 2. Instantiate and Validate
        parser = parser_cls(
            df_map=result.dataframes, 
            source_file=result.dataset_name, 
            source_type=result.source_type
        )
        try:
            parser.validate()
        except ValueError as e:
            logger.warning(f"IngestionService: validation failed for '{result.dataset_name}' as {parser_cls.__name__} - {e}")
            raise ValueError(f"Report validation failed: {e}")

        # 3. Parse into Domain Documents
        report_result: ReportResult = parser.parse()
        doc_count = report_result.document_count
        
        # Inject enterprise metadata if present
        report_result.organization_id = result.organization_id
        
        logger.info(
            f"IngestionService: parsing complete. "
            f"Type: {report_result.report_type.value}, "
            f"Domain: {report_result.business_domain.value}, "
            f"Docs: {doc_count}"
        )

        # 4. Push to IndexingService
        if doc_count > 0:
            logger.info(f"IngestionService: handing off {doc_count} documents to IndexingService.")
            self.indexing_service.index_documents(
                documents=report_result.documents,
                source_file=result.dataset_name
            )
        else:
            logger.warning(f"IngestionService: zero documents produced for '{result.dataset_name}'. Skipping index.")

        duration = (time.perf_counter() - start_time) * 1000
        logger.info(f"IngestionService: pipeline finished for '{result.dataset_name}' in {duration:.1f}ms")
        return report_result

    def process_file(self, file_path: str) -> ReportResult:
        """
        Legacy file ingestion pipeline. Wrapper to maintain backward compatibility.
        Converts file loading into a ConnectorResult.
        """
        start_time = time.perf_counter()
        filename = os.path.basename(file_path)
        logger.info(f"IngestionService: parsing file '{filename}' for ConnectorResult conversion")

        ext = os.path.splitext(filename)[1].lower()
        source_loader: BaseSource
        source_type: SourceType

        if ext in ExcelSource.SUPPORTED_EXTENSIONS:
            source_loader = ExcelSource()
            source_type = SourceType.EXCEL
        elif ext in CSVSource.SUPPORTED_EXTENSIONS:
            source_loader = CSVSource()
            source_type = SourceType.CSV
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        df_map = source_loader.load(file_path)
        
        result = ConnectorResult(
            source_type=source_type,
            dataset_name=filename,
            dataframes=df_map
        )
        
        return self.process_connector_result(result)
