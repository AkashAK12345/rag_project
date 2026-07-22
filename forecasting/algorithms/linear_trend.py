import statistics

def compute(values: list[float], horizon_days: int) -> tuple[float, float, float, str]:
    """
    Computes a linear trend forecast using Ordinary Least Squares (OLS) regression.
    """
    if not values:
        raise ValueError("Cannot compute Linear Trend on empty values.")
        
    n = len(values)
    if n == 1:
        predicted = values[0]
        margin = predicted * 0.1
        slope = 0.0
    else:
        # X is 0, 1, 2, ...
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean)**2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0.0
        intercept = y_mean - slope * x_mean
        
        # Predict next period (n)
        predicted = intercept + slope * n
        
        # Calculate standard error of the estimate
        residuals = [values[i] - (intercept + slope * x[i]) for i in range(n)]
        sse = sum(r**2 for r in residuals)
        mse = sse / (n - 2) if n > 2 else 0.0
        se = mse ** 0.5
        margin = 1.96 * se
        
    lower = max(0.0, predicted - margin)
    upper = predicted + margin
    
    methodology = f"Linear Trend Regression (slope={slope:.2f}, n={n})"
    return predicted, lower, upper, methodology
