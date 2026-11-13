import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.entities import Agent, BenchmarkTask, Experiment, Run, Trial

client = TestClient(app)


def test_export_run_json_and_csv_isolated():
    """Explicitly creates an isolated experiment and run to test export without relying on demo seeds."""
    db = SessionLocal()
    try:
        agent = Agent(
            name="Export-Test-Agent",
            framework="custom",
            version="1.0.0",
            adapter_type="simulator",
            status="VALIDATED",
            source_mode="REAL_EXECUTION",
            is_demo=False
        )
        task = BenchmarkTask(
            name="Export Verification Task",
            version="1.0.0",
            category="Testing",
            difficulty="EASY",
            description="Task to test export functionality",
            instruction="Run verifier",
            expected_outcome="Pass",
            verification_method="ASSERTION_SCRIPT",
            source_mode="REAL_EXECUTION",
            is_demo=False
        )
        db.add_all([agent, task])
        db.commit()

        exp = Experiment(
            title="Export Test Experiment",
            agent_id=agent.id,
            benchmark_task_id=task.id,
            repetitions_k=1,
            timeout_seconds=60,
            status="COMPLETED",
            source_mode="REAL_EXECUTION",
            is_demo=False
        )
        db.add(exp)
        db.commit()

        run = Run(
            experiment_id=exp.id,
            total_trials=1,
            successful_trials=1,
            failed_trials=0,
            pass_rate=1.0,
            status="COMPLETED",
            source_mode="REAL_EXECUTION"
        )
        db.add(run)
        db.commit()

        trial = Trial(
            run_id=run.id,
            trial_number=1,
            status="PASSED",
            reward_score=1.0,
            duration_seconds=5.0,
            failure_injected=False,
            failure_recovered=False,
            source_mode="REAL_EXECUTION"
        )
        db.add(trial)
        db.commit()
        run_id = run.id

        # 1. Test Export JSON
        exp_json = client.get(f"/api/v1/runs/{run_id}/export?format=json")
        assert exp_json.status_code == 200
        data = exp_json.json()
        assert data["run_id"] == run_id
        assert "trials" in data
        assert data["source_mode"] == "REAL_EXECUTION"

        # 2. Test Export CSV
        exp_csv = client.get(f"/api/v1/runs/{run_id}/export?format=csv")
        assert exp_csv.status_code == 200
        assert exp_csv.headers["content-type"].startswith("text/csv")
        csv_text = exp_csv.text
        assert "run_id,trial_number,status" in csv_text
        assert str(run_id) in csv_text

    finally:
        # Clean up
        db.query(Trial).filter(Trial.run_id == run.id).delete()
        db.query(Run).filter(Run.id == run.id).delete()
        db.query(Experiment).filter(Experiment.id == exp.id).delete()
        db.query(BenchmarkTask).filter(BenchmarkTask.id == task.id).delete()
        db.query(Agent).filter(Agent.id == agent.id).delete()
        db.commit()
        db.close()


def test_regression_run_all_summary_endpoint():
    # Calling run-all when store is empty returns 0
    resp_empty = client.post("/api/v1/regressions/run-all?target_agent=fragile")
    assert resp_empty.status_code == 200
    assert resp_empty.json()["total"] == 0

    # Add a case dynamically and run
    from app.api.routes.reliability import regression_store
    case = regression_store.seed_fixture_case()

    resp = client.post("/api/v1/regressions/run-all?target_agent=fragile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert data["still_failing"] >= 1
    assert data["fixed"] == 0

    # Clean up test case
    regression_store._cases.clear()
