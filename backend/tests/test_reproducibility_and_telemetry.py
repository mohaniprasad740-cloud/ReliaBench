import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.entities import Agent, BenchmarkTask, Experiment, Run, Trial, ToolEvent, ModelRequestEvent

client = TestClient(app)

def test_immutable_config_snapshot_and_reproduce():
    db = SessionLocal()
    agent = Agent(name="Test Reproduce Agent", framework="custom", version="1.2.0")
    task = BenchmarkTask(name="Test Reproduce Task", description="Testing snapshot", instruction="Echo 1", expected_outcome="1")
    db.add(agent)
    db.add(task)
    db.commit()
    db.refresh(agent)
    db.refresh(task)
    agent_id = agent.id
    task_id = task.id
    db.close()

    try:
        # Create experiment via API
        payload = {
            "title": "Config Snapshot Baseline",
            "description": "Validating immutable snapshot",
            "agent_id": agent_id,
            "benchmark_task_id": task_id,
            "repetitions_k": 3,
            "timeout_seconds": 60
        }
        res = client.post("/api/v1/experiments", json=payload)
        assert res.status_code == 201
        exp_data = res.json()
        exp_id = exp_data["id"]

        # Verify snapshot
        snapshot = exp_data.get("config_snapshot")
        assert snapshot is not None
        assert snapshot["agent"]["name"] == "Test Reproduce Agent"
        assert snapshot["agent"]["version"] == "1.2.0"
        assert snapshot["benchmark_task"]["name"] == "Test Reproduce Task"
        assert snapshot["repetitions_k"] == 3

        # Reproduce experiment via API
        rep_res = client.post(f"/api/v1/experiments/{exp_id}/reproduce")
        assert rep_res.status_code == 201
        rep_data = rep_res.json()
        assert rep_data["id"] != exp_id
        assert "(Reproduced" in rep_data["title"]
        assert rep_data["config_snapshot"]["agent"]["name"] == "Test Reproduce Agent"
    finally:
        clean_db = SessionLocal()
        for e in clean_db.query(Experiment).filter(Experiment.agent_id == agent_id).all():
            clean_db.delete(e)
        a = clean_db.query(Agent).filter(Agent.id == agent_id).first()
        if a:
            clean_db.delete(a)
        t = clean_db.query(BenchmarkTask).filter(BenchmarkTask.id == task_id).first()
        if t:
            clean_db.delete(t)
        clean_db.commit()
        clean_db.close()

def test_unified_telemetry_persistence_and_events_api():
    db = SessionLocal()
    agent = Agent(name="Telemetry Agent", framework="custom", version="2.0.0")
    task = BenchmarkTask(name="Tavily Web Search Task", category="web_research_tavily", description="Search web", instruction="Find latest AI research", expected_outcome="Results")
    db.add(agent)
    db.add(task)
    db.commit()
    db.refresh(agent)
    db.refresh(task)
    agent_id = agent.id
    task_id = task.id

    exp_id = None
    try:
        # Create experiment
        exp = Experiment(
            title="Telemetry Pipeline Experiment",
            agent_id=agent.id,
            benchmark_task_id=task.id,
            repetitions_k=2,
            status="RUNNING"
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)
        exp_id = exp.id

        run = Run(experiment_id=exp.id, total_trials=2, successful_trials=2)
        db.add(run)
        db.commit()
        db.refresh(run)

        trial1 = Trial(run_id=run.id, trial_number=1, status="PASSED", duration_seconds=1.2)
        trial2 = Trial(run_id=run.id, trial_number=2, status="PASSED", duration_seconds=1.4)
        db.add(trial1)
        db.add(trial2)
        db.commit()
        db.refresh(trial1)
        db.refresh(trial2)

        # Add ToolEvents
        tev1 = ToolEvent(
            trial_id=trial1.id,
            tool_name="tavily_search",
            tool_call_id="call_001",
            args={"query": "AI research"},
            observation="Search results found",
            is_error=False,
            latency_ms=210.0,
            source="TAVILY"
        )
        tev2 = ToolEvent(
            trial_id=trial2.id,
            tool_name="tavily_search",
            tool_call_id="call_002",
            args={"query": "Reliability metrics"},
            observation="Metrics found",
            is_error=False,
            latency_ms=195.0,
            source="TAVILY"
        )
        db.add(tev1)
        db.add(tev2)

        # Add ModelRequestEvents
        mev1 = ModelRequestEvent(
            trial_id=trial1.id,
            correlation_id=f"corr_{exp.id[:8]}_{trial1.id[:8]}",
            provider="bifrost",
            model="claude-3-7-sonnet",
            prompt_tokens=400,
            completion_tokens=60,
            total_tokens=460,
            cost_usd=0.0012,
            latency_ms=450.0
        )
        mev2 = ModelRequestEvent(
            trial_id=trial2.id,
            correlation_id=f"corr_{exp.id[:8]}_{trial2.id[:8]}",
            provider="bifrost",
            model="claude-3-7-sonnet",
            prompt_tokens=420,
            completion_tokens=70,
            total_tokens=490,
            cost_usd=0.0013,
            latency_ms=480.0
        )
        db.add(mev1)
        db.add(mev2)
        db.commit()
        t1_id = trial1.id
        t2_id = trial2.id
        r_id = run.id
        db.close()

        # Query events API
        res = client.get(f"/api/v1/experiments/{exp_id}/events")
        assert res.status_code == 200
        data = res.json()
        assert data["experiment_id"] == exp_id
        assert data["total_events"] == 4
        event_types = [e["event_type"] for e in data["events"]]
        assert "MODEL_REQUEST" in event_types
        assert "TOOL_CALL" in event_types
    finally:
        clean_db = SessionLocal()
        if exp_id:
            e = clean_db.query(Experiment).filter(Experiment.id == exp_id).first()
            if e:
                clean_db.delete(e)
        a = clean_db.query(Agent).filter(Agent.id == agent_id).first()
        if a:
            clean_db.delete(a)
        t = clean_db.query(BenchmarkTask).filter(BenchmarkTask.id == task_id).first()
        if t:
            clean_db.delete(t)
        clean_db.commit()
        clean_db.close()
