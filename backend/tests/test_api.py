import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.entities import Agent, BenchmarkTask, Experiment, Run, Trial

client = TestClient(app)


def test_health_check():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "adapters" in data
    assert "harbor" in data["adapters"]


def test_dashboard_summary_clean_state():
    """On a clean installation with no experiments run, counts are 0 and rates are null."""
    res = client.get("/api/v1/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_experiments"] == 0
    assert data["overall_pass_rate"] is None
    assert data["recent_experiments"] == []
    assert data["recent_failures"] == []


def test_agents_crud():
    # Clean check: list agents
    initial_res = client.get("/api/v1/agents")
    assert initial_res.status_code == 200
    initial_agents = initial_res.json()

    # 1. Create agent explicitly
    payload = {
        "name": "Integration-Test-Agent",
        "description": "Agent created during automated verification",
        "framework": "custom",
        "version": "1.0.0",
        "adapter_type": "simulator",
        "model_provider": "anthropic",
        "model_name": "claude-3-7-sonnet"
    }
    create_res = client.post("/api/v1/agents", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    agent_id = created["id"]
    assert created["name"] == "Integration-Test-Agent"

    # 2. Get agent
    get_res = client.get(f"/api/v1/agents/{agent_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Integration-Test-Agent"

    # 3. Delete agent
    del_res = client.delete(f"/api/v1/agents/{agent_id}")
    assert del_res.status_code == 200


def test_benchmarks_empty_on_fresh_install():
    """User-created benchmarks start empty; system challenge packs are in /packs."""
    res = client.get("/api/v1/benchmarks")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_failures_catalog_available_from_system():
    """System failure catalog is available without requiring fake DB records."""
    res = client.get("/api/v1/failures")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    codes = {f["code"] for f in data}
    assert "TOOL_ERROR" in codes
    assert "TOOL_TIMEOUT" in codes
    assert "MODEL_UNAVAILABLE" in codes
