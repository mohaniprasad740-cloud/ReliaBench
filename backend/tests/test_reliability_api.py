from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_list_packs():
    resp = client.get("/api/v1/packs")
    assert resp.status_code == 200
    packs = resp.json()
    assert len(packs) >= 6
    pack_ids = {p["id"] for p in packs}
    assert "flaky_test_triage" in pack_ids


def test_api_get_pack_detail():
    resp = client.get("/api/v1/packs/flaky_test_triage")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "flaky_test_triage"
    assert len(data["plan"]) == 3


def test_api_get_pack_404():
    resp = client.get("/api/v1/packs/non_existent_pack_xyz")
    assert resp.status_code == 404


def test_api_run_pack_endpoint():
    payload = {
        "profile": "fragile",
        "k": 2,
        "seed": 42,
        "fault_kind": "TOOL_ERROR",
        "at_step": 3,
        "tool": "update_quarantine_config",
        "probability": 1.0,
    }
    resp = client.post("/api/v1/packs/flaky_test_triage/run", json=payload)
    assert resp.status_code == 200
    sc = resp.json()
    assert sc["pass_rate"] == 0.0
    assert sc["taxonomy_counts"]["TOOL_CONTRACT"] == 2


def test_api_taxonomy_endpoint():
    resp = client.get("/api/v1/taxonomy")
    assert resp.status_code == 200
    data = resp.json()
    assert "TIMEOUT" in data["categories"]
    assert "priority_order" in data


def test_api_regression_endpoints_empty_by_default():
    """RegressionStore starts empty — no seeded cases in clean state."""
    resp = client.get("/api/v1/regressions")
    assert resp.status_code == 200
    cases = resp.json()
    assert isinstance(cases, list)
    assert len(cases) == 0


def test_api_regression_seed_and_replay():
    """Seed a fixture case explicitly then verify replay works."""
    from app.api.routes.reliability import regression_store

    # Seed a test fixture case
    case = regression_store.seed_fixture_case()
    case_id = case.id

    try:
        # Verify it appears in the list
        resp = client.get("/api/v1/regressions")
        assert resp.status_code == 200
        cases = resp.json()
        assert len(cases) >= 1

        # Replay with fragile -> STILL_FAILING
        r1 = client.post(f"/api/v1/regressions/{case_id}/replay?runner_agent=fragile")
        assert r1.status_code == 200
        assert r1.json()["status"] == "STILL_FAILING"

        # Replay with resilient -> FIXED
        r2 = client.post(f"/api/v1/regressions/{case_id}/replay?runner_agent=resilient")
        assert r2.status_code == 200
        assert r2.json()["status"] == "FIXED"
    finally:
        # Clean up the seeded case so it doesn't pollute other tests
        regression_store._cases.pop(case_id, None)
