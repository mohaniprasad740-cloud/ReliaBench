import {
  DashboardSummary,
  Agent,
  BenchmarkTask,
  FailureScenario,
  Experiment,
  Run,
  ATIFTrajectory
} from './types';

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '') + '/api/v1';

export const api = {
  // System
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  async testTavily() {
    const res = await fetch(`${API_BASE}/integrations/tavily/test`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to test Tavily connection');
    return res.json();
  },

  async testBifrost() {
    const res = await fetch(`${API_BASE}/integrations/bifrost/test`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to test Bifrost connection');
    return res.json();
  },

  async getDashboardSummary(sourceMode?: string): Promise<DashboardSummary> {
    const url = sourceMode ? `${API_BASE}/dashboard/summary?source_mode=${sourceMode}` : `${API_BASE}/dashboard/summary`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch dashboard summary');
    return res.json();
  },

  // Agents
  async getAgents(): Promise<Agent[]> {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) throw new Error('Failed to fetch agents');
    return res.json();
  },

  async createAgent(data: Partial<Agent>): Promise<Agent> {
    const res = await fetch(`${API_BASE}/agents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create agent');
    return res.json();
  },

  async validateAgent(id: string): Promise<{ message: string; status: string }> {
    const res = await fetch(`${API_BASE}/agents/${id}/validate`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to validate agent');
    return res.json();
  },

  async deleteAgent(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/agents/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete agent');
  },

  // Benchmarks
  async getBenchmarks(): Promise<BenchmarkTask[]> {
    const res = await fetch(`${API_BASE}/benchmarks`);
    if (!res.ok) throw new Error('Failed to fetch benchmark tasks');
    return res.json();
  },

  async createBenchmark(data: Partial<BenchmarkTask>): Promise<BenchmarkTask> {
    const res = await fetch(`${API_BASE}/benchmarks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create benchmark');
    return res.json();
  },

  // Failures
  async getFailures(): Promise<FailureScenario[]> {
    const res = await fetch(`${API_BASE}/failures`);
    if (!res.ok) throw new Error('Failed to fetch failure scenarios');
    return res.json();
  },

  // Experiments
  async getExperiments(): Promise<Experiment[]> {
    const res = await fetch(`${API_BASE}/experiments`);
    if (!res.ok) throw new Error('Failed to fetch experiments');
    return res.json();
  },

  async getExperiment(id: string): Promise<Experiment> {
    const res = await fetch(`${API_BASE}/experiments/${id}`);
    if (!res.ok) throw new Error('Failed to fetch experiment details');
    return res.json();
  },

  async createExperiment(data: {
    title: string;
    agent_id: string;
    benchmark_task_id: string;
    failure_scenario_id?: string;
    repetitions_k: number;
    timeout_seconds: number;
  }): Promise<Experiment> {
    const res = await fetch(`${API_BASE}/experiments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to configure experiment');
    return res.json();
  },

  async startExperiment(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/experiments/${id}/start`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to start experiment');
  },

  // Runs & ATIF Trajectories
  async getRun(id: string): Promise<Run> {
    const res = await fetch(`${API_BASE}/runs/${id}`);
    if (!res.ok) throw new Error('Failed to fetch run');
    return res.json();
  },

  async getRunTrajectory(id: string): Promise<ATIFTrajectory> {
    const res = await fetch(`${API_BASE}/runs/${id}/trajectory`);
    if (!res.ok) throw new Error('Failed to fetch ATIF trajectory');
    return res.json();
  },

  // Comparisons
  async getComparisons(experimentIds: string[]): Promise<any> {
    const res = await fetch(`${API_BASE}/comparisons?experiment_ids=${experimentIds.join(',')}`);
    if (!res.ok) throw new Error('Failed to fetch comparisons');
    return res.json();
  },

  // Reliability Core Endpoints
  async getPacks(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/packs`);
    if (!res.ok) throw new Error('Failed to fetch packs');
    return res.json();
  },

  async getPack(packId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/packs/${packId}`);
    if (!res.ok) throw new Error(`Failed to fetch pack ${packId}`);
    return res.json();
  },

  async runPack(packId: string, payload: {
    profile: string;
    k: number;
    seed: number;
    fault_kind?: string;
    at_step?: number;
    tool?: string;
    probability?: number;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/packs/${packId}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to run challenge pack');
    }
    return res.json();
  },

  async getTaxonomy(): Promise<any> {
    const res = await fetch(`${API_BASE}/taxonomy`);
    if (!res.ok) throw new Error('Failed to fetch failure taxonomy');
    return res.json();
  },

  async getRegressions(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/regressions`);
    if (!res.ok) throw new Error('Failed to fetch regression gates');
    return res.json();
  },

  async replayRegression(caseId: string, runnerAgent?: string): Promise<any> {
    const url = runnerAgent
      ? `${API_BASE}/regressions/${caseId}/replay?runner_agent=${runnerAgent}`
      : `${API_BASE}/regressions/${caseId}/replay`;
    const res = await fetch(url, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to replay regression case');
    return res.json();
  },

  async replayAllRegressions(targetAgent?: string): Promise<any> {
    const url = targetAgent
      ? `${API_BASE}/regressions/run-all?target_agent=${targetAgent}`
      : `${API_BASE}/regressions/run-all`;
    const res = await fetch(url, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to replay all regressions');
    return res.json();
  }
};

