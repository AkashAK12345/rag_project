import statistics

def compute(values: list[float], horizon_days: int, window: int = 6) -> tuple[float, float, float, str]:
    """
    Computes a simple moving average over the specified window.
    """
    if not values:
        raise ValueError("Cannot compute moving average on empty values.")
    
    w = min(window, len(values))
    subset = values[-w:]
    predicted = statistics.mean(subset)
    
    if w > 1:
        stdev = statistics.stdev(subset)
        margin = 1.96 * stdev
    else:
        margin = predicted * 0.1
        
    lower = max(0.0, predicted - margin)
    upper = predicted + margin
    
    methodology = f"Simple Moving Average (window={w})"
    return predicted, lower, upper, methodology
