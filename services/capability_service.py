from dataclasses import dataclass
from typing import Dict, Any, List
from repositories.capability_repository import CapabilityRepository
from schemas.report import WorkbookCapabilityGraph, CapabilityContext, BusinessDomain, MetricCapability, ChartCapability

@dataclass
class CapabilityExplanation:
    status: str
    reason: str | None = None
    required_fields: list[str] | None = None


class CapabilityService:
    def __init__(self, repository: CapabilityRepository | None = None):
        self.repository = repository or CapabilityRepository()

    def get_enterprise_graph(self) -> WorkbookCapabilityGraph:
        """Merges all available workbook capability graphs into one Enterprise Graph."""
        graphs = self.repository.load_all()
        
        all_metrics = []
        all_charts = []
        all_domains = set()
        
        for g in graphs:
            all_metrics.extend(g.supported_metrics)
            all_charts.extend(g.supported_charts)
            all_domains.update(g.supported_domains)
            
        return WorkbookCapabilityGraph(
            workbook_name="Enterprise",
            sheets=[],
            supported_metrics=all_metrics,
            supported_charts=all_charts,
            supported_domains=all_domains
        )

    def get_capability_context(self) -> CapabilityContext:
        """Returns a lightweight context for AI pipelines to prevent hallucination."""
        graph = self.get_enterprise_graph()
        
        supported_domains = [d.value for d in graph.supported_domains]
        all_domains = [d.value for d in BusinessDomain if d != BusinessDomain.UNKNOWN]
        unsupported_domains = list(set(all_domains) - set(supported_domains))
        
        supported_metrics = list({m.name for m in graph.supported_metrics})
        supported_charts = list({c.name for c in graph.supported_charts})
        
        return CapabilityContext(
            supported_domains=supported_domains,
            supported_metrics=supported_metrics,
            supported_charts=supported_charts,
            unsupported_domains=unsupported_domains
        )

    def explain_metric(self, metric_name: str, domain: BusinessDomain) -> CapabilityExplanation:
        """Checks if a metric is supported, and if not, returns a deterministic explanation."""
        graph = self.get_enterprise_graph()
        
        for m in graph.supported_metrics:
            if m.name == metric_name:
                return CapabilityExplanation(status="supported")
                
        # Unsupported. Find why.
        # Find which parsers could have provided it
        from reports.report_factory import REGISTERED_PARSERS
        possible_parsers = []
        required = []
        for p in REGISTERED_PARSERS:
            if metric_name in p.COVERAGE.get("metrics", []):
                possible_parsers.append(p.REPORT_NAMES[0])
                required.extend(p.REQUIRED_FIELDS)
                
        if possible_parsers:
            reason = f"{possible_parsers[0]} not detected"
            return CapabilityExplanation(
                status="unsupported",
                reason=reason,
                required_fields=list(set(required))
            )
            
        return CapabilityExplanation(
            status="unsupported",
            reason=f"Metric '{metric_name}' is not known to the system",
            required_fields=[]
        )

    def explain_chart(self, chart_name: str, domain: BusinessDomain) -> CapabilityExplanation:
        """Checks if a chart is supported, and if not, returns a deterministic explanation."""
        graph = self.get_enterprise_graph()
        
        for c in graph.supported_charts:
            if c.name == chart_name:
                return CapabilityExplanation(status="supported")
                
        # Unsupported. Find why.
        from reports.report_factory import REGISTERED_PARSERS
        possible_parsers = []
        required = []
        for p in REGISTERED_PARSERS:
            if chart_name in p.COVERAGE.get("charts", []):
                possible_parsers.append(p.REPORT_NAMES[0])
                required.extend(p.REQUIRED_FIELDS)
                
        if possible_parsers:
            reason = f"{possible_parsers[0]} not detected"
            return CapabilityExplanation(
                status="unsupported",
                reason=reason,
                required_fields=list(set(required))
            )
            
        return CapabilityExplanation(
            status="unsupported",
            reason=f"Chart '{chart_name}' is not known to the system",
            required_fields=[]
        )

    def generate_upload_summary(self, workbook_id: str) -> dict[str, Any]:
        """Generates a structured upload summary based on the given workbook_id graph."""
        graph = self.repository.load(workbook_id)
        if not graph:
            return {"error": "Capabilities not found for workbook."}
            
        detected_sheets = [s.sheet_name for s in graph.sheets if s.accepted_parsers]
        detected_domains = [d.value for d in graph.supported_domains]
        supported_metrics = list({m.name for m in graph.supported_metrics})
        supported_charts = list({c.name for c in graph.supported_charts})
        
        # Determine unsupported
        all_domains = [d for d in BusinessDomain if d != BusinessDomain.UNKNOWN]
        unsupported_domains = list(set(all_domains) - graph.supported_domains)
        
        recommended_uploads = []
        from reports.report_factory import REGISTERED_PARSERS
        for d in unsupported_domains:
            # recommend the first parser of that domain
            for p in REGISTERED_PARSERS:
                if p.BUSINESS_DOMAIN == d:
                    metrics = p.COVERAGE.get("metrics", [])
                    if metrics:
                        recommended_uploads.append(f"Upload a {p.REPORT_NAMES[0]} to unlock: " + ", ".join(metrics))
                    break
        
        return {
            "Workbook Name": graph.workbook_name,
            "Detected Sheets": detected_sheets,
            "Detected Domains": detected_domains,
            "Supported KPIs": supported_metrics,
            "Supported Charts": supported_charts,
            "Unsupported Domains": [d.value for d in unsupported_domains],
            "Recommended Uploads": recommended_uploads
        }
