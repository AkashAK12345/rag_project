import json
import os
from typing import Dict, Any

from core.logging import get_logger
from loaders.excel_loader import load_single_excel
from indexing.index_manager import load_existing_index

logger = get_logger(__name__)

class IndexingService:
    """Service to handle document indexing logic."""
    
    METADATA_FILE = "./metadata/indexed_files.json"
    UPLOAD_DIR = "./uploads"
    BATCH_SIZE = 500

    def index_documents(self, documents: list, source_file: str) -> None:
        """
        Directly index a pre-parsed list of LlamaIndex Documents.
        Persists the index and updates metadata immediately.
        Used by the IngestionService pipeline.
        """
        logger.info(f"IndexingService: preparing to index {len(documents)} documents for '{source_file}'")
        
        # Load metadata
        if os.path.exists(self.METADATA_FILE):
            with open(self.METADATA_FILE, "r") as f:
                metadata = json.load(f)
        else:
            metadata = {"indexed_files": []}

        indexed_files = set(metadata.get("indexed_files", []))
        
        # We index even if it's already in the set? 
        # Actually the background job caller handles duplicate checking, 
        # but to be safe we just add to the set.
        
        index = load_existing_index()
        
        doc_count = len(documents)
        for i in range(0, doc_count, self.BATCH_SIZE):
            batch = documents[i:i+self.BATCH_SIZE]
            logger.info(f"Inserting batch {i // self.BATCH_SIZE + 1} for '{source_file}'")
            for doc in batch:
                index.insert(doc)
                
        logger.info(f"IndexingService: Persisting updated index to storage after '{source_file}'.")
        index.storage_context.persist(persist_dir="./storage")
        
        indexed_files.add(source_file)
        metadata["indexed_files"] = list(indexed_files)
        os.makedirs(os.path.dirname(self.METADATA_FILE), exist_ok=True)
        with open(self.METADATA_FILE, "w") as f:
            json.dump(metadata, f, indent=4)
        
        logger.info(f"IndexingService: index complete for '{source_file}'.")

    def run_incremental_update(self) -> Dict[str, Any]:
        """
        Scans the UPLOAD_DIR for new files, indexes them in batches,
        and persists the updated index and metadata.
        Returns a dictionary of execution statistics.
        """
        logger.info("Starting incremental index update.")
        
        # Initialize stats
        stats = {
            "processed_files": [],
            "skipped_files": [],
            "indexed_documents_count": 0
        }

        # Load metadata
        if os.path.exists(self.METADATA_FILE):
            with open(self.METADATA_FILE, "r") as f:
                metadata = json.load(f)
        else:
            metadata = {"indexed_files": []}

        indexed_files = set(metadata.get("indexed_files", []))
        index = load_existing_index()
        
        # Ensure upload dir exists
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

        for file in os.listdir(self.UPLOAD_DIR):
            if file in indexed_files:
                logger.info(f"Skipping {file} - already indexed.")
                stats["skipped_files"].append(file)
                continue

            logger.info(f"Processing {file}")
            file_path = os.path.join(self.UPLOAD_DIR, file)
            
            documents = load_single_excel(file_path)
            doc_count = len(documents)
            logger.info(f"Created {doc_count} documents from {file}")
            stats["indexed_documents_count"] += doc_count

            for i in range(0, doc_count, self.BATCH_SIZE):
                batch = documents[i:i+self.BATCH_SIZE]
                logger.info(f"Inserting batch {i // self.BATCH_SIZE + 1} for {file}")
                
                for doc in batch:
                    index.insert(doc)

            indexed_files.add(file)
            stats["processed_files"].append(file)

        # Persist changes if any processing occurred
        if stats["processed_files"]:
            logger.info("Persisting updated index to storage.")
            index.storage_context.persist(persist_dir="./storage")
            
            metadata["indexed_files"] = list(indexed_files)
            
            os.makedirs(os.path.dirname(self.METADATA_FILE), exist_ok=True)
            with open(self.METADATA_FILE, "w") as f:
                json.dump(metadata, f, indent=4)
        
        logger.info("Incremental update complete.")
        return stats
