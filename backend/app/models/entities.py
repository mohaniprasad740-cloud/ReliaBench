import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    framework = Column(String(50), nullable=False, default="custom")
    version = Column(String(30), nullable=False, default="1.0.0")
    adapter_type = Column(String(50), nullable=False, default="simulator")
    model_provider = Column(String(50), nullable=True)
    model_name = Column(String(100), nullable=True)
    endpoint_url = Column(String(255), nullable=True)
    status = Column(String(30), nullable=False, default="CONFIGURED") # CONFIGURED, VALIDATED, AVAILABLE, UNAVAILABLE, ERROR, SIMULATOR
    source_mode = Column(String(30), nullable=False, default="SIMULATOR") # REAL_EXECUTION, SIMULATOR
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    experiments = relationship("Experiment", back_populates="agent", cascade="all, delete-orphan")


class BenchmarkTask(Base):
    __tablename__ = "benchmark_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(120), nullable=False, index=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    category = Column(String(60), nullable=False, default="general")
    difficulty = Column(String(20), nullable=False, default="MEDIUM")
    description = Column(Text, nullable=False)
    instruction = Column(Text, nullable=False)
    expected_outcome = Column(Text, nullable=False)
    verification_method = Column(String(50), nullable=False, default="ASSERTION_SCRIPT") # ASSERTION_SCRIPT, SCRIPT_VERIFIER, FILE_STATE, STRUCTURED_OUTPUT
    time_limit_seconds = Column(Integer, default=120)
    environment_type = Column(String(50), default="DOCKER_SANDBOX")
    source_mode = Column(String(30), nullable=False, default="SIMULATOR")
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    experiments = relationship("Experiment", back_populates="benchmark_task", cascade="all, delete-orphan")


class FailureScenario(Base):
    __tablename__ = "failure_scenarios"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    trigger_point = Column(String(50), nullable=False, default="TOOL_CALL")
    severity = Column(String(20), nullable=False, default="MEDIUM")
    parameters = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    experiments = relationship("Experiment", back_populates="failure_scenario")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    benchmark_task_id = Column(String(36), ForeignKey("benchmark_tasks.id"), nullable=False)
    failure_scenario_id = Column(String(36), ForeignKey("failure_scenarios.id"), nullable=True)
    repetitions_k = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=180)
    status = Column(String(30), default="QUEUED", index=True)  # DRAFT, QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    source_mode = Column(String(30), nullable=False, default="SIMULATOR") # REAL_EXECUTION, SIMULATOR
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    agent = relationship("Agent", back_populates="experiments")
    benchmark_task = relationship("BenchmarkTask", back_populates="experiments")
    failure_scenario = relationship("FailureScenario", back_populates="experiments")
    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("experiments.id"), nullable=False)
    total_trials = Column(Integer, default=0)
    successful_trials = Column(Integer, default=0)
    failed_trials = Column(Integer, default=0)
    pass_rate = Column(Float, nullable=True)
    ci_lower = Column(Float, nullable=True) # Wilson score lower bound
    ci_upper = Column(Float, nullable=True) # Wilson score upper bound
    pass_at_k = Column(Float, nullable=True)
    pass_to_k = Column(Float, nullable=True)
    recovery_rate = Column(Float, nullable=True)
    avg_duration_seconds = Column(Float, default=0.0)
    median_duration_seconds = Column(Float, default=0.0)
    duration_variance = Column(Float, default=0.0)
    avg_cost_usd = Column(Float, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    status = Column(String(30), default="COMPLETED")
    source_mode = Column(String(30), nullable=False, default="SIMULATOR")
    created_at = Column(DateTime, default=utc_now)

    experiment = relationship("Experiment", back_populates="runs")
    trials = relationship("Trial", back_populates="run", cascade="all, delete-orphan")


class Trial(Base):
    __tablename__ = "trials"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("runs.id"), nullable=False)
    trial_number = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False, default="PASSED")  # PASSED, FAILED, RECOVERED, TIMEOUT, INFRASTRUCTURE_ERROR
    reward_score = Column(Float, default=1.0)
    duration_seconds = Column(Float, default=0.0)
    failure_injected = Column(Boolean, default=False)
    failure_recovered = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    log_file_path = Column(String(255), nullable=True)
    source_mode = Column(String(30), nullable=False, default="SIMULATOR")
    created_at = Column(DateTime, default=utc_now)

    run = relationship("Run", back_populates="trials")
    trajectory = relationship("Trajectory", back_populates="trial", uselist=False, cascade="all, delete-orphan")


class Trajectory(Base):
    __tablename__ = "trajectories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trial_id = Column(String(36), ForeignKey("trials.id"), nullable=False, unique=True)
    atif_version = Column(String(30), default="ATIF-v1.8")
    total_steps = Column(Integer, default=0)
    agent_name = Column(String(100), nullable=True)
    model_name = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    storage_path = Column(String(255), nullable=False)
    summary_steps = Column(JSON, default=list)

    trial = relationship("Trial", back_populates="trajectory")


class ToolEvent(Base):
    __tablename__ = "tool_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trial_id = Column(String(36), ForeignKey("trials.id"), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False)
    tool_call_id = Column(String(100), nullable=True)
    args = Column(JSON, default=dict)
    observation = Column(Text, nullable=True)
    is_error = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Float, default=0.0)
    source = Column(String(50), default="TAVILY")  # TAVILY, LOCAL_SHELL, MCP
    meta_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    trial = relationship("Trial", backref="tool_events")


class ModelRequestEvent(Base):
    __tablename__ = "model_request_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trial_id = Column(String(36), ForeignKey("trials.id"), nullable=False, index=True)
    correlation_id = Column(String(100), nullable=True, index=True)
    provider = Column(String(50), default="bifrost")
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, nullable=True)
    latency_ms = Column(Float, default=0.0)
    fallback_used = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    status_code = Column(Integer, default=200)
    created_at = Column(DateTime, default=utc_now)

    trial = relationship("Trial", backref="model_requests")

