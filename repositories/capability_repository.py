import os
import json
import re
from dataclasses import asdict
from core.logging import get_logger
from schemas.report import WorkbookCapabilityGraph, SheetCapability, MetricCapability, ChartCapability, BusinessDomain

logger = get_logger(__name__)

STORAGE_DIR = os.path.join("storage", "capabilities")

class CapabilityRepository:
    """
    Abstracts storage for the WorkbookCapabilityGraph.
    Currently uses JSON files on disk. Can be migrated to DB/S3 with zero service changes.
    Capabilities persist indefinitely on disk without eviction or TTL; to be addressed in future production hardening.
    """
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        
    def _get_path(self, workbook_id: str) -> str:
        safe_id = re.sub(r'[^a-zA-Z0-9_\-.]', '_', workbook_id)
        return os.path.join(STORAGE_DIR, f"{safe_id}.json")
        
    def save(self, workbook_id: str, capability_graph: WorkbookCapabilityGraph) -> None:
        try:
            # We must serialize custom Enum and Dataclasses manually or use a helper
            class CustomEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, set):
                        return list(obj)
                    if hasattr(obj, "value"):
                        return obj.value
                    if hasattr(obj, "__dataclass_fields__"):
                        return asdict(obj)
                    return super().default(obj)
                    
            data = json.dumps(capability_graph, cls=CustomEncoder, indent=2)
            with open(self._get_path(workbook_id), "w", encoding="utf-8") as f:
                f.write(data)
            logger.info(f"CapabilityRepository: Saved capabilities for '{workbook_id}'.")
        except Exception as e:
            logger.error(f"CapabilityRepository: Failed to save capabilities for '{workbook_id}': {e}")
            raise
            
    def load(self, workbook_id: str) -> WorkbookCapabilityGraph | None:
        path = self._get_path(workbook_id)
        if not os.path.exists(path):
            return None
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Deserialize nested objects
            # Domains
            supported_domains = {BusinessDomain(d) for d in data.get("supported_domains", [])}
            
            # Metrics
            supported_metrics = [
                MetricCapability(
                    name=m["name"],
                    business_domain=BusinessDomain(m["business_domain"]),
                    source_sheet=m["source_sheet"],
                    source_parser=m["source_parser"],
                    required_fields=m["required_fields"],
                    optional_fields=m["optional_fields"],
                    confidence=m["confidence"]
                ) for m in data.get("supported_metrics", [])
            ]
            
            # Charts
            supported_charts = [
                ChartCapability(
                    name=c["name"],
                    business_domain=BusinessDomain(c["business_domain"]),
                    source_sheet=c["source_sheet"],
                    source_parser=c["source_parser"],
                    required_fields=c["required_fields"],
                    optional_fields=c["optional_fields"],
                    confidence=c["confidence"]
                ) for c in data.get("supported_charts", [])
            ]
            
            from schemas.report import DetectionDiagnostic
            sheets = []
            for s in data.get("sheets", []):
                rankings = []
                for r in s.get("candidate_rankings", []):
                    rankings.append(DetectionDiagnostic(**r))
                    
                s_metrics = [MetricCapability(**{**m, 'business_domain': BusinessDomain(m['business_domain'])}) for m in s.get("supported_metrics", [])]
                s_charts = [ChartCapability(**{**c, 'business_domain': BusinessDomain(c['business_domain'])}) for c in s.get("supported_charts", [])]
                s_domains = [BusinessDomain(d) for d in s.get("supported_domains", [])]
                
                sheets.append(SheetCapability(
                    sheet_name=s["sheet_name"],
                    accepted_parsers=s["accepted_parsers"],
                    candidate_rankings=rankings,
                    supported_metrics=s_metrics,
                    supported_charts=s_charts,
                    supported_domains=s_domains
                ))
            
            return WorkbookCapabilityGraph(
                workbook_name=data.get("workbook_name", workbook_id),
                sheets=sheets,
                supported_metrics=supported_metrics,
                supported_charts=supported_charts,
                supported_domains=supported_domains
            )
        except Exception as e:
            logger.error(f"CapabilityRepository: Failed to load capabilities for '{workbook_id}': {e}")
            return None
            
    def load_all(self) -> list[WorkbookCapabilityGraph]:
        graphs = []
        if not os.path.exists(STORAGE_DIR):
            return graphs
            
        for filename in os.listdir(STORAGE_DIR):
            if filename.endswith(".json"):
                workbook_id = filename[:-5]
                graph = self.load(workbook_id)
                if graph:
                    graphs.append(graph)
        return graphs
