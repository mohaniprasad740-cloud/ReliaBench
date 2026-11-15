# Reliabench Demo Video Walkthrough & Presentation Script

This script is designed for team members recording a 3–5 minute product pitch video using the live deployed website without requiring external API keys.

---

## Act 1: The Hook & Landing Page (0:00 – 0:45)

### Screen: Landing Page (`/`)
1. **Show the Editorial Headline**:
   > *"Most AI benchmarks test whether an agent can pass a task once. In production, that is not reliability. An agent that passes once and crashes on the next 7 attempts has an 87.5% failure rate."*
2. **Interact with the Trial Matrix Simulator**:
   - Click several trial boxes on the interactive matrix to cycle states (`PASSED`, `FAILED`, `RECOVERED`, `TIMEOUT`).
   - Point out how the live pass rate, recovery count, and Wilson confidence intervals update.
3. **Show the Production Demo Ready Banner**:
   - Highlight the banner: 4 canonical agents, 14 benchmark tasks, 32 multi-trial experiments, 160 real ATIF traces.
   - Click **"Explore Demo"** to transition to `/app`.

---

## Act 2: Dashboard Overview & Guided Tour (0:45 – 1:30)

### Screen: Dashboard (`/app`)
1. **Show the Persistent Header Badge**:
   - Point to `DEMO ENVIRONMENT · CANONICAL DATA`. Mention that all evidence is pre-populated and mathematically verifiable.
2. **Review the Aggregate Reliability Metrics Strip**:
   - Total Experiments: 32 executed.
   - Overall Pass Rate with Wilson 95% Confidence Intervals.
   - P50, P90, P95 duration spreads and average cost per successful outcome.
3. **Launch the Guided Product Tour**:
   - Click the **"Product Tour"** button in the header.
   - Click **"Next"** through 2–3 steps to show the dark overlay spotlight effect, positioning engine, and cross-page navigation.
   - Click **"Skip Tour"** to resume manual navigation.

---

## Act 3: Agent Registry & Multi-Framework Profiles (1:30 – 2:15)

### Screen: Agent Registry (`/app/agents`)
1. **Show the 4 Canonical Agent Profiles**:
   - **Atlas Research Agent**: LangGraph + GPT-4o for deep technical web research.
   - **Nova Browser Agent**: Browser-Use + Claude 3.7 Sonnet for multi-step DOM automation.
   - **Sentinel Workflow Agent**: CrewAI + GPT-4o-mini for multi-tool calling and fault recovery.
   - **Swift Assistant**: Custom Haiku pipeline for high-throughput structured data extraction.
2. **Highlight Framework Independence**:
   - Point out that Reliabench evaluates agents through standardized harness contracts (HTTP, CLI, and Harbor container interfaces).

---

## Act 4: Deep Dive into Execution Traces & ATIF Telemetry (2:15 – 3:15)

### Screen: Experiment Detail & Trial View (`/app/experiments/{id}`)
1. **Open an Experiment with Fault Injection**:
   - Select an experiment evaluating `Sentinel Workflow Agent` on `Tool Execution Timeout Recovery` with `TOOL_TIMEOUT` injected.
2. **Show the Trial Outcome Strip**:
   - Show the 5 repeated trials (e.g. 4 RECOVERED, 1 FAILED).
   - Show how Recovery Rate (80.0%) and Pass@k vs Pass^k are computed.
3. **Inspect the ATIF v1.8 Execution Trajectory**:
   - Open Trial #1.
   - Show step-by-step reasoning, primary tool call timeout at 15 seconds, and subsequent compensatory cache fallback execution.
4. **Show Unified Telemetry Records**:
   - Point out `ModelRequestEvent` with token counts and latency.
   - Point out `ToolEvent` capturing exact tool arguments and error payloads.

---

## Act 5: Agent Comparisons & Benchmark Reports (3:15 – 4:00)

### Screen: Comparisons (`/app/comparisons`)
1. **Side-by-Side Agent Comparison**:
   - Compare **Atlas Research Agent** vs **Nova Browser Agent** on multi-step research.
   - Contrast pass rate variance, execution duration spreads, and cost efficiency.
2. **Reports Page (`/app/reports`)**:
   - Show generated benchmark summary tables.
   - Click **Export JSON** or **Export CSV** to demonstrate scientific auditability.
3. **Conclusion & Value Proposition**:
   > *"Same tasks. Same conditions. Measurable agent reliability. Reliabench gives engineering teams the rigor to deploy autonomous agents with statistical confidence."*

