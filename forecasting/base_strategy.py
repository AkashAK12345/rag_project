"""
forecasting/base_strategy.py

Abstract interface for all ForecastStrategy implementations.

Design rules:
  - Strategies NEVER read from disk, query a vector store, or call the LLM.
  - Strategies NEVER access the RetrievalPlan or user question directly.
  - Strategies receive ONLY a ForecastRequest.
  - Strategies delegate algorithm selection to AlgorithmSelector.
  - Each strategy is responsible for one thing: extracting the relevant
    numeric series from BusinessObservation.key_values and producing
    a ForecastResult.

Replacing a strategy with a Prophet or ARIMA implementation means
only implementing this interface with a new class — nothing else changes.
"""

from abc import ABC, abstractmethod

from schemas.forecast_context import ForecastRequest, ForecastResult


class ForecastStrategy(ABC):
    """
    Contract for all concrete forecast strategy implementations.

    A strategy is responsible for:
      1. Extracting numeric values from ForecastRequest.observations.
      2. Delegating algorithm selection to AlgorithmSelector.
      3. Executing the computation via AlgorithmSelector.compute().
      4. Returning a fully populated ForecastResult.

    A strategy MUST NOT:
      - Perform KPI calculations (that is Analytics' responsibility).
      - Access LLM, vector store, or any I/O.
      - Raise exceptions for insufficient data — return a low-confidence
        result with a warning instead, letting ForecastEngine collect it.
    """

    @abstractmethod
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        """
        Produce a deterministic forecast from the given request.

        Args:
            request: A ForecastRequest containing metric, horizon, and observations.

        Returns:
            A ForecastResult with full provenance (algorithm, methodology,
            observations_used, historical_period).
        """
        ...
