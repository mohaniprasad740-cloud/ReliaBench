from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Base Agent
class AgentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    framework: str = Field("custom", max_length=50)
    version: str = Field("1.0.0", max_length=30)
    adapter_type: str = Field("simulator", max_length=50)
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    status: str = "CONFIGURED"
    source_mode: str = "SIMULATOR"
    is_demo: bool = False

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    framework: Optional[str] = None
    version: Optional[str] = None
    adapter_type: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    status: Optional[str] = None

class AgentResponse(AgentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Benchmark Task
class BenchmarkTaskBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    version: str = "1.0.0"
    category: str = "general"
    difficulty: str = "MEDIUM"
    description: str
    instruction: str
    expected_outcome: str
    verification_method: str = "ASSERTION_SCRIPT"
    time_limit_seconds: int = 120
    environment_type: str = "DOCKER_SANDBOX"
    source_mode: str = "SIMULATOR"
    is_demo: bool = False

class BenchmarkTaskCreate(BenchmarkTaskBase):
    pass

class BenchmarkTaskResponse(BenchmarkTaskBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Failure Scenario
class FailureScenarioResponse(BaseModel):
    id: str
    name: str
    code: str
    description: str
    trigger_point: str
    severity: str
    parameters: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

# Experiment
class ExperimentCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    agent_id: str
    benchmark_task_id: str
    failure_scenario_id: Optional[str] = None
    repetitions_k: int = Field(3, ge=1, le=10)
    timeout_seconds: int = Field(180, ge=10, le=600)

class ToolEventResponse(BaseModel):
    id: str
    trial_id: str
    tool_name: str
    tool_call_id: Optional[str] = None
    args: Dict[str, Any] = Field(default_factory=dict)
    observation: Optional[str] = None
    is_error: bool = False
    error_message: Optional[str] = None
    latency_ms: float = 0.0
    source: str = "TAVILY"
    meta_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ModelRequestEventResponse(BaseModel):
    id: str
    trial_id: str
    correlation_id: Optional[str] = None
    provider: str = "bifrost"
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: Optional[float] = None
    latency_ms: float = 0.0
    fallback_used: bool = False
    retry_count: int = 0
    status_code: int = 200
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TrialResponse(BaseModel):
    id: str
    trial_number: int
    status: str
    reward_score: float
    duration_seconds: float
    failure_injected: bool
    failure_recovered: bool
    error_message: Optional[str] = None
    taxonomy_category: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    source_mode: str
    tool_events: List[ToolEventResponse] = Field(default_factory=list)
    model_requests: List[ModelRequestEventResponse] = Field(default_factory=list)
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RunResponse(BaseModel):
    id: str
    total_trials: int
    successful_trials: int
    failed_trials: int
    pass_rate: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    pass_at_k: Optional[float] = None
    pass_to_k: Optional[float] = None
    recovery_rate: Optional[float] = None
    avg_duration_seconds: float
    median_duration_seconds: float = 0.0
    duration_variance: float
    avg_cost_usd: Optional[float] = None
    total_tokens: Optional[int] = None
    status: str
    source_mode: str
    trials: List[TrialResponse] = Field(default_factory=list)
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExperimentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    agent_id: str
    benchmark_task_id: str
    failure_scenario_id: Optional[str] = None
    repetitions_k: int
    timeout_seconds: int
    config_snapshot: Optional[Dict[str, Any]] = None
    status: str
    source_mode: str
    is_demo: bool
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    agent: Optional[AgentResponse] = None
    benchmark_task: Optional[BenchmarkTaskResponse] = None
    failure_scenario: Optional[FailureScenarioResponse] = None
    runs: List[RunResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

# Dashboard
class DashboardSummary(BaseModel):
    total_agents: int
    total_benchmarks: int
    total_experiments: int
    overall_pass_rate: Optional[float] = None
    average_duration_seconds: float
    median_duration_seconds: float = 0.0
    average_cost_usd: Optional[float] = None
    active_environment_mode: str
    source_mode: str = "SIMULATOR"
    harbor_status: Dict[str, Any]
    recent_experiments: List[ExperimentResponse]
    recent_failures: List[Dict[str, Any]]
    reliability_distribution: List[Dict[str, Any]]
