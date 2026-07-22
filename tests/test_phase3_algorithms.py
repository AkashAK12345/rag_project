import pytest
import math

from forecasting.algorithms import (
    moving_average,
    weighted_moving_average,
    exponential_smoothing,
    linear_trend,
)

def test_moving_average_empty():
    with pytest.raises(ValueError):
        moving_average.compute([], 30)

def test_moving_average_single_value():
    p, l, u, m = moving_average.compute([100.0], 30)
    assert p == 100.0
    assert l == 90.0
    assert u == 110.0
    assert "1" in m

def test_moving_average_constant():
    p, l, u, m = moving_average.compute([50.0, 50.0, 50.0], 30, window=3)
    assert p == 50.0
    assert l == 50.0
    assert u == 50.0
    assert "3" in m

def test_moving_average_increasing():
    p, l, u, m = moving_average.compute([10.0, 20.0, 30.0], 30, window=3)
    assert p == 20.0
    assert l < p
    assert u > p

def test_wma_empty():
    with pytest.raises(ValueError):
        weighted_moving_average.compute([], 30)

def test_wma_single_value():
    p, l, u, m = weighted_moving_average.compute([100.0], 30)
    assert p == 100.0
    assert l == 90.0
    assert u == 110.0

def test_wma_constant():
    p, l, u, m = weighted_moving_average.compute([50.0, 50.0, 50.0], 30, window=3)
    assert p == 50.0
    assert l == 50.0
    assert u == 50.0

def test_wma_increasing():
    p, l, u, m = weighted_moving_average.compute([10.0, 20.0, 30.0], 30, window=3)
    # Weights: 1, 2, 3 -> (10*1 + 20*2 + 30*3) / 6 = (10 + 40 + 90) / 6 = 140 / 6 = 23.333
    assert math.isclose(p, 23.333333333333332)
    
def test_es_empty():
    with pytest.raises(ValueError):
        exponential_smoothing.compute([], 30)

def test_es_invalid_alpha():
    with pytest.raises(ValueError):
        exponential_smoothing.compute([10.0, 20.0], 30, alpha=0.0)
    with pytest.raises(ValueError):
        exponential_smoothing.compute([10.0, 20.0], 30, alpha=1.1)

def test_es_single_value():
    p, l, u, m = exponential_smoothing.compute([100.0], 30)
    assert p == 100.0
    assert l == 90.0
    assert u == 110.0

def test_es_constant():
    p, l, u, m = exponential_smoothing.compute([50.0, 50.0, 50.0], 30)
    assert p == 50.0
    assert l == 50.0
    assert u == 50.0

def test_es_increasing():
    p, l, u, m = exponential_smoothing.compute([10.0, 20.0, 30.0], 30, alpha=0.5)
    # smoothed1 = 10
    # smoothed2 = 0.5*20 + 0.5*10 = 15
    # smoothed3 = 0.5*30 + 0.5*15 = 22.5
    assert p == 22.5

def test_linear_trend_empty():
    with pytest.raises(ValueError):
        linear_trend.compute([], 30)

def test_linear_trend_single_value():
    p, l, u, m = linear_trend.compute([100.0], 30)
    assert p == 100.0
    assert l == 90.0
    assert u == 110.0

def test_linear_trend_constant():
    p, l, u, m = linear_trend.compute([50.0, 50.0, 50.0], 30)
    assert p == 50.0
    assert l == 50.0
    assert u == 50.0

def test_linear_trend_increasing():
    p, l, u, m = linear_trend.compute([10.0, 20.0, 30.0], 30)
    # y = 10x + 10. Next index is 3 -> 10*3 + 10 = 40.0
    assert math.isclose(p, 40.0)
    
def test_linear_trend_decreasing():
    p, l, u, m = linear_trend.compute([30.0, 20.0, 10.0], 30)
    # y = -10x + 30. Next index is 3 -> -10*3 + 30 = 0.0
    assert math.isclose(p, 0.0)
