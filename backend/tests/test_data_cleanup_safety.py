import pytest
from app.db.session import SessionLocal
from app.models.entities import Agent, BenchmarkTask, Experiment, Run, Trial, Trajectory
from app.cli import clean_demo_data


def test_clean_demo_data_preserves_real_records():
    db = SessionLocal()
    try:
        # 1. Create a real user-registered agent
        real_agent = Agent(
            name="Real-Production-Agent-123",
            framework="custom",
            version="1.0.0",
            adapter_type="custom",
            source_mode="REAL_EXECUTION",
            is_demo=False
        )
        db.add(real_agent)

        # 2. Create a demo agent
        demo_agent = Agent(
            name="Demo-Mock-Agent-XYZ",
            framework="simulator",
            version="1.0.0",
            adapter_type="simulator",
            source_mode="SIMULATOR",
            is_demo=True
        )
        db.add(demo_agent)
        db.commit()

        # 3. Run dry-run cleanup
        clean_demo_data(dry_run=True)

        # Assert both still exist after dry-run
        assert db.query(Agent).filter(Agent.id == real_agent.id).first() is not None
        assert db.query(Agent).filter(Agent.id == demo_agent.id).first() is not None

        # 4. Run real cleanup
        clean_demo_data(dry_run=False)

        # Assert real agent remains intact while demo agent is safely purged
        assert db.query(Agent).filter(Agent.id == real_agent.id).first() is not None
        assert db.query(Agent).filter(Agent.id == demo_agent.id).first() is None

    finally:
        # Cleanup test fixture
        db.query(Agent).filter(Agent.name == "Real-Production-Agent-123").delete()
        db.commit()
        db.close()
