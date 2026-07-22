"""
forecasting/strategies/_helpers.py

Shared utilities for ForecastStrategy implementations.
"""

from schemas.query_context import BusinessObservation
from schemas.forecast_context import (
    ForecastAlgorithm,
    ForecastHorizon,
    ForecastMetric,
    ForecastResult,
)

def extract_numeric_series(observations: list[BusinessObservation], keys: list[str]) -> list[float]:
    """
    Extracts a numeric series by checking a list of possible keys in order of preference.
    Returns a list of floats. Ignores observations where the keys are missing or unparseable.
    """
    series = []
    for obs in observations:
        for key in keys:
            if key in obs.key_values:
                val_str = obs.key_values[key].replace(",", "").replace("$", "").strip()
                try:
                    series.append(float(val_str))
                    break  # Stop at first matching key for this observation
                except ValueError:
                    pass
    return series


def derive_confidence(num_observations: int, min_required: int = 3, optimal: int = 12) -> float:
    """
    Derives a confidence score [0.0 - 1.0] based on the number of observations.
    Fewer than min_required -> 0.0 (strategies should raise ValueError before this).
    Between min_required and optimal -> scales from 0.5 to 0.9.
    Above optimal -> 0.95.
    """
    if num_observations < min_required:
        return 0.0
    if num_observations >= optimal:
        return 0.95
    fraction = (num_observations - min_required) / (optimal - min_required)
    return 0.5 + fraction * 0.4


def build_result(
    metric: ForecastMetric,
    horizon: ForecastHorizon,
    predicted: float,
    lower: float,
    upper: float,
    methodology: str,
    algorithm: ForecastAlgorithm,
    num_observations: int,
) -> ForecastResult:
    """
    Constructs a fully populated ForecastResult.
    """
    return ForecastResult(
        metric=metric,
        forecast_period=horizon.label,
        predicted_value=predicted,
        confidence=derive_confidence(num_observations),
        lower_bound=lower,
        upper_bound=upper,
        algorithm=algorithm,
        methodology=methodology,
        observations_used=num_observations,
        historical_period=f"Last {num_observations} observations",
    )
