# Reliabench — Experiment Reproducibility & Configuration Immutability

## 1. Principles of Reproducibility

Scientific evaluation of AI agents requires that historical experiment evidence cannot be rewritten when an agent's prompt, model, or benchmark task definition is updated. Reliabench enforces strict configuration immutability:

1. **Frozen Snapshot at Creation**: When an experiment is created via `POST /api/v1/experiments`, a complete `config_snapshot` JSON object is generated and persisted in the database.
2. **Version Isolation**: Edits to an agent's version, framework, model, or instructions do not alter prior experiment records.
3. **Deterministic Seeds**: Random seeds are captured and used by the fault injection engine to ensure reproducible fault schedules.
4. **Distinction between Stochastic and Exact Replay**: LLM non-determinism is acknowledged; while model sampling involves temperature, execution preconditions, tool arguments, fault injections, and verification criteria are completely deterministic.

---

## 2. Configuration Snapshot Schema

Stored in `experiments.config_snapshot`:

```json
{
  "title": "Agent Resilience Baseline",
  "description": "Evaluating fallback under tool error",
  "repetitions_k": 3,
  "timeout_seconds": 180,
  "seed": 42,
  "snapshot_timestamp": "2026-11-13T16:20:00Z",
  "agent": {
    "id": "agent-uuid",
    "name": "Resilient-Reference-Agent",
    "version": "1.0.0",
    "framework": "custom",
    "adapter_type": "simulator",
    "model_provider": "anthropic",
    "model_name": "claude-3-7-sonnet",
    "endpoint_url": null,
    "source_mode": "SIMULATOR"
  },
  "benchmark_task": {
    "id": "task-uuid",
    "name": "Web Research under Rate Limit",
    "version": "1.0.0",
    "category": "web_research_tavily",
    "difficulty": "MEDIUM",
    "verification_method": "ASSERTION_SCRIPT",
    "time_limit_seconds": 120,
    "environment_type": "DOCKER_SANDBOX",
    "instruction": "Research latest findings and format findings...",
    "expected_outcome": "Synthesized markdown report"
  },
  "failure_scenario": {
    "id": "scenario-uuid",
    "name": "HTTP 429 Rate Limit",
    "code": "RATE_LIMIT_429",
    "trigger_point": "TOOL_CALL",
    "severity": "HIGH",
    "parameters": {
      "retry_after_seconds": 2,
      "max_retries": 3
    }
  },
  "integrations": {
    "bifrost_enabled": false,
    "bifrost_endpoint": "http://localhost:8080/v1",
    "tavily_configured": true,
    "harbor_required_version": "v0.25.0"
  }
}
```

---

## 3. Reproduction Workflow

Users can reproduce any completed or historical experiment directly via the API or UI:

### Endpoint: `POST /api/v1/experiments/{experiment_id}/reproduce`
- Fetches the original immutable `config_snapshot`.
- Instantiates a new experiment titled `"{original_title} (Reproduced #{hash})"`.
- Preserves identical task preconditions, repetition count $k$, seed, and failure parameters.
- Queues the new experiment for execution.
