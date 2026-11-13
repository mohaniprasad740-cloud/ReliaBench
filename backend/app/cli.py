"""CLI tool for Reliabench maintenance and data cleanup operations."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.models.entities import Agent, BenchmarkTask, Experiment, Run, Trial, Trajectory, FailureScenario


def clean_demo_data(dry_run: bool = False) -> None:
    """Finds all records flagged as is_demo=True, their associated runs/trials/trajectories,
    and synthetic artifact files, and safely removes them while preserving user records.
    """
    print(f"=== Reliabench Data Cleanup (dry_run={dry_run}) ===")
    
    with SessionLocal() as db:
        demo_agents = db.query(Agent).filter(Agent.is_demo == True).all()
        demo_tasks = db.query(BenchmarkTask).filter(BenchmarkTask.is_demo == True).all()
        demo_exps = db.query(Experiment).filter(Experiment.is_demo == True).all()
        
        exp_ids = [e.id for e in demo_exps]
        demo_runs = db.query(Run).filter(Run.experiment_id.in_(exp_ids)).all() if exp_ids else []
        run_ids = [r.id for r in demo_runs]
        demo_trials = db.query(Trial).filter(Trial.run_id.in_(run_ids)).all() if run_ids else []
        trial_ids = [t.id for t in demo_trials]
        demo_trajs = db.query(Trajectory).filter(Trajectory.trial_id.in_(trial_ids)).all() if trial_ids else []

        print(f"Found {len(demo_agents)} demo agents")
        print(f"Found {len(demo_tasks)} demo benchmark tasks")
        print(f"Found {len(demo_exps)} demo experiments")
        print(f"Found {len(demo_runs)} demo runs")
        print(f"Found {len(demo_trials)} demo trials")
        print(f"Found {len(demo_trajs)} demo trajectories")

        # Check trajectory files on disk
        artifacts_to_delete = []
        for traj in demo_trajs:
            if traj.storage_path and Path(traj.storage_path).exists():
                artifacts_to_delete.append(Path(traj.storage_path))

        # Check for any lingering mock/synthetic trajectory files in artifacts/trajectories
        if settings.TRAJECTORIES_DIR.exists():
            for p in settings.TRAJECTORIES_DIR.glob("trial_*.json"):
                if p not in artifacts_to_delete:
                    artifacts_to_delete.append(p)

        print(f"Found {len(artifacts_to_delete)} synthetic trajectory artifact files")

        if dry_run:
            print("\n[DRY RUN] No records or files were deleted.")
            return

        # Perform deletion
        deleted_files = 0
        for p in artifacts_to_delete:
            try:
                p.unlink(missing_ok=True)
                deleted_files += 1
            except Exception as e:
                print(f"Error removing {p}: {e}")

        # Delete from DB
        for exp in demo_exps:
            db.delete(exp)
        for task in demo_tasks:
            db.delete(task)
        for agent in demo_agents:
            db.delete(agent)

        db.commit()
        print(f"\n[CLEANUP COMPLETE] Removed demo DB records and {deleted_files} artifact files.")


def main():
    parser = argparse.ArgumentParser(description="Reliabench Management CLI")
    subparsers = parser.add_subparsers(dest="command")

    clean_parser = subparsers.add_parser("clean-demo-data", help="Clean synthetic demo records and mock artifacts")
    clean_parser.add_argument("--dry-run", action="store_true", help="Report records without deleting")

    args = parser.parse_args()

    if args.command == "clean-demo-data":
        clean_demo_data(dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

