import pytest
from app.evaluation.metrics import ReliabilityMetricsCalculator

def test_metrics_percentiles_empty():
    res = ReliabilityMetricsCalculator.calculate_percentiles([])
    assert res["samples"] == 0
    assert res["p50"] is None
    assert res["p90"] is None
    assert res["p95"] is None

def test_metrics_percentiles_single_and_multiple():
    # Single sample
    res_single = ReliabilityMetricsCalculator.calculate_percentiles([42.5])
    assert res_single["samples"] == 1
    assert res_single["p50"] == 42.5
    assert res_single["p90"] == 42.5
    assert res_single["p95"] == 42.5

    # Multiple samples
    samples = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    res = ReliabilityMetricsCalculator.calculate_percentiles(samples)
    assert res["samples"] == 10
    assert res["p50"] == 55.0  # Median of 1-10 is between 5 and 6
    assert res["p90"] == 91.0 or res["p90"] == 90.0 or 85.0 <= res["p90"] <= 95.0
    assert res["p95"] >= res["p90"]

def test_cost_per_success():
    # Null total cost
    assert ReliabilityMetricsCalculator.calculate_cost_per_success(None, 5) is None
    # Zero successes
    assert ReliabilityMetricsCalculator.calculate_cost_per_success(10.0, 0) is None
    # Negative successes
    assert ReliabilityMetricsCalculator.calculate_cost_per_success(10.0, -1) is None
    # Valid
    assert ReliabilityMetricsCalculator.calculate_cost_per_success(1.50, 3) == 0.50

def test_wilson_boundary_edge_cases():
    # 0 valid trials returns None
    assert ReliabilityMetricsCalculator.calculate_wilson_confidence_interval(0, 0) is None
    
    # 0 successes out of 10
    ci_zero = ReliabilityMetricsCalculator.calculate_wilson_confidence_interval(0, 10)
    assert ci_zero is not None
    assert ci_zero["lower"] == 0.0
    assert ci_zero["upper"] > 0.0

    # All successes out of 10
    ci_full = ReliabilityMetricsCalculator.calculate_wilson_confidence_interval(10, 10)
    assert ci_full is not None
    assert ci_full["lower"] > 0.0
    assert ci_full["upper"] == 1.0

def test_pass_at_k_and_pass_to_k_edge_cases():
    # n < k returns None
    assert ReliabilityMetricsCalculator.calculate_pass_at_k(2, 2, 5) is None
    assert ReliabilityMetricsCalculator.calculate_pass_to_k(2, 2, 5) is None
    
    # n == k
    assert ReliabilityMetricsCalculator.calculate_pass_at_k(5, 0, 5) == 0.0
    assert ReliabilityMetricsCalculator.calculate_pass_at_k(5, 5, 5) == 1.0
    assert ReliabilityMetricsCalculator.calculate_pass_to_k(5, 5, 5) == 1.0
    assert ReliabilityMetricsCalculator.calculate_pass_to_k(5, 4, 5) == 0.0
