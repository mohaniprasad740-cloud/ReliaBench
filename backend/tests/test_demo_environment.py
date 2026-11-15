import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.entities import Agent, BenchmarkTask, FailureScenario, Experiment, Run, Trial, Trajectory
from app.services.demo_seed import seed_demo_data, reset_demo_data, clean_existing_demo_records

client = TestClient(app)


def test_demo_seed_and_mathematical_consistency():
    """Verify demo seed populates canonical dataset with exact mathematical consistency."""
    with SessionLocal() as db:
        res = seed_demo_data(db, force_reset=True)
        assert res["status"] in ("SUCCESS", "ALREADY_SEEDED")

        # 1. Verify Agents
        agents = db.query(Agent).filter(Agent.is_demo == True).all()
        assert len(agents) == 4
        agent_names = {a.name for a in agents}
        assert "Atlas Research Agent" in agent_names
        assert "Nova Browser Agent" in agent_names
        assert "Sentinel Workflow Agent" in agent_names
        assert "Swift Assistant" in agent_names

        for a in agents:
            assert a.source_mode == "SIMULATOR"
            assert a.is_demo is True

        # 2. Verify Benchmark Tasks
        tasks = db.query(BenchmarkTask).filter(BenchmarkTask.is_demo == True).all()
        assert len(tasks) == 14
        categories = {t.category for t in tasks}
        assert "Web Research" in categories
        assert "Browser Automation" in categories
        assert "Tool Execution" in categories
        assert "Data Extraction" in categories
        assert "Failure Resilience" in categories

        # 3. Verify Experiments and Finite-Sample Metrics Consistency
        experiments = db.query(Experiment).filter(Experiment.is_demo == True).all()
        assert len(experiments) >= 32

        for exp in experiments:
            assert exp.is_demo is True
            assert exp.source_mode == "SIMULATOR"
            assert len(exp.runs) >= 1
            run = exp.runs[0]
            assert run.total_trials in (5, 8)
            assert run.successful_trials + run.failed_trials == run.total_trials

            # Mathematical checks: Pass Rate = successful_trials / total_trials
            expected_pass_rate = round(run.successful_trials / run.total_trials, 3)
            assert abs(run.pass_rate - expected_pass_rate) < 1e-4

            # Wilson Score interval bounds
            if run.successful_trials > 0 and run.failed_trials > 0:
                assert run.ci_lower < run.pass_rate < run.ci_upper
            assert 0.0 <= run.ci_lower <= 1.0
            assert 0.0 <= run.ci_upper <= 1.0

            # Pass@k and Pass^k bounds
            assert 0.0 <= run.pass_at_k <= 1.0
            assert 0.0 <= run.pass_to_k <= 1.0
            assert run.pass_to_k <= run.pass_at_k  # Pass^k is always <= Pass@k

            # Trajectory schema and persistence
            for trial in run.trials:
                assert trial.trajectory is not None
                assert trial.trajectory.atif_version == "ATIF-v1.8"
                assert isinstance(trial.trajectory.summary_steps, list)
                assert len(trial.trajectory.summary_steps) >= 3


def test_demo_idempotency():
    """Calling seed_demo_data multiple times produces no duplicates."""
    with SessionLocal() as db:
        res1 = seed_demo_data(db, force_reset=False)
        count_exps_1 = db.query(Experiment).filter(Experiment.is_demo == True).count()

        res2 = seed_demo_data(db, force_reset=False)
        assert res2["status"] in ("SUCCESS", "ALREADY_SEEDED")
        count_exps_2 = db.query(Experiment).filter(Experiment.is_demo == True).count()

        assert count_exps_1 == count_exps_2 >= 32


def test_demo_reset_safety():
    """Resetting demo dataset purges demo data without touching user experiments."""
    with SessionLocal() as db:
        # Create user-owned test agent and experiment
        user_agent = Agent(
            name="Prod-User-Agent-Safety-Test",
            framework="langchain",
            version="2.0.0",
            adapter_type="custom",
            source_mode="REAL_EXECUTION",
            is_demo=False
        )
        db.add(user_agent)
        db.flush()

        demo_task = db.query(BenchmarkTask).first()
        user_exp = Experiment(
            title="User Safety Experiment Keep Me",
            agent_id=user_agent.id,
            benchmark_task_id=demo_task.id,
            repetitions_k=3,
            source_mode="REAL_EXECUTION",
            is_demo=False
        )
        db.add(user_exp)
        db.commit()

        user_exp_id = user_exp.id
        user_agent_id = user_agent.id

        try:
            # Trigger reset
            res = reset_demo_data(db)
            assert res["status"] in ("SUCCESS", "ALREADY_SEEDED")

            # Verify user record is untouched
            preserved_exp = db.query(Experiment).filter(Experiment.id == user_exp_id).first()
            assert preserved_exp is not None
            assert preserved_exp.title == "User Safety Experiment Keep Me"
            assert preserved_exp.is_demo is False

            preserved_agent = db.query(Agent).filter(Agent.id == user_agent_id).first()
            assert preserved_agent is not None
            assert preserved_agent.is_demo is False
        finally:
            # Cleanup user fixtures
            db.query(Experiment).filter(Experiment.id == user_exp_id).delete()
            db.query(Agent).filter(Agent.id == user_agent_id).delete()
            db.commit()


def test_demo_api_endpoints():
    """Verify demo endpoints via HTTP API."""
    # 1. GET /api/v1/demo/status
    res = client.get("/api/v1/demo/status")
    assert res.status_code == 200
    status_data = res.json()
    assert status_data["mode"] == "DEMO_ENVIRONMENT"
    assert status_data["agents_count"] == 4
    assert status_data["tasks_count"] == 14
    assert status_data["experiments_count"] >= 32
    assert status_data["seeded"] is True
    assert "Atlas Research Agent" in status_data["canonical_agents"]

    # 2. Filtering by is_demo
    demo_res = client.get("/api/v1/experiments?is_demo=true")
    assert demo_res.status_code == 200
    demo_exps = demo_res.json()
    assert len(demo_exps) >= 32
    assert all(e["is_demo"] is True for e in demo_exps)

    # 3. POST /api/v1/demo/seed (idempotent)
    seed_res = client.post("/api/v1/demo/seed")
    assert seed_res.status_code == 200
    assert seed_res.json()["status"] in ("SUCCESS", "ALREADY_SEEDED")

    # 4. POST /api/v1/demo/reset
    reset_res = client.post("/api/v1/demo/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] in ("SUCCESS", "ALREADY_SEEDED")
