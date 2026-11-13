import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Experiment, Agent, BenchmarkTask, FailureScenario } from '../services/types';
import { FlaskConical, Play, Plus, RefreshCw, AlertTriangle, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export const ExperimentsPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<BenchmarkTask[]>([]);
  const [failures, setFailures] = useState<FailureScenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const [form, setForm] = useState({
    title: '',
    agent_id: '',
    benchmark_task_id: '',
    failure_scenario_id: '',
    repetitions_k: 3,
    timeout_seconds: 180
  });

  const loadAll = async () => {
    setLoading(true);
    try {
      const [exps, ags, bms, fails] = await Promise.all([
        api.getExperiments(),
        api.getAgents(),
        api.getBenchmarks(),
        api.getFailures()
      ]);
      setExperiments(exps);
      setAgents(ags);
      setTasks(bms);
      setFailures(fails);

      if (ags.length > 0 && bms.length > 0) {
        setForm((prev) => ({
          ...prev,
          agent_id: prev.agent_id || ags[0].id,
          benchmark_task_id: prev.benchmark_task_id || bms[0].id
        }));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await api.createExperiment({
        ...form,
        failure_scenario_id: form.failure_scenario_id || undefined
      });
      // Automatically trigger execution
      await api.startExperiment(created.id);
      setShowModal(false);
      loadAll();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleStart = async (id: string) => {
    await api.startExperiment(id);
    loadAll();
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center pb-6 border-b border-[#2D332B]">
        <div>
          <h1 className="text-2xl font-black text-[#E8DDC8] flex items-center gap-2">
            <FlaskConical size={26} className="text-[#F06B45]" />
            <span>Benchmark Experiments & Repeated Runs</span>
          </h1>
          <p className="text-xs text-[#A7A393] font-sans mt-0.5">
            Configure repeatable multi-trial evaluations ($k$ repetitions) with controlled fault injection.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={loadAll}
            className="reliabench-btn reliabench-btn-outline"
          >
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="reliabench-btn reliabench-btn-persimmon"
          >
            <Plus size={14} />
            <span>New Experiment</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="font-mono text-xs text-[#C7D94C]">[ FETCHING BENCHMARK RUNS... ]</div>
      ) : experiments.length === 0 ? (
        <div className="reliabench-panel p-10 text-center">
          <FlaskConical size={40} className="text-[#89977A] mx-auto mb-4" />
          <h3 className="text-lg font-bold text-[#E8DDC8] mb-2">No experiments executed yet</h3>
          <p className="text-xs text-[#A7A393] mb-4 max-w-lg mx-auto">
            Create a benchmark experiment by selecting a registered agent, a challenge pack task, and an optional failure scenario. Each experiment runs <em>k</em> repeated trials to measure reliability.
          </p>
          {agents.length === 0 ? (
            <p className="text-xs text-[#F06B45] font-mono mb-4">
              ⚠ Register at least one agent before creating experiments.
            </p>
          ) : (
            <button
              onClick={() => setShowModal(true)}
              className="reliabench-btn reliabench-btn-persimmon"
            >
              <Plus size={14} />
              <span>Create First Experiment</span>
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {experiments.map((exp) => {
            const latestRun = exp.runs && exp.runs.length > 0 ? exp.runs[exp.runs.length - 1] : null;

            return (
              <div key={exp.id} className="reliabench-panel p-6">
                <div className="flex flex-col lg:flex-row justify-between lg:items-center gap-4 mb-4 pb-4 border-b border-[#2D332B]">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <span className="font-black text-base text-[#E8DDC8]">{exp.title}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#142B20] text-[#C7D94C] border border-[#234A35]">
                        {exp.status}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                        exp.source_mode === 'REAL_EXECUTION'
                          ? 'bg-[#1D2B1C] text-[#C7D94C] border-[#3B5436]'
                          : 'bg-[#2B231D] text-[#F06B45] border-[#5E3F2A]'
                      }`}>
                        {exp.source_mode}
                      </span>
                    </div>
                    <div className="text-xs font-mono text-[#89977A] flex gap-4">
                      <span>Agent: <strong className="text-[#C49A55]">{exp.agent?.name}</strong></span>
                      <span>Task: <strong className="text-[#E8DDC8]">{exp.benchmark_task?.name}</strong></span>
                      <span>
                        Fault: <strong className={exp.failure_scenario ? 'text-[#F06B45]' : 'text-slate-400'}>
                          {exp.failure_scenario?.name || 'Clean Run (No Fault)'}
                        </strong>
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {exp.status !== 'RUNNING' && (
                      <button
                        onClick={() => handleStart(exp.id)}
                        className="reliabench-btn reliabench-btn-lime text-xs py-1.5 px-3"
                      >
                        <Play size={13} />
                        <span>Re-Execute</span>
                      </button>
                    )}
                    {latestRun && (
                      <Link
                        to={`/app/traces?run_id=${latestRun.id}`}
                        className="reliabench-btn reliabench-btn-outline text-xs py-1.5 px-3"
                      >
                        Inspect ATIF Trace
                      </Link>
                    )}
                  </div>
                </div>

                {/* Scorecard Metrics Bar */}
                {latestRun ? (
                  <div>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-4 font-mono">
                      <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                        <div className="text-[10px] uppercase font-bold text-[#89977A]">Pass Rate</div>
                        <div className="text-xl font-black text-[#C7D94C]">
                          {latestRun.pass_rate !== null ? `${(latestRun.pass_rate * 100).toFixed(0)}%` : 'N/A'}
                        </div>
                      </div>

                      <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                        <div className="text-[10px] uppercase font-bold text-[#89977A]">Pass@{exp.repetitions_k}</div>
                        <div className="text-xl font-black text-[#E8DDC8]">
                          {latestRun.pass_at_k !== null ? `${(latestRun.pass_at_k * 100).toFixed(0)}%` : 'N/A'}
                        </div>
                      </div>

                      <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                        <div className="text-[10px] uppercase font-bold text-[#89977A]">Pass^{exp.repetitions_k} (Strict)</div>
                        <div className="text-xl font-black text-[#E8DDC8]">
                          {latestRun.pass_to_k !== null ? `${(latestRun.pass_to_k * 100).toFixed(0)}%` : 'N/A'}
                        </div>
                      </div>

                      <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                        <div className="text-[10px] uppercase font-bold text-[#89977A]">Recovery Rate</div>
                        <div className="text-xl font-black text-[#C49A55]">
                          {latestRun.recovery_rate !== null && latestRun.recovery_rate !== undefined ? `${(latestRun.recovery_rate * 100).toFixed(0)}%` : 'N/A'}
                        </div>
                      </div>

                      <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                        <div className="text-[10px] uppercase font-bold text-[#89977A]">Mean Duration</div>
                        <div className="text-xl font-black text-[#E8DDC8]">
                          {latestRun.avg_duration_seconds}s
                        </div>
                      </div>

                      <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                        <div className="text-[10px] uppercase font-bold text-[#89977A]">Duration Variance</div>
                        <div className="text-xl font-black text-[#A7A393]">
                          {latestRun.duration_variance}s²
                        </div>
                      </div>
                    </div>

                    {/* Repeated Trials Breakdown */}
                    <div className="space-y-2">
                      <div className="text-xs font-bold uppercase text-[#89977A] font-mono">
                        Trials Iteration Breakdown (k = {exp.repetitions_k})
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                        {latestRun.trials.map((trial) => (
                          <div
                            key={trial.id}
                            className={`p-3 rounded border text-xs font-mono flex items-center justify-between ${
                              trial.status === 'PASSED'
                                ? 'bg-[#1D2B1C] border-[#3B5436] text-[#C7D94C]'
                                : trial.status === 'RECOVERED'
                                ? 'bg-[#292A1A] border-[#5E5A2A] text-[#C49A55]'
                                : 'bg-[#2B1D1D] border-[#5E2A2A] text-[#FF725E]'
                            }`}
                          >
                            <div className="flex items-center gap-2">
                              {trial.status === 'PASSED' ? (
                                <CheckCircle2 size={15} />
                              ) : trial.status === 'RECOVERED' ? (
                                <CheckCircle2 size={15} />
                              ) : (
                                <XCircle size={15} />
                              )}
                              <span>Trial #{trial.trial_number}: <strong>{trial.status}</strong></span>
                            </div>
                            <span>{trial.duration_seconds}s</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-xs font-mono text-[#89977A]">
                    No execution trials recorded yet. Click Re-Execute to start evaluation.
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* New Experiment Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="reliabench-panel bg-[#1D211C] border border-[#F06B45] p-6 max-w-lg w-full">
            <h2 className="text-lg font-bold text-[#E8DDC8] mb-4 font-mono">Configure Benchmark Experiment</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                  Experiment Title
                </label>
                <input
                  type="text"
                  required
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded outline-none"
                  placeholder="e.g. Claude-Code: Stress Test with Tool Timeout"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                  Candidate Agent
                </label>
                <select
                  value={form.agent_id}
                  onChange={(e) => setForm({ ...form, agent_id: e.target.value })}
                  className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded"
                >
                  {agents.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.framework} / {a.adapter_type}) [{a.source_mode}]
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                  Benchmark Task
                </label>
                <select
                  value={form.benchmark_task_id}
                  onChange={(e) => setForm({ ...form, benchmark_task_id: e.target.value })}
                  className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded"
                >
                  {tasks.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} [{t.difficulty}]
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                  Controlled Failure Scenario (Optional)
                </label>
                <select
                  value={form.failure_scenario_id}
                  onChange={(e) => setForm({ ...form, failure_scenario_id: e.target.value })}
                  className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded"
                >
                  <option value="">None (Clean Baseline Execution)</option>
                  {failures.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.name} ({f.code}) [{f.severity}]
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                    Repetitions (k)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={form.repetitions_k}
                    onChange={(e) => setForm({ ...form, repetitions_k: parseInt(e.target.value) || 3 })}
                    className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded"
                  />
                  <span className="text-[10px] text-[#89977A]">Calculates Pass@k & Pass^k</span>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                    Timeout (Seconds)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="600"
                    value={form.timeout_seconds}
                    onChange={(e) => setForm({ ...form, timeout_seconds: parseInt(e.target.value) || 180 })}
                    className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-[#2D332B]">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-[#2D332B] text-xs text-[#A7A393] font-bold uppercase font-mono"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="reliabench-btn reliabench-btn-persimmon"
                >
                  Launch Experiment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
