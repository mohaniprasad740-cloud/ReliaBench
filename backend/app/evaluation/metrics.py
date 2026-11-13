import math
from typing import List, Optional, Dict, Any, Tuple

class ReliabilityMetricsCalculator:
    """
    Standardized mathematical evaluation engine for Reliabench.
    Calculates Pass Rate, Wilson Score Confidence Intervals, Pass@k, Pass^k,
    Recovery Rate, Mean/Median Duration, and Execution Variance.
    """

    @staticmethod
    def calculate_pass_rate(successes: int, total_valid_trials: int) -> Optional[float]:
        """
        Pass Rate: Successful task executions divided by total valid executions.
        Returns None if total_valid_trials == 0 (distinguishes unavailable from zero).
        """
        if total_valid_trials <= 0:
            return None
        return round(float(successes) / float(total_valid_trials), 4)

    @staticmethod
    def calculate_wilson_confidence_interval(
        successes: int, total_valid_trials: int, confidence: float = 0.95
    ) -> Optional[Dict[str, float]]:
        """
        Wilson score interval for a binomial proportion.
        Handles small sample sizes without exceeding [0, 1] bounds.
        Default 95% confidence level (z ~ 1.95996).
        """
        if total_valid_trials <= 0:
            return None

        z = 1.95996  # 95% two-sided normal quantile
        n = float(total_valid_trials)
        p_hat = float(successes) / n

        denominator = 1.0 + (z**2) / n
        center_adj = p_hat + (z**2) / (2.0 * n)
        margin = z * math.sqrt((p_hat * (1.0 - p_hat) + (z**2) / (4.0 * n)) / n)

        lower = max(0.0, (center_adj - margin) / denominator)
        upper = min(1.0, (center_adj + margin) / denominator)

        return {
            "lower": round(lower, 4),
            "upper": round(upper, 4),
            "confidence": confidence
        }

    @staticmethod
    def calculate_pass_at_k(n: int, c: int, k: int) -> Optional[float]:
        """
        Pass@k: Probability that at least one of k independent attempts succeeds.
        Uses unbiased estimator: 1 - comb(n - c, k) / comb(n, k)
        where n = total trials, c = successful trials, k = sample size evaluated.
        Returns None if insufficient sample size (n < k).
        """
        if n <= 0 or k <= 0 or k > n:
            return None

        if n - c < k:
            return 1.0

        try:
            comb_fail = math.comb(n - c, k)
            comb_total = math.comb(n, k)
            prob_all_fail = comb_fail / comb_total
            return round(1.0 - prob_all_fail, 4)
        except Exception:
            return 1.0 if c > 0 else 0.0

    @staticmethod
    def calculate_pass_to_k(n: int, c: int, k: int) -> Optional[float]:
        """
        Pass^k: The probability/fraction that all k attempts succeed.
        Under independent identically distributed trials: p^k.
        Also calculates exact hypergeometric sample fraction: comb(c, k) / comb(n, k).
        Returns None if n < k.
        """
        if n <= 0 or k <= 0 or k > n:
            return None

        if c < k:
            return 0.0

        try:
            comb_succ = math.comb(c, k)
            comb_total = math.comb(n, k)
            return round(comb_succ / comb_total, 4)
        except Exception:
            return 1.0 if c == n else 0.0

    @staticmethod
    def calculate_recovery_rate(recoveries: int, total_injected_failures: int) -> Optional[float]:
        """
        Recovery Rate: Proportion of injected-failure executions that recover and complete successfully.
        Returns None if no failures were injected (distinguishes unavailable from zero).
        """
        if total_injected_failures <= 0:
            return None
        return round(float(recoveries) / float(total_injected_failures), 4)

    @staticmethod
    def calculate_duration_metrics(durations: List[float]) -> Dict[str, Any]:
        """
        Calculates mean, median, min, max, and sample variance across repeated trials.
        """
        if not durations:
            return {
                "avg_duration": 0.0,
                "median_duration": 0.0,
                "variance": 0.0,
                "min": 0.0,
                "max": 0.0,
                "samples": 0
            }

        count = len(durations)
        mean_val = sum(durations) / count

        # Median calculation
        sorted_d = sorted(durations)
        if count % 2 == 1:
            median_val = sorted_d[count // 2]
        else:
            median_val = (sorted_d[(count // 2) - 1] + sorted_d[count // 2]) / 2.0

        # Sample variance
        if count > 1:
            variance_val = sum((x - mean_val) ** 2 for x in durations) / (count - 1)
        else:
            variance_val = 0.0

        return {
            "avg_duration": round(mean_val, 2),
            "median_duration": round(median_val, 2),
            "variance": round(variance_val, 4),
            "min": round(min(durations), 2),
            "max": round(max(durations), 2),
            "samples": count
        }

    @staticmethod
    def aggregate_task_metrics(
        task_results: List[Dict[str, Any]],
        weighting: str = "macro",  # "macro" (unweighted mean across tasks) or "micro" (trial-weighted)
    ) -> Dict[str, Any]:
        """Calculates Macro-averaged or Micro-averaged metrics across multiple benchmark tasks."""
        if not task_results:
            return {
                "weighting": weighting,
                "overall_pass_rate": None,
                "macro_pass_rate": None,
                "micro_pass_rate": None,
                "tasks_count": 0,
            }

        tasks_count = len(task_results)
        macro_pass_rates = [t["pass_rate"] for t in task_results if t.get("pass_rate") is not None]
        macro_pass = sum(macro_pass_rates) / len(macro_pass_rates) if macro_pass_rates else None

        total_successes = sum(t.get("successes", 0) for t in task_results)
        total_trials = sum(t.get("trials", 0) for t in task_results)
        micro_pass = (total_successes / total_trials) if total_trials > 0 else None

        chosen_rate = macro_pass if weighting == "macro" else micro_pass

        return {
            "weighting": weighting,
            "overall_pass_rate": round(chosen_rate, 4) if chosen_rate is not None else None,
            "macro_pass_rate": round(macro_pass, 4) if macro_pass is not None else None,
            "micro_pass_rate": round(micro_pass, 4) if micro_pass is not None else None,
            "total_successes": total_successes,
            "total_trials": total_trials,
            "tasks_count": tasks_count,
        }



def calculate_pass_at_k(n: int, c: int, k: int) -> float:
    val = ReliabilityMetricsCalculator.calculate_pass_at_k(n, c, k)
    return val if val is not None else 0.0


def calculate_pass_pow_k(successes_list: List[int], k: int) -> float:
    """Calculates pass^k (fraction of runs/trials where all k passed or p^k)."""
    if not successes_list or k <= 0:
        return 0.0
    c = successes_list[0] if isinstance(successes_list, list) else int(successes_list)
    val = ReliabilityMetricsCalculator.calculate_pass_to_k(k, c, k)
    return val if val is not None else 0.0


def wilson_score_interval(successes: int, total: int) -> Tuple[float, float]:
    res = ReliabilityMetricsCalculator.calculate_wilson_confidence_interval(successes, total)
    if not res:
        return (0.0, 1.0)
    return (res["lower"], res["upper"])

