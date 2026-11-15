# Reliabench Canonical Demo Dataset

## 1. Canonical Agents (4 Profiles)

Reliabench includes 4 pre-configured agent profiles demonstrating distinct architecture trade-offs:

| Agent Name | Framework | Model | Adapter Type | Focus / Specialty |
| :--- | :--- | :--- | :--- | :--- |
| **Atlas Research Agent** | LangGraph | `gpt-4o` | Simulator / Web | Deep multi-step technical research, synthesis, and Tavily-augmented citations. |
| **Nova Browser Agent** | Browser-Use | `claude-3-7-sonnet` | Simulator / Browser | Multi-step web automation, dynamic DOM interactions, checkout flows, and session state. |
| **Sentinel Workflow Agent** | CrewAI | `gpt-4o-mini` | Simulator / CLI | Complex multi-tool calling, SQL optimizations, resilient error recovery, and webhook retries. |
| **Swift Assistant** | Custom | `claude-3-5-haiku` | Simulator / Lightweight | Low-latency structured JSON extraction, rapid parsing, high throughput, and cost efficiency. |

---

## 2. Benchmark Suites & Tasks (14 Tasks across 5 Suites)

### Suite 1: Web Research & Grounding (Category: `Web Research`)
- **Task 1: FastAPI Dependency Injection Analysis (`task.web_research.fastapi_di`)**: Multi-page documentation synthesis and code pattern verification.
- **Task 2: CVE-2024 Exploit Mitigation Synthesis (`task.web_research.cve_synthesis`)**: Vulnerability mitigation retrieval and verifiable patch extraction.
- **Task 3: PyPI Wheel Build Metadata Extraction (`task.web_research.wheel_metadata`)**: Dependency tree inspection across binary package indexes.

### Suite 2: Multi-Step Browser Automation (Category: `Browser Automation`)
- **Task 4: Multi-Step E-Commerce Checkout Flow (`task.browser.checkout_flow`)**: Cart manipulation, shipping address validation, and simulated payment submission.
- **Task 5: Paginated Data Table Scrape (`task.browser.table_pagination`)**: Multi-page pagination traversal and structured deduplicated record extraction.
- **Task 6: Authentication & Session State Maintenance (`task.browser.auth_state`)**: Login form submission, session cookie verification, and protected resource access.

### Suite 3: Multi-Tool Execution & Code Operations (Category: `Tool Execution`)
- **Task 7: SQL Query Optimization & N+1 Elimination (`task.tools.sql_n_plus_one`)**: EXPLAIN query plan analysis and join rewrite assertion verification.
- **Task 8: Nested JSON Transformation Pipeline (`task.tools.json_transform`)**: Multi-stage schema transformation with validation against strict Pydantic models.
- **Task 9: Webhook Delivery & Exponential Backoff (`task.tools.webhook_retry`)**: Retry loop handling across intermittent HTTP 503 gateway responses.

### Suite 4: Structured Data Extraction (Category: `Data Extraction`)
- **Task 10: 10-K Financial Statement Balance Sheet Extraction (`task.extraction.financial_statement`)**: Precision tabular financial extraction with GAAP balance verification.
- **Task 11: Multi-Service Android Logcat Crash Isolation (`task.extraction.logcat_crash`)**: Trace stack analysis and root cause determination across distributed threads.

### Suite 5: Failure Resilience & Recovery (Category: `Failure Resilience`)
- **Task 12: Tool Execution Timeout Recovery (`task.recovery.tool_timeout`)**: Subprocess timeout handling (15s deadline) and compensatory cache fallback.
- **Task 13: Gateway Rate Limit 429 Adaptive Backoff (`task.recovery.rate_limit_backoff`)**: HTTP 429 Retry-After header parsing and delayed jitter retry.
- **Task 14: Malformed Output Schema Self-Correction (`task.recovery.schema_violation`)**: Verifier JSON-Schema validation rejection and self-correction prompt retry.

---

## 3. Controlled Fault Injection Scenarios (5 Scenarios)

1. `TOOL_TIMEOUT` (`failure.tool_timeout`): Tool execution exceeds configured threshold (15s), evaluating agent timeout detection and compensatory routing.
2. `RATE_LIMIT_429` (`failure.rate_limit_429`): Model gateway or upstream API returns HTTP 429 Too Many Requests, testing exponential backoff with jitter.
3. `SEARCH_UNAVAILABLE` (`failure.search_unavailable`): Web research tool fails with HTTP 503, testing fallback to local cached symbol indexes.
4. `NAV_TIMEOUT` (`failure.nav_timeout`): Browser page load exceeds navigation threshold (30s), testing DOM readiness recovery.
5. `SCHEMA_VIOLATION` (`failure.schema_violation`): Agent output fails strict JSON schema verification, testing reflection and regeneration.

---

## 4. Experiment Structure & Finite-Sample Metric Equations

The dataset includes **32 multi-trial experiments** with 5 to 8 trials each (~160 trials in total).

Every experiment run computes metrics directly from underlying `Trial` outcomes:

### A. Pass Rate
$$\text{Pass Rate} = \frac{\sum_{i=1}^n \mathbb{I}(\text{status}_i \in \{\text{PASSED}, \text{RECOVERED}\})}{n}$$

### B. Wilson 95% Confidence Interval
With $z = 1.959964$ and $\hat{p} = \text{Pass Rate}$:
$$\text{CI} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1 - \hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

### C. Pass@k (Unbiased Finite-Sample Estimator)
Given $n$ repeated trials and $c$ observed successes:
$$\text{Pass@}k = 1 - \frac{\binom{n - c}{k}}{\binom{n}{k}}$$

### D. Pass^k (Strict Reliability Estimator)
All $k$ trials must succeed consecutively:
$$\text{Pass}^k = \frac{\binom{c}{k}}{\binom{n}{k}}$$

### E. Recovery Rate
For trials with injected faults ($F_{\text{injected}}$):
$$\text{Recovery Rate} = \frac{\sum \mathbb{I}(\text{status} = \text{RECOVERED})}{F_{\text{injected}}}$$

