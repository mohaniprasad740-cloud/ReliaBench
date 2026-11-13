import pytest
from app.benchmarks.pack import list_packs, load_pack_from_file


def test_load_all_challenge_packs():
    packs = list_packs("benchmark_tasks/packs")
    assert len(packs) >= 6
    pack_ids = {p.id for p in packs}
    assert "tavily_docs_research" in pack_ids
    assert "tavily_failure_recovery" in pack_ids
    pack_ids = {p.id for p in packs}
    expected = {
        "flaky_test_triage",
        "rate_limit_backoff",
        "config_migration",
        "django_csrf_patch",
        "pandas_aggregation",
        "sql_model_refactor",
    }
    assert expected.issubset(pack_ids)


def test_pack_schema_and_preconditions():
    pack = load_pack_from_file("benchmark_tasks/packs/flaky_test_triage.yaml")
    assert pack.id == "flaky_test_triage"
    assert len(pack.tools) == 3
    assert len(pack.plan) == 3
    assert pack.plan[0].requires is None
    assert pack.plan[1].requires == "Found intermittent failure in test_session_expiry"
    assert len(pack.validators) >= 2


def test_pack_validators_structure():
    pack = load_pack_from_file("benchmark_tasks/packs/rate_limit_backoff.yaml")
    types = [v.type for v in pack.validators]
    assert "tool_called" in types
    assert "observation_contains" in types
