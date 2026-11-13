# RELIABENCH — CLEAN-STATE ARCHITECTURE & DATA AUDIT
**Date**: November 2026
**Project**: Reliabench (Global AI Hackathon | PS02: AI Agent Benchmarking Platform)
**Objective**: Eliminate automatically generated demo records, synthetic historical activity, and seeded showcase data while preserving real benchmarking engines, challenge packs, and deterministic harness tools.

---

## 1. Inventory of Automatically Generated Records & Seeds

### 1.1 Startup Seeding Mechanism
- **File**: `backend/app/main.py`
  - Lines 6 & 14-16:
    ```python
    from app.services.demo_seed import seed_demo_data_if_empty
    ...
    with SessionLocal() as db:
        seed_demo_data_if_empty(db)
    ```
  - **Issue**: Runs on every application startup if SQLite DB is empty, fabricating 4 agents (`Devin-Reference-v2`, `Claude-Code-Engine`, `AutoGPT-Loop-Ref`, `Gemini-CodeAgent`), 4 synthetic benchmark task records, 4 failure scenario DB records, 4 experiments with 12 completed trials, and generating 12 synthetic ATIF trajectory JSON files into `artifacts/trajectories/`.

### 1.2 Demonstration Seed Service
- **File**: `backend/app/services/demo_seed.py`
  - Defines `DEMO_AGENTS`, `DEMO_BENCHMARKS`, `DEMO_FAILURES`, and `seed_demo_data_if_empty(db)`.
  - Generates fake timestamps, fake durations, fabricated token counts, fake dollar costs (`random.uniform(0.0015, 0.0042)`), and synthetic `trial_*.json` ATIF files.

### 1.3 Pre-Generated Artifacts in Repository
- **Directory**: `artifacts/trajectories/`
  - Contains 36 synthetic trajectory JSON files (`trial_*.json`) generated during previous demo runs and seeds.
  - None of these are from actual executions of external agents; they are synthetic mock payloads.

### 1.4 Hardcoded Default Regression Case
- **File**: `backend/app/services/regression.py`
  - Lines 34-49: `_seed_default_cases()` creates a pre-populated case `reg-flaky-triage-tool-contract`.
  - Causes the regression page to show a pre-existing failure history on a fresh install.

### 1.5 Built-In Failure Scenario Catalog
- Currently, `GET /api/v1/failures` queries the database table `FailureScenario`.
- When database seeding is removed, the DB table is empty.
- However, failure scenarios are **system capabilities / taxonomy definitions**, not historical data.
- They must be provided via a built-in scenario catalog (derived from `FaultKind` and `TaxonomyClassifier`) rather than relying on seeded DB records.

---

## 2. Test Suite Dependencies on Seeded Data

1. **`backend/tests/test_exports_and_run_all.py`**:
   - `test_export_run_json()` and `test_export_run_csv()` assume `client.get("/api/v1/experiments")` returns at least one pre-seeded run.
   - **Remediation**: Use a test fixture or explicitly execute an experiment/trial within the test before asserting export endpoints.
2. **`backend/tests/test_api.py`**:
   - `test_dashboard_summary()` asserts `data["total_agents"] >= 1` and `data["total_benchmarks"] >= 1`.
   - `test_benchmarks_list()` and `test_failures_list()` assert `len(res.json()) >= 1`.
   - **Remediation**: Update assertions for clean-state semantics (e.g. `total_agents == 0` on fresh DB, or create explicit test records in test setup), and ensure `failures` returns the built-in system catalog.
3. **`backend/tests/test_regressions.py` & `backend/tests/test_reliability_api.py`**:
   - Asserts `len(cases) >= 1` because of `_seed_default_cases()`.
   - **Remediation**: Keep default cases as an explicit test helper or create a test fixture case in tests, while production `RegressionStore` starts empty.

---

## 3. Frontend Pages & Missing Empty States

1. **`DashboardPage.tsx`**:
   - Shows empty chart gracefully when `total_experiments == 0`, but needs a dedicated clean "Get Started" onboarding card when no experiments or agents exist.
2. **`AgentsPage.tsx`**:
   - Currently shows empty grid when `agents.length === 0`. Needs an explicit Empty State banner with action button.
3. **`ExperimentsPage.tsx`**:
   - Needs an empty state when `experiments.length === 0`.
4. **`TracesPage.tsx`**:
   - Shows an empty message when no run exists. Needs clear instructions that traces are recorded on experiment execution.
5. **`ComparisonsPage.tsx`**:
   - Needs an empty state explaining that at least 2 experiments are needed.
6. **`ReportsPage.tsx`**:
   - Needs an empty state when no experiments exist.
7. **`RegressionsPage.tsx`**:
   - Needs an empty state when no regression cases are recorded.

---

## 4. Preserved Capabilities (Do NOT Delete)

- `backend/app/faults/engine.py`: Deterministic PRNG fault injection engine (`seed`, `at_step`, `probability`, `kind`).
- `backend/app/agents/reference.py`: Deterministic harness profiles (`fragile`, `retrying`, `resilient`).
- `backend/app/benchmarks/pack.py`: Curated YAML challenge packs in `benchmark_tasks/packs/` (6 packs: `flaky_test_triage`, `order_discount_rounding`, `memory_leak_investigation`, `auth_token_refresh`, `db_deadlock_recovery`, `circuit_breaker_recovery`).
- `backend/app/evaluation/taxonomy.py`: Standardized failure taxonomy (8 categories) with remediation hints.
- `backend/app/evaluation/metrics.py`: Mathematical evaluation formulas (Pass Rate, Wilson CI, Pass@k, Pass^k, Recovery Rate).
- `backend/app/adapters/harbor/adapter.py`: Harbor CLI v0.25.0 subprocess execution wrapper.
- `backend/app/adapters/gateways/bifrost.py`: Bifrost model gateway adapter.

---

## 5. Step-by-Step Cleanup Plan

1. **Remove Startup Seeding**:
   - Remove `seed_demo_data_if_empty` invocation from `backend/app/main.py`.
   - Remove `backend/app/services/demo_seed.py`.
2. **Built-in Failure Scenario Catalog**:
   - Expose the failure scenarios directly from the built-in system definitions (built on `FaultKind` and `TaxonomyClassifier`) so `/api/v1/failures` returns available fault injection capabilities even with an empty DB.
3. **Regression Store Clean State**:
   - Remove `_seed_default_cases()` from `RegressionStore.__init__`. Allow `seed_default_case()` for tests.
4. **CLI Cleanup Command**:
   - Create `backend/app/cli.py` with `clean-demo-data` command (including `--dry-run` and live cleanup of `is_demo=True` records and orphaned synthetic files).
5. **Clean Local Storage**:
   - Remove synthetic trajectory files from `artifacts/trajectories/`.
   - Clean or reset local SQLite database `reliabench.db` to 0 agents, 0 experiments, 0 trials, 0 runs.
6. **Update Test Suites**:
   - Refactor `test_exports_and_run_all.py`, `test_api.py`, `test_regressions.py`, and `test_reliability_api.py` to create their own isolated test fixtures.
7. **Frontend Empty States & Polish**:
   - Update `DashboardPage`, `AgentsPage`, `ExperimentsPage`, `TracesPage`, `ComparisonsPage`, `ReportsPage`, and `RegressionsPage` with clean empty states.
8. **Validation & Verification**:
   - Verify all tests pass.
   - Verify fresh database contains 0 agents, 0 experiments, 0 runs.
   - Verify explicit execution of an experiment or pack generates real trials and ATIF trajectories dynamically.

