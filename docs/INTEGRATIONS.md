# Reliabench — System Integrations & Diagnostics

## 1. Harbor Framework Integration

**Repository:** `https://github.com/harbor-framework/harbor`  
**Adapter:** `backend/app/adapters/harbor/adapter.py`  
**Purpose:** Primary containerized execution runtime for evaluating autonomous AI agents in isolated Docker sandboxes.

### Operational Characteristics
- **Command Construction:** Safe subprocess argument arrays (`["harbor", "run", "-p", task_path, "-a", agent_name]`), completely eliminating shell injection vulnerabilities.
- **Availability Probe:** Inspects host for `harbor` binary and active Docker daemon.
- **Fail-Safe Simulator:** When running in environments without Docker or Harbor CLI (e.g. Vercel serverless functions), gracefully falls back to the deterministic Simulator (`source_mode='SIMULATOR'`), emitting full ATIF v1.8 trajectories without fabricating execution status.
- **Diagnostic Endpoint:** `GET /api/v1/health` reports status (`READY`, `CLI_NOT_INSTALLED`, or `DOCKER_UNAVAILABLE`).

---

## 2. Bifrost Model Gateway Integration

**Repository:** `https://github.com/maximhq/bifrost`  
**Adapter:** `backend/app/adapters/gateways/bifrost.py`  
**Purpose:** Model routing, retry/fallback management, token accounting, and microsecond-level request telemetry.

### Operational Characteristics
- **Correlation Headers:** Attaches standard `x-bf-lh-*` metadata headers (`x-bf-lh-experiment-id`, `x-bf-lh-run-id`, `x-bf-lh-trial-id`, `x-bf-lh-agent-id`, `x-bf-lh-correlation-id`) to propagate tracing across upstream model providers.
- **Telemetry Capture:** Ingests prompt tokens, completion tokens, measured latency (ms), HTTP status codes, and retry counts into the `model_request_events` table.
- **Fallback Accounting:** When provider failures trigger model fallback, records `fallback_used=True` without misclassifying provider retries as agent task failures.
- **Diagnostics:**
  - `GET /api/v1/diagnostics/bifrost`: Checks configuration and endpoint reachability.
  - `POST /api/v1/diagnostics/bifrost/test`: Executes a test probe against the configured gateway.

---

## 3. Tavily Web Research Tool Integration

**Documentation:** `https://docs.tavily.com/`  
**Adapter:** `backend/app/adapters/tools/tavily/`  
**Purpose:** External research capability for agents undergoing multi-source web search benchmarks.

### Operational Characteristics
- **Secure Secret Handling:** Reads `TAVILY_API_KEY` strictly server-side. Never exposes keys in client responses or telemetry tables.
- **Telemetry Capture:** Ingests queries, search depth, domain inclusions/exclusions, returned domains, response latency (ms), and HTTP status into the `tool_events` table.
- **Error Taxonomy:** Maps network timeouts, 401 unauthorized, and 429 rate limits to standardized taxonomy categories (`TOOL_TIMEOUT`, `TOOL_CONTRACT`, `RATE_LIMIT_429`).
- **Diagnostics:**
  - `GET /api/v1/diagnostics/tavily`: Reports API key status and total captured events.
  - `POST /api/v1/diagnostics/tavily/test`: Executes live search query probe (`"Reliabench AI Agent Benchmarking"`) to verify upstream connectivity.
