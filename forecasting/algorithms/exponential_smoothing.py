import statistics

def compute(values: list[float], horizon_days: int, alpha: float = 0.3) -> tuple[float, float, float, str]:
    """
    Computes a single exponential smoothing forecast.
    """
    if not values:
        raise ValueError("Cannot compute Exponential Smoothing on empty values.")
        
    if not (0.0 < alpha <= 1.0):
        raise ValueError("Alpha must be between 0.0 (exclusive) and 1.0 (inclusive).")
        
    # Start with the first value as the initial smoothed value
    smoothed = values[0]
    for v in values[1:]:
        smoothed = alpha * v + (1 - alpha) * smoothed
        
    predicted = smoothed
    
    if len(values) > 1:
        stdev = statistics.stdev(values)
        margin = 1.96 * stdev
    else:
        margin = predicted * 0.1
        
    lower = max(0.0, predicted - margin)
    upper = predicted + margin
    
    methodology = f"Exponential Smoothing (a={alpha:.2f})"
    return predicted, lower, upper, methodology
