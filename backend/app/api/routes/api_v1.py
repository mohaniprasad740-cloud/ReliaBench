from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.db.session import get_db
from app.models.entities import Agent, BenchmarkTask, FailureScenario, Experiment, Run, Trial, Trajectory, ToolEvent, ModelRequestEvent
from app.schemas.api import (
    AgentResponse, AgentCreate, AgentUpdate,
    BenchmarkTaskResponse, BenchmarkTaskCreate,
    FailureScenarioResponse,
    ExperimentResponse, ExperimentCreate,
    DashboardSummary, RunResponse
)
from app.adapters.harbor.adapter import HarborAdapter
from app.adapters.gateways.bifrost import BifrostAdapter
from app.services.execution import ExecutionService
from app.core.config import settings

router = APIRouter()

# ----------------- SYSTEM & DIAGNOSTICS -----------------
@router.get("/health")
def health_check():
    harbor_ad = HarborAdapter(settings.HARBOR_BIN_PATH, settings.HARBOR_VERSION_REQUIRED)
    bifrost_ad = BifrostAdapter()
    harbor_info = harbor_ad.check_availability()
    bifrost_info = bifrost_ad.get_status()

    # Determine active source mode
    if harbor_info.get("available") and harbor_info.get("docker_available"):
        active_mode = "REAL_EXECUTION"
    else:
        active_mode = "DETERMINISTIC_HARNESS"

    from app.benchmarks.pack import list_packs
    packs = list_packs()

    from app.adapters.tools.tavily import tavily_service
    tavily_info = tavily_service.get_status()

    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": "connected",
        "active_source_mode": active_mode,
        "pack_count": len(packs),
        "adapters": {
            "harbor": harbor_info,
            "bifrost": bifrost_info,
            "tavily": tavily_info,
        },
    }


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(source_mode: Optional[str] = Query(None), db: Session = Depends(get_db)):
    agents_query = db.query(Agent)
    benchmarks_query = db.query(BenchmarkTask)
    experiments_query = db.query(Experiment)
    runs_query = db.query(Run)

    if source_mode:
        agents_query = agents_query.filter(Agent.source_mode == source_mode)
        benchmarks_query = benchmarks_query.filter(BenchmarkTask.source_mode == source_mode)
        experiments_query = experiments_query.filter(Experiment.source_mode == source_mode)
        runs_query = runs_query.filter(Run.source_mode == source_mode)

    agents_count = agents_query.count()
    benchmarks_count = benchmarks_query.count()
    experiments_count = experiments_query.count()

    runs = runs_query.all()
    overall_pass = None
    avg_duration = 0.0
    median_duration = 0.0
    avg_cost = None

    if runs:
        valid_runs = [r for r in runs if r.total_trials > 0 and r.pass_rate is not None]
        if valid_runs:
            overall_pass = sum(r.pass_rate for r in valid_runs) / len(valid_runs)
            avg_duration = sum(r.avg_duration_seconds for r in valid_runs) / len(valid_runs)
            durations = [r.avg_duration_seconds for r in valid_runs]
            sorted_d = sorted(durations)
            median_duration = sorted_d[len(sorted_d) // 2]
            costs = [r.avg_cost_usd for r in valid_runs if r.avg_cost_usd is not None]
            avg_cost = (sum(costs) / len(costs)) if costs else None

    recent_exps = experiments_query.order_by(Experiment.created_at.desc()).limit(5).all()

    # Recent failure trials
    trials_query = db.query(Trial).filter(Trial.status == "FAILED")
    if source_mode:
        trials_query = trials_query.filter(Trial.source_mode == source_mode)
    failed_trials = trials_query.order_by(Trial.created_at.desc()).limit(5).all()

    recent_failures = []
    for ft in failed_trials:
        run = ft.run
        exp = run.experiment if run else None
        recent_failures.append({
            "trial_id": ft.id,
            "experiment_title": exp.title if exp else "Unknown",
            "agent_name": exp.agent.name if exp and exp.agent else "Unknown",
            "error_message": ft.error_message or "Verifier failed",
            "source_mode": ft.source_mode,
            "created_at": ft.created_at.isoformat()
        })

    # Reliability distribution across categories
    categories = db.query(BenchmarkTask.category).distinct().all()
    rel_dist = []
    for (cat,) in categories:
        cat_tasks = db.query(BenchmarkTask.id).filter(BenchmarkTask.category == cat)
        if source_mode:
            cat_tasks = cat_tasks.filter(BenchmarkTask.source_mode == source_mode)
        cat_task_ids = [t[0] for t in cat_tasks.all()]
        
        cat_runs = db.query(Run).join(Experiment).filter(Experiment.benchmark_task_id.in_(cat_task_ids))
        if source_mode:
            cat_runs = cat_runs.filter(Run.source_mode == source_mode)
        cat_runs_list = cat_runs.all()

        if cat_runs_list:
            valid_cat_runs = [r for r in cat_runs_list if r.pass_rate is not None]
            pass_rt = (sum(r.pass_rate for r in valid_cat_runs) / len(valid_cat_runs)) if valid_cat_runs else 0.0
            rec_runs = [r.recovery_rate for r in cat_runs_list if r.recovery_rate is not None]
            rec_rt = (sum(rec_runs) / len(rec_runs)) if rec_runs else 0.0
        else:
            pass_rt = 0.0
            rec_rt = 0.0

        rel_dist.append({
            "category": cat,
            "pass_rate": round(pass_rt, 3),
            "recovery_rate": round(rec_rt, 3),
            "sample_size": len(cat_runs_list)
        })

    harbor_status = HarborAdapter(settings.HARBOR_BIN_PATH, settings.HARBOR_VERSION_REQUIRED).check_availability()
    active_mode = "HARBOR_NATIVE" if harbor_status.get("available") and harbor_status.get("docker_available") else "SIMULATOR_DEMO"

    return DashboardSummary(
        total_agents=agents_count,
        total_benchmarks=benchmarks_count,
        total_experiments=experiments_count,
        overall_pass_rate=round(overall_pass, 3) if overall_pass is not None else None,
        average_duration_seconds=round(avg_duration, 1),
        median_duration_seconds=round(median_duration, 1),
        average_cost_usd=round(avg_cost, 4) if avg_cost else None,
        active_environment_mode=active_mode,
        source_mode=source_mode or "ALL",
        harbor_status=harbor_status,
        recent_experiments=recent_exps,
        recent_failures=recent_failures,
        reliability_distribution=rel_dist
    )

# ----------------- AGENT REGISTRY -----------------
@router.get("/agents", response_model=List[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).order_by(Agent.created_at.desc()).all()

@router.post("/agents", response_model=AgentResponse, status_code=201)
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db)):
    # Auto-assign status based on adapter
    status = "CONFIGURED"
    if agent_in.adapter_type == "simulator":
        status = "SIMULATOR"
    agent_data = agent_in.model_dump()
    agent_data["status"] = status
    agent = Agent(**agent_data)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

@router.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/agents/{agent_id}/validate")
def validate_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    from app.adapters.agents.real_adapters import HttpAgentAdapter, CliAgentAdapter

    # Check adapter connectivity
    if agent.adapter_type == "http" and agent.endpoint_url:
        adapter = HttpAgentAdapter(endpoint_url=agent.endpoint_url)
        probe_res = adapter.probe()
        agent.status = probe_res.status
        db.commit()
        db.refresh(agent)
        return {
            "message": probe_res.message,
            "status": probe_res.status,
            "latency_ms": probe_res.latency_ms,
            "details": probe_res.details,
        }
    elif agent.adapter_type == "cli" and agent.endpoint_url:
        adapter = CliAgentAdapter(command_path=agent.endpoint_url)
        probe_res = adapter.probe()
        agent.status = probe_res.status
        db.commit()
        db.refresh(agent)
        return {
            "message": probe_res.message,
            "status": probe_res.status,
            "latency_ms": probe_res.latency_ms,
            "details": probe_res.details,
        }
    elif agent.adapter_type == "harbor_cli":
        harbor_ad = HarborAdapter(settings.HARBOR_BIN_PATH, settings.HARBOR_VERSION_REQUIRED)
        avail = harbor_ad.check_availability()
        agent.status = "AVAILABLE" if (avail["available"] and avail["docker_available"]) else "UNAVAILABLE"
        db.commit()
        db.refresh(agent)
        return {
            "message": f"Harbor availability check: {avail['status']}",
            "status": agent.status,
            "details": avail,
        }
    else:
        agent.status = "VALIDATED"
        db.commit()
        db.refresh(agent)
        return {"message": "Agent validation complete", "status": agent.status}

@router.put("/agents/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: str, agent_in: AgentUpdate, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for field, val in agent_in.model_dump(exclude_unset=True).items():
        setattr(agent, field, val)
    db.commit()
    db.refresh(agent)
    return agent

@router.delete("/agents/{agent_id}")
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"message": "Agent deleted successfully"}

# ----------------- BENCHMARK TASK LIBRARY -----------------
@router.get("/benchmarks", response_model=List[BenchmarkTaskResponse])
def list_benchmarks(db: Session = Depends(get_db)):
    return db.query(BenchmarkTask).order_by(BenchmarkTask.created_at.desc()).all()

@router.post("/benchmarks", response_model=BenchmarkTaskResponse, status_code=201)
def create_benchmark(task_in: BenchmarkTaskCreate, db: Session = Depends(get_db)):
    task = BenchmarkTask(**task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/benchmarks/{benchmark_id}", response_model=BenchmarkTaskResponse)
def get_benchmark(benchmark_id: str, db: Session = Depends(get_db)):
    task = db.query(BenchmarkTask).filter(BenchmarkTask.id == benchmark_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Benchmark task not found")
    return task

# ----------------- FAILURE SCENARIOS -----------------
@router.get("/failures")
def list_failures(db: Session = Depends(get_db)):
    from app.faults.catalog import get_system_failure_catalog
    # Return the supported system failure scenarios catalog
    # Also combine with any custom DB failure scenarios if added by users
    db_failures = db.query(FailureScenario).all()
    if db_failures:
        return [
            {
                "id": f.id,
                "name": f.name,
                "code": f.code,
                "description": f.description,
                "trigger_point": f.trigger_point,
                "severity": f.severity,
                "parameters": f.parameters,
            }
            for f in db_failures
        ]
    # Default: system catalog definitions
    return [
        {
            "id": entry.id,
            "name": entry.name,
            "code": entry.code,
            "description": entry.description,
            "trigger_point": entry.trigger_point,
            "severity": entry.severity,
            "parameters": entry.default_parameters,
        }
        for entry in get_system_failure_catalog()
    ]

# ----------------- EXPERIMENTS -----------------
@router.get("/experiments", response_model=List[ExperimentResponse])
def list_experiments(db: Session = Depends(get_db)):
    return db.query(Experiment).order_by(Experiment.created_at.desc()).all()

@router.post("/experiments", response_model=ExperimentResponse, status_code=201)
def create_experiment(exp_in: ExperimentCreate, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == exp_in.agent_id).first()
    if not agent:
        raise HTTPException(status_code=400, detail="Invalid agent_id")
    task = db.query(BenchmarkTask).filter(BenchmarkTask.id == exp_in.benchmark_task_id).first()
    if not task:
        raise HTTPException(status_code=400, detail="Invalid benchmark_task_id")

    failure = None
    if exp_in.failure_scenario_id:
        failure = db.query(FailureScenario).filter(FailureScenario.id == exp_in.failure_scenario_id).first()

    config_snapshot = {
        "title": exp_in.title,
        "description": exp_in.description,
        "repetitions_k": exp_in.repetitions_k,
        "timeout_seconds": exp_in.timeout_seconds,
        "seed": 42,
        "snapshot_timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "version": agent.version,
            "framework": agent.framework,
            "adapter_type": agent.adapter_type,
            "model_provider": agent.model_provider,
            "model_name": agent.model_name,
            "endpoint_url": agent.endpoint_url,
            "source_mode": agent.source_mode,
        },
        "benchmark_task": {
            "id": task.id,
            "name": task.name,
            "version": task.version,
            "category": task.category,
            "difficulty": task.difficulty,
            "verification_method": task.verification_method,
            "time_limit_seconds": task.time_limit_seconds,
            "environment_type": task.environment_type,
            "instruction": task.instruction,
            "expected_outcome": task.expected_outcome,
        },
        "failure_scenario": {
            "id": failure.id,
            "name": failure.name,
            "code": failure.code,
            "trigger_point": failure.trigger_point,
            "severity": failure.severity,
            "parameters": failure.parameters or {},
        } if failure else None,
        "integrations": {
            "bifrost_enabled": settings.ENABLE_BIFROST_GATEWAY,
            "bifrost_endpoint": settings.BIFROST_ENDPOINT,
            "tavily_configured": bool(settings.TAVILY_API_KEY),
            "harbor_required_version": settings.HARBOR_VERSION_REQUIRED,
        }
    }

    exp = Experiment(
        **exp_in.model_dump(),
        config_snapshot=config_snapshot,
        status="QUEUED",
        source_mode=agent.source_mode,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp

@router.post("/experiments/{experiment_id}/reproduce", response_model=ExperimentResponse, status_code=201)
def reproduce_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Creates a new experiment faithfully derived from an immutable historical configuration snapshot."""
    orig = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not orig:
        raise HTTPException(status_code=404, detail="Original experiment not found")

    snapshot = orig.config_snapshot or {}
    new_title = f"{orig.title} (Reproduced #{str(uuid.uuid4())[:4]})"

    new_exp = Experiment(
        title=new_title,
        description=f"Deterministic reproduction of experiment {orig.id}.",
        agent_id=orig.agent_id,
        benchmark_task_id=orig.benchmark_task_id,
        failure_scenario_id=orig.failure_scenario_id,
        repetitions_k=orig.repetitions_k,
        timeout_seconds=orig.timeout_seconds,
        config_snapshot=snapshot,
        status="QUEUED",
        source_mode=orig.source_mode,
    )
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return new_exp

@router.get("/experiments/{experiment_id}/events")
def get_experiment_unified_events(experiment_id: str, db: Session = Depends(get_db)):
    """Returns chronological timeline combining ModelRequestEvent and ToolEvent across all trials in this experiment."""
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    events = []
    for run in exp.runs:
        for trial in run.trials:
            for req in getattr(trial, "model_requests", []):
                events.append({
                    "event_type": "MODEL_REQUEST",
                    "event_id": req.id,
                    "trial_id": trial.id,
                    "trial_number": trial.trial_number,
                    "correlation_id": req.correlation_id,
                    "provider": req.provider,
                    "model": req.model,
                    "prompt_tokens": req.prompt_tokens,
                    "completion_tokens": req.completion_tokens,
                    "total_tokens": req.total_tokens,
                    "cost_usd": req.cost_usd,
                    "latency_ms": req.latency_ms,
                    "fallback_used": req.fallback_used,
                    "retry_count": req.retry_count,
                    "status_code": req.status_code,
                    "timestamp": req.created_at.isoformat() if req.created_at else None,
                })
            for tool in getattr(trial, "tool_events", []):
                events.append({
                    "event_type": "TOOL_CALL",
                    "event_id": tool.id,
                    "trial_id": trial.id,
                    "trial_number": trial.trial_number,
                    "tool_name": tool.tool_name,
                    "tool_call_id": tool.tool_call_id,
                    "args": tool.args,
                    "observation": tool.observation,
                    "is_error": tool.is_error,
                    "error_message": tool.error_message,
                    "latency_ms": tool.latency_ms,
                    "source": tool.source,
                    "meta_info": tool.meta_info,
                    "timestamp": tool.created_at.isoformat() if tool.created_at else None,
                })

    events.sort(key=lambda e: e.get("timestamp") or "")
    return {
        "experiment_id": experiment_id,
        "total_events": len(events),
        "events": events,
    }

@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp

@router.post("/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    executor = ExecutionService(db)
    background_tasks.add_task(executor.execute_experiment_async, experiment_id)
    return {"message": "Experiment execution started", "experiment_id": experiment_id, "status": "RUNNING"}

@router.post("/experiments/{experiment_id}/cancel")
def cancel_experiment(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    exp.status = "CANCELLED"
    db.commit()
    return {"message": "Experiment marked CANCELLED", "experiment_id": experiment_id}

# ----------------- RUNS & TRAJECTORIES -----------------
@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/runs/{run_id}/export")
def export_run_scorecard(
    run_id: str,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
):
    """Full scorecard export with metrics, per-trial outcomes, taxonomy, and provenance."""
    import csv
    import io
    from fastapi.responses import Response

    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    trials_data = []
    for t in run.trials:
        trials_data.append({
            "trial_id": t.id,
            "trial_number": t.trial_number,
            "status": t.status,
            "reward_score": t.reward_score,
            "duration_seconds": t.duration_seconds,
            "failure_injected": t.failure_injected,
            "failure_recovered": t.failure_recovered,
            "error_message": t.error_message or "",
            "source_mode": t.source_mode,
        })

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "run_id",
            "trial_number",
            "status",
            "reward_score",
            "duration_seconds",
            "failure_injected",
            "failure_recovered",
            "error_message",
            "source_mode",
        ])
        for td in trials_data:
            writer.writerow([
                run.id,
                td["trial_number"],
                td["status"],
                td["reward_score"],
                td["duration_seconds"],
                td["failure_injected"],
                td["failure_recovered"],
                td["error_message"],
                td["source_mode"],
            ])
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=run_{run_id}.csv"},
        )

    return {
        "run_id": run.id,
        "experiment_id": run.experiment_id,
        "status": run.status,
        "source_mode": run.source_mode,
        "total_trials": run.total_trials,
        "successful_trials": run.successful_trials,
        "failed_trials": run.failed_trials,
        "pass_rate": run.pass_rate,
        "ci_lower": run.ci_lower,
        "ci_upper": run.ci_upper,
        "pass_at_k": run.pass_at_k,
        "pass_to_k": run.pass_to_k,
        "recovery_rate": run.recovery_rate,
        "avg_duration_seconds": run.avg_duration_seconds,
        "median_duration_seconds": run.median_duration_seconds,
        "avg_cost_usd": run.avg_cost_usd,
        "total_tokens": run.total_tokens,
        "trials": trials_data,
    }


@router.get("/runs/{run_id}/trajectory")
def get_run_trajectory(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run or not run.trials:
        raise HTTPException(status_code=404, detail="Run or trials not found")

    trial = run.trials[0]
    traj = trial.trajectory
    if not traj:
        raise HTTPException(status_code=404, detail="Trajectory record not found for trial")

    # Use storage abstraction to read trajectory content
    from app.storage.artifacts import get_artifact_storage
    storage = get_artifact_storage()

    raw_content = storage.read_artifact(traj.storage_path)
    if raw_content:
        try:
            return json.loads(raw_content)
        except Exception:
            pass
    
    return {
        "schema_version": traj.atif_version,
        "trajectory_id": f"reliabench:{trial.id}",
        "steps": traj.summary_steps
    }

# ----------------- COMPARISONS -----------------
@router.get("/comparisons")
def compare_experiments(experiment_ids: str, db: Session = Depends(get_db)):
    ids = [i.strip() for i in experiment_ids.split(",") if i.strip()]
    if not ids:
        raise HTTPException(status_code=400, detail="Provide at least one experiment_id")

    experiments = db.query(Experiment).filter(Experiment.id.in_(ids)).all()
    comparison_data = []

    # Check condition compatibility across compared experiments
    task_ids = set()
    failure_ids = set()
    repetitions_set = set()

    for exp in experiments:
        task_ids.add(exp.benchmark_task_id)
        failure_ids.add(exp.failure_scenario_id)
        repetitions_set.add(exp.repetitions_k)

    is_compatible = (len(task_ids) <= 1 and len(failure_ids) <= 1 and len(repetitions_set) <= 1)
    compatibility_warning = None if is_compatible else "Warning: Selected experiments evaluate different benchmark tasks, failure conditions, or repetition counts (k). Cross-condition comparisons should be interpreted with caution."

    for exp in experiments:
        latest_run = exp.runs[-1] if exp.runs else None
        comparison_data.append({
            "experiment_id": exp.id,
            "title": exp.title,
            "agent_name": exp.agent.name if exp.agent else "Unknown",
            "framework": exp.agent.framework if exp.agent else "Unknown",
            "model_name": exp.agent.model_name if exp.agent else "Unknown",
            "task_name": exp.benchmark_task.name if exp.benchmark_task else "Unknown",
            "failure_injected": exp.failure_scenario.name if exp.failure_scenario else "None (Clean)",
            "repetitions_k": exp.repetitions_k,
            "pass_rate": latest_run.pass_rate if latest_run else None,
            "ci_lower": latest_run.ci_lower if latest_run else None,
            "ci_upper": latest_run.ci_upper if latest_run else None,
            "pass_at_k": latest_run.pass_at_k if latest_run else None,
            "pass_to_k": latest_run.pass_to_k if latest_run else None,
            "recovery_rate": latest_run.recovery_rate if latest_run else None,
            "avg_duration_seconds": latest_run.avg_duration_seconds if latest_run else 0.0,
            "median_duration_seconds": latest_run.median_duration_seconds if latest_run else 0.0,
            "duration_variance": latest_run.duration_variance if latest_run else 0.0,
            "avg_cost_usd": latest_run.avg_cost_usd if latest_run else None,
            "source_mode": exp.source_mode,
            "status": exp.status
        })

    return {
        "comparisons": comparison_data,
        "is_compatible": is_compatible,
        "compatibility_warning": compatibility_warning
    }


# ----------------- INTEGRATION DIAGNOSTICS & PROBES -----------------
@router.post("/integrations/tavily/test")
def test_tavily_integration():
    from app.adapters.tools.tavily import tavily_service
    status = tavily_service.client.check_connection()
    return status


@router.post("/integrations/bifrost/test")
def test_bifrost_integration():
    bifrost_ad = BifrostAdapter()
    return bifrost_ad.get_status()

