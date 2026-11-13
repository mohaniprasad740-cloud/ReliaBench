# Reliabench — Statistical Evaluation Methodology

## 1. Executive Summary

Reliabench departs from standard single-turn LLM benchmarks by evaluating **repeated execution consistency**, **fault tolerance**, and **resilience under systemic perturbations**. This document provides the mathematical foundations, finite-sample estimators, confidence interval calculations, latency distributions, cost attribution, and aggregation formulas implemented in `backend/app/evaluation/metrics.py`.

---

## 2. Metric Formulations

### 2.1. Pass Rate ($\hat{p}$)

For a given task and agent evaluation across $n$ valid trials where $s$ trials pass the deterministic task verifier:

$$\hat{p} = \frac{s}{n}$$

**Rules:**
- If $n = 0$, the metric returns `null` (never zero).
- Infrastructure failures, cancelled trials, and harness setup errors are excluded from $n$ and reported separately as invalid trials.

### 2.2. Wilson Score Confidence Interval (95% CI)

For binomial proportions with small sample sizes ($n \le 30$), normal approximations fail. Reliabench implements the asymmetric Wilson score interval:

$$\text{Center} = \frac{\hat{p} + \frac{z^2}{2n}}{1 + \frac{z^2}{n}}$$

$$\text{Margin} = \frac{z \cdot \sqrt{\frac{\hat{p}(1 - \hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

$$\text{Lower} = \max\left(0.0, \text{Center} - \text{Margin}\right), \quad \text{Upper} = \min\left(1.0, \text{Center} + \text{Margin}\right)$$

For a 95% two-sided confidence interval, $z \approx 1.95996$.
- If $n = 0$, returns `null`.
- Bounds strictly respect the $[0.0, 1.0]$ probability domain.

### 2.3. Pass@k (Unbiased Finite-Sample Estimator)

Measures the probability that at least one of $k$ attempts succeeds from an observed pool of $n$ rollout attempts with $s$ successes ($n \ge k$):

$$\text{Pass}@k = 1 - \frac{\binom{n - s}{k}}{\binom{n}{k}}$$

**Edge cases:**
- If $n < k$, returns `null` (insufficient samples).
- If $n - s < k$, $\text{Pass}@k = 1.0$.
- Uses `math.comb` to eliminate floating-point overflow and precision loss.

### 2.4. Pass^k (All k Succeed)

Measures the probability that all $k$ attempts succeed consecutively. Under the observed finite sample:

$$\text{Pass}^k = \frac{\binom{s}{k}}{\binom{n}{k}}$$

**Edge cases:**
- If $n < k$ or $s < k$, $\text{Pass}^k = 0.0$.
- Distinct from the independent identically distributed (i.i.d.) asymptotic approximation $\hat{p}^k$.

### 2.5. Recovery Rate

Measures the proportion of injected-failure trials from which an agent successfully recovers and passes verification:

$$\text{Recovery Rate} = \frac{\text{Recovered Eligible Injected-Failure Trials}}{\text{Eligible Injected-Failure Trials}}$$

**Scientific Recovery Criterion:**
An agent is classified as recovered **only if**:
1. The injected fault was actually executed and observed by the agent.
2. The agent continued execution or performed fallback routing.
3. The final task verifier passed deterministically.

A retry that still fails task verification is **not** counted as recovered.

---

## 3. Aggregation Methodology

### 3.1. Macro Aggregation

Unweighted arithmetic mean of per-task metric values across $T$ evaluated tasks:

$$\text{Macro Pass Rate} = \frac{1}{T} \sum_{t=1}^{T} \hat{p}_t$$

- Treats every benchmark task with equal importance regardless of sample count.
- Excludes tasks where $n_t = 0$ from the denominator $T$.

### 3.2. Micro Aggregation

Pooled trial-weighted ratio across all tasks:

$$\text{Micro Pass Rate} = \frac{\sum_{t=1}^{T} s_t}{\sum_{t=1}^{T} n_t}$$

---

## 4. Latency & Cost Distribution

### 4.1. Duration Metrics & Percentiles
- **Mean & Median (P50)**: Standard central tendency.
- **P90 & P95 Percentiles**: Interpolated quantile boundaries identifying latency tail degradation.
- **Sample Variance**: Unbiased $n-1$ variance for trial timing consistency.

### 4.2. Measured Cost per Success
$$\text{Cost per Success} = \frac{\text{Total Measured USD Cost}}{\text{Number of Successful Tasks}}$$

- Excludes unmeasured or unavailable costs (represented as `null`, never fabricated as `$0.00`).
