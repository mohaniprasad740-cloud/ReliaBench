import os
import tempfile
import pytest
from sqlalchemy import create_engine, inspect
from app.db.session import Base
from app.db.migrations import run_additive_migrations
from app.models.entities import Agent, BenchmarkTask, FailureScenario, Experiment, Run, Trial, Trajectory


def test_fresh_database_bootstrap_and_schema():
    """Verify that a brand new SQLite database initializes with all tables and columns without errors."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        test_engine = create_engine(f"sqlite:///{tmp_path}")
        # 1. Base create_all
        Base.metadata.create_all(bind=test_engine)

        # 2. Additive migrations
        run_additive_migrations(test_engine)

        # 3. Assert tables exist
        inspector = inspect(test_engine)
        table_names = set(inspector.get_table_names())
        expected_tables = {
            "agents",
            "benchmark_tasks",
            "failure_scenarios",
            "experiments",
            "runs",
            "trials",
            "trajectories",
        }
        assert expected_tables.issubset(table_names)

        # 4. Assert additive columns exist
        runs_cols = {c["name"] for c in inspector.get_columns("runs")}
        assert "taxonomy_counts" in runs_cols
        assert "remediation_hints" in runs_cols

        trials_cols = {c["name"] for c in inspector.get_columns("trials")}
        assert "taxonomy_category" in trials_cols
        assert "cost_usd" in trials_cols
        assert "prompt_tokens" in trials_cols
    finally:
        test_engine.dispose()
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
