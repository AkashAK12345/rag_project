"""
services/insight_builder.py

Converts a collection of BusinessObservation objects into BusinessInsight objects.

Responsibilities:
  - Scan observations for signals (numeric trends, keyword patterns).
  - Produce structured BusinessInsight objects with severity and evidence.
  - Operate entirely on in-memory data structures (no I/O, no LLM).

Design principles:
  - All methods are pure functions of their inputs.
  - InsightBuilder knows NOTHING about where observations came from.
  - InsightBuilder knows NOTHING about the vector store or the LLM.
  - It is independently unit-testable with a list of mock observations.

Why observations before insights?
  Observations are direct extractions from retrieved text ("revenue: 8000").
  Insights are interpretations ("Revenue declined 20% vs prior period").
  Separating these two steps keeps the extraction logic simple and the
  interpretation logic focused. A future ML-based insight engine can replace
  this class without touching how observations are created.
"""

import re
from collections import defaultdict

from core.logging import get_logger
from schemas.query_context import BusinessObservation
from schemas.business_insight import (
    BusinessInsight,
    InsightSeverity,
    InsightType,
)
from schemas.report import BusinessDomain

logger = get_logger(__name__)

# Numeric patterns — match values like "10,000", "8.5%", "-15%", "1200.50"
_NUMERIC_RE = re.compile(r"-?\d[\d,]*\.?\d*%?")

# Keywords that signal negative direction
_NEGATIVE_SIGNALS = {
    "decrease", "declined", "dropped", "reduced", "lower", "down",
    "loss", "spoil", "wast", "expir", "shortage", "absent", "poor",
    "low", "below", "defici", "gap",
}

# Keywords that signal positive direction
_POSITIVE_SIGNALS = {
    "increase", "grew", "growth", "higher", "up", "improved",
    "exceeded", "surplus", "profit", "revenue", "gain", "top",
}

# Domain-specific risk signal keywords
_DOMAIN_RISK_SIGNALS: dict[BusinessDomain, list[str]] = {
    BusinessDomain.INVENTORY: ["low stock", "out of stock", "near expiry", "expired", "below reorder"],
    BusinessDomain.WASTAGE: ["spoiled", "damaged", "discarded", "high wastage", "shrinkage"],
    BusinessDomain.PURCHASES: ["price increase", "supplier", "overpriced", "delayed"],
    BusinessDomain.EMPLOYEES: ["absent", "shortage", "understaffed", "leave", "low attendance"],
    BusinessDomain.PRODUCTION: ["low yield", "shortfall", "batch failure", "below target"],
    BusinessDomain.FINANCE: ["loss", "deficit", "over budget", "negative margin"],
    BusinessDomain.SALES: ["low sales", "declined", "below target", "low revenue"],
}

# Cross-domain causal chains
_CAUSAL_CHAINS: list[tuple[BusinessDomain, BusinessDomain, str]] = [
    (BusinessDomain.PURCHASES, BusinessDomain.FINANCE,
     "Supplier price increases directly raise food cost and compress margins."),
    (BusinessDomain.INVENTORY, BusinessDomain.SALES,
     "Low stock levels can prevent order fulfilment and reduce outlet revenue."),
    (BusinessDomain.WASTAGE, BusinessDomain.FINANCE,
     "High wastage increases the effective cost of goods and erodes margins."),
    (BusinessDomain.EMPLOYEES, BusinessDomain.PRODUCTION,
     "Staff shortages reduce kitchen output capacity and recipe yield."),
    (BusinessDomain.PRODUCTION, BusinessDomain.SALES,
     "Reduced production output limits menu availability and sales volume."),
    (BusinessDomain.INVENTORY, BusinessDomain.WASTAGE,
     "Overstocked perishables increase the risk of spoilage and wastage."),
    (BusinessDomain.PURCHASES, BusinessDomain.INVENTORY,
     "Procurement gaps can lead to stock shortfalls or emergency over-purchasing."),
]


class InsightBuilder:
    """
    Derives BusinessInsight objects from a list of BusinessObservation objects.

    Usage:
        builder = InsightBuilder()
        insights = builder.build(observations)
    """

    def build(self, observations: list[BusinessObservation]) -> list[BusinessInsight]:
        """
        Analyze observations and return a deduplicated list of insights.

        Args:
            observations: List from BusinessContextBuilder, grouped implicitly by domain.

        Returns:
            List of BusinessInsight, ordered by severity (CRITICAL first).
        """
        if not observations:
            return []

        # Group observations by domain
        by_domain: dict[BusinessDomain, list[BusinessObservation]] = defaultdict(list)
        for obs in observations:
            by_domain[obs.domain].append(obs)

        insights: list[BusinessInsight] = []

        # Step 1: Per-domain signal analysis
        for domain, domain_obs in by_domain.items():
            domain_insights = self._analyze_domain(domain, domain_obs)
            insights.extend(domain_insights)

        # Step 2: Cross-domain correlation signals
        present_domains = set(by_domain.keys())
        cross_insights = self._detect_cross_domain_signals(present_domains, observations)
        insights.extend(cross_insights)

        # Step 3: Sort by severity
        severity_order = {
            InsightSeverity.CRITICAL: 0,
            InsightSeverity.WARNING: 1,
            InsightSeverity.INFO: 2,
            InsightSeverity.POSITIVE: 3,
        }
        insights.sort(key=lambda i: severity_order.get(i.severity, 99))

        logger.info(f"InsightBuilder: produced {len(insights)} insight(s) from {len(observations)} observation(s).")
        return insights

    # ------------------------------------------------------------------
    # Private analysis methods
    # ------------------------------------------------------------------

    def _analyze_domain(
        self, domain: BusinessDomain, observations: list[BusinessObservation]
    ) -> list[BusinessInsight]:
        """Scan a single domain's observations for risk/positive signals."""
        insights: list[BusinessInsight] = []
        risk_keywords = _DOMAIN_RISK_SIGNALS.get(domain, [])
        source_files = list({obs.source_file for obs in observations})

        negative_evidence: list[str] = []
        positive_evidence: list[str] = []

        for obs in observations:
            text_lower = obs.raw_text.lower()

            # Check for domain-specific risk keywords
            for kw in risk_keywords:
                if kw in text_lower:
                    negative_evidence.append(f"[{obs.source_file}] {obs.raw_text[:120]}")
                    break

            # Check for general directional signals
            if any(neg in text_lower for neg in _NEGATIVE_SIGNALS):
                negative_evidence.append(f"[{obs.source_file}] {obs.raw_text[:120]}")
            elif any(pos in text_lower for pos in _POSITIVE_SIGNALS):
                positive_evidence.append(f"[{obs.source_file}] {obs.raw_text[:120]}")

        # Generate insights from evidence
        if negative_evidence:
            severity = (
                InsightSeverity.CRITICAL
                if len(negative_evidence) >= 3
                else InsightSeverity.WARNING
            )
            insights.append(BusinessInsight(
                insight_type=self._map_domain_to_insight_type(domain),
                severity=severity,
                domain=domain,
                headline=f"Negative signals detected in {domain.value.title()} data "
                         f"({len(negative_evidence)} indicator(s)).",
                evidence=list(set(negative_evidence))[:5],
                source_files=source_files,
            ))

        if positive_evidence and not negative_evidence:
            insights.append(BusinessInsight(
                insight_type=InsightType.POSITIVE_SIGNAL,
                severity=InsightSeverity.POSITIVE,
                domain=domain,
                headline=f"Positive signals detected in {domain.value.title()} data "
                         f"({len(positive_evidence)} indicator(s)).",
                evidence=list(set(positive_evidence))[:3],
                source_files=source_files,
            ))

        return insights

    def _detect_cross_domain_signals(
        self,
        present_domains: set[BusinessDomain],
        observations: list[BusinessObservation],
    ) -> list[BusinessInsight]:
        """Detect insights that require data from two or more domains."""
        insights: list[BusinessInsight] = []
        source_files = list({obs.source_file for obs in observations})

        for from_domain, to_domain, description in _CAUSAL_CHAINS:
            if from_domain in present_domains and to_domain in present_domains:
                insights.append(BusinessInsight(
                    insight_type=InsightType.CROSS_DOMAIN_CORRELATION,
                    severity=InsightSeverity.INFO,
                    domain=from_domain,
                    related_domains=[to_domain],
                    headline=description,
                    evidence=[
                        f"Both {from_domain.value} and {to_domain.value} data present in context."
                    ],
                    source_files=source_files,
                ))

        return insights

    @staticmethod
    def _map_domain_to_insight_type(domain: BusinessDomain) -> InsightType:
        return {
            BusinessDomain.INVENTORY: InsightType.INVENTORY_RISK,
            BusinessDomain.WASTAGE: InsightType.WASTAGE_CONCERN,
            BusinessDomain.PURCHASES: InsightType.COST_PRESSURE,
            BusinessDomain.EMPLOYEES: InsightType.STAFFING_CONCERN,
            BusinessDomain.PRODUCTION: InsightType.PRODUCTION_SHORTFALL,
            BusinessDomain.FINANCE: InsightType.PERFORMANCE_CHANGE,
            BusinessDomain.SALES: InsightType.PERFORMANCE_CHANGE,
        }.get(domain, InsightType.GENERAL_OBSERVATION)
