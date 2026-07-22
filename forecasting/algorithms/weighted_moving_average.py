import statistics

def compute(values: list[float], horizon_days: int, window: int = 6) -> tuple[float, float, float, str]:
    """
    Computes a weighted moving average with linear weights (most recent observation has highest weight).
    """
    if not values:
        raise ValueError("Cannot compute WMA on empty values.")
    
    w = min(window, len(values))
    subset = values[-w:]
    
    if w == 1:
        predicted = subset[0]
        margin = predicted * 0.1
    else:
        weights = list(range(1, w + 1))
        total_weight = sum(weights)
        predicted = sum(v * w_i for v, w_i in zip(subset, weights)) / total_weight
        stdev = statistics.stdev(subset)
        margin = 1.96 * stdev
        
    lower = max(0.0, predicted - margin)
    upper = predicted + margin
    
    methodology = f"Weighted Moving Average (window={w}, linear weights)"
    return predicted, lower, upper, methodology
