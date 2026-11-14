import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardSummary } from '../services/types';
import { useGuidedTour } from '../components/tour';
import {
  CheckCircle2,
  AlertTriangle,
  Clock,
  Layers,
  Bot,
  Activity,
  ArrowRight,
  ShieldAlert,
  SlidersHorizontal,
  Flame,
  Compass,
  Database,
  Cpu,
  Server,
  Search,
  HardDrive
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sourceFilter, setSourceFilter] = useState<string>('ALL');
  const { startTour } = useGuidedTour();

  useEffect(() => {
    api.getHealth().then(setHealth).catch(() => {});
  }, []);

  useEffect(() => {
    loadSummary(sourceFilter === 'ALL' ? undefined : sourceFilter);
  }, [sourceFilter]);

  const loadSummary = (mode?: string) => {
    setLoading(true);
    api.getDashboardSummary(mode)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64 font-mono text-xs text-[#C7D94C]">
        [ QUERYING RELIABENCH TELEMETRY ENGINE... ]
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="reliabench-panel p-6 border-red-800 bg-[#2B1D1D] text-red-300">
        <h3 className="font-bold text-base mb-1 font-mono">Failed to load platform telemetry</h3>
        <p className="text-xs font-mono">{error || 'Unknown error'}</p>
      </div>
    );
  }

  const isEmpty = data.total_experiments === 0 && data.total_agents === 0;

  if (isEmpty) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto">
        {/* Clean-State Onboarding */}
        <div data-tour="dashboard-header" className="flex flex-col items-center justify-center py-16">
          <div className="text-[11px] font-mono font-bold uppercase tracking-wider text-[#C7D94C] mb-4">
            OPERATIONAL WORKSPACE — CLEAN STATE
          </div>
          <h1 className="text-3xl font-black text-[#E8DDC8] tracking-tight text-center mb-2">
            Agent Reliability Overview
          </h1>
          <p className="text-sm text-[#A7A393] text-center max-w-lg mb-6">
            No agents registered and no experiments executed yet. Begin by registering an agent, exploring benchmark tasks, or taking the guided product tour.
          </p>

          <div className="flex gap-3 mb-8">
            <button
              onClick={() => startTour(0)}
              className="reliabench-btn reliabench-btn-persimmon flex items-center gap-2 cursor-pointer"
            >
              <Compass size={15} />
              <span>Start Guided Tour</span>
            </button>
            <Link
              to="/app/agents"
              className="reliabench-btn reliabench-btn-outline flex items-center gap-2"
            >
              <Bot size={15} />
              <span>Register First Agent</span>
            </Link>
          </div>

          <div data-tour="dashboard-metrics-strip" className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl">
            <Link to="/app/agents" className="reliabench-panel p-6 hover:border-[#C7D94C] transition-colors group cursor-pointer">
              <Bot size={28} className="text-[#F06B45] mb-3" />
              <h3 className="font-bold text-sm text-[#E8DDC8] mb-1">Register Your First Agent</h3>
              <p className="text-xs text-[#A7A393]">
                Add an agent endpoint, select a framework adapter, and validate connectivity.
              </p>
              <span className="text-xs font-mono font-bold text-[#C7D94C] mt-3 flex items-center gap-1 group-hover:underline">
                Go to Agent Registry <ArrowRight size={12} />
              </span>
            </Link>

            <Link to="/app/benchmarks" className="reliabench-panel p-6 hover:border-[#C7D94C] transition-colors group cursor-pointer">
              <Layers size={28} className="text-[#C49A55] mb-3" />
              <h3 className="font-bold text-sm text-[#E8DDC8] mb-1">Explore Benchmark Library</h3>
              <p className="text-xs text-[#A7A393]">
                Browse {data.total_benchmarks} challenge packs with multi-step tasks and failure scenarios.
              </p>
              <span className="text-xs font-mono font-bold text-[#C7D94C] mt-3 flex items-center gap-1 group-hover:underline">
                View Challenge Packs <ArrowRight size={12} />
              </span>
            </Link>

            <div className="reliabench-panel p-6 border-dashed">
              <Activity size={28} className="text-[#89977A] mb-3" />
              <h3 className="font-bold text-sm text-[#E8DDC8] mb-1">System Health</h3>
              <div className="text-xs font-mono space-y-1 text-[#A7A393]">
                <div className="flex justify-between">
                  <span>Harbor Runtime:</span>
                  <span className={data.harbor_status?.available ? "text-[#C7D94C] font-bold" : "text-[#C49A55] font-bold"}>
                    {data.harbor_status?.available ? "CLI Ready" : "Deterministic"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Bifrost Gateway:</span>
                  <span className={health?.adapters?.bifrost?.configured ? "text-[#C7D94C] font-bold" : "text-[#89977A] font-bold"}>
                    {health?.adapters?.bifrost?.configured ? "Active" : "Mock"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Tavily Search:</span>
                  <span className={health?.adapters?.tavily?.configured ? "text-[#C7D94C] font-bold" : "text-[#89977A] font-bold"}>
                    {health?.adapters?.tavily?.configured ? "Connected" : "Mock"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Challenge Packs:</span>
                  <span className="text-[#C7D94C] font-bold">{data.total_benchmarks} available</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Workspace Header & Provenance Mode Selector */}
      <div data-tour="dashboard-header" className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-6 border-b border-[#2D332B]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-[#C7D94C]">
              Operational Workspace
            </span>
            <span className="text-xs text-[#89977A]">·</span>
            <span className="text-[11px] font-mono text-[#A7A393]">
              {data.total_experiments} Experiments Executed
            </span>
          </div>
          <h1 className="text-2xl font-black text-[#E8DDC8] tracking-tight">
            Agent Reliability Overview
          </h1>
          <p className="text-xs text-[#A7A393] font-sans mt-0.5">
            Measure consistency, resilience, and execution behavior across repeated benchmark trials.
          </p>
        </div>

        {/* Source Mode Filter Toggle */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => startTour(0)}
            className="reliabench-btn reliabench-btn-outline text-xs py-1.5 px-3 flex items-center gap-1.5"
            title="Start Guided Product Tour"
          >
            <Compass size={14} className="text-[#C7D94C]" />
            <span>Product Tour</span>
          </button>

          <div className="flex items-center gap-2 bg-[#141713] p-1 border border-[#2D332B] rounded">
          <SlidersHorizontal size={14} className="text-[#89977A] ml-2" />
          <button
            onClick={() => setSourceFilter('ALL')}
            className={`px-3 py-1 text-xs font-mono font-bold rounded transition-colors ${
              sourceFilter === 'ALL'
                ? 'bg-[#1D211C] text-[#C7D94C] border border-[#3B5436]'
                : 'text-[#A7A393] hover:text-[#E8DDC8]'
            }`}
          >
            All Data
          </button>
          <button
            onClick={() => setSourceFilter('SIMULATOR')}
            className={`px-3 py-1 text-xs font-mono font-bold rounded transition-colors ${
              sourceFilter === 'SIMULATOR'
                ? 'bg-[#2B231D] text-[#F06B45] border border-[#5E3F2A]'
                : 'text-[#A7A393] hover:text-[#E8DDC8]'
            }`}
          >
            Simulator Data Only
          </button>
          <button
            onClick={() => setSourceFilter('REAL_EXECUTION')}
            className={`px-3 py-1 text-xs font-mono font-bold rounded transition-colors ${
              sourceFilter === 'REAL_EXECUTION'
                ? 'bg-[#1D2B1C] text-[#C7D94C] border border-[#3B5436]'
                : 'text-[#A7A393] hover:text-[#E8DDC8]'
            }`}
          >
            Real Verified Runs
          </button>
        </div>
        </div>
      </div>

      {/* System Health & Adapter Topology Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 p-3 bg-[#111310] border border-[#2D332B] rounded">
        <div className="flex items-center gap-2.5">
          <Database size={15} className="text-[#C7D94C] shrink-0" />
          <div className="min-w-0">
            <div className="text-[10px] uppercase font-mono text-[#89977A] font-bold truncate">Database</div>
            <div className="text-xs font-mono font-bold text-[#E8DDC8] truncate">
              {health?.database === 'connected' ? 'Connected' : 'Active (SQLite)'}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Cpu size={15} className={data.harbor_status?.available ? "text-[#C7D94C] shrink-0" : "text-[#C49A55] shrink-0"} />
          <div className="min-w-0">
            <div className="text-[10px] uppercase font-mono text-[#89977A] font-bold truncate">Harbor Runtime</div>
            <div className="text-xs font-mono font-bold text-[#E8DDC8] truncate">
              {data.harbor_status?.available ? 'Harbor CLI Ready' : 'Deterministic Mode'}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Server size={15} className={health?.adapters?.bifrost?.configured ? "text-[#C7D94C] shrink-0" : "text-[#89977A] shrink-0"} />
          <div className="min-w-0">
            <div className="text-[10px] uppercase font-mono text-[#89977A] font-bold truncate">Bifrost Gateway</div>
            <div className="text-xs font-mono font-bold text-[#E8DDC8] truncate">
              {health?.adapters?.bifrost?.configured ? 'Active (Telemetry)' : 'Direct / Mock'}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Search size={15} className={health?.adapters?.tavily?.configured ? "text-[#C7D94C] shrink-0" : "text-[#89977A] shrink-0"} />
          <div className="min-w-0">
            <div className="text-[10px] uppercase font-mono text-[#89977A] font-bold truncate">Tavily Search</div>
            <div className="text-xs font-mono font-bold text-[#E8DDC8] truncate">
              {health?.adapters?.tavily?.configured ? 'API Connected' : 'Mock Cache'}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <HardDrive size={15} className="text-[#C7D94C] shrink-0" />
          <div className="min-w-0">
            <div className="text-[10px] uppercase font-mono text-[#89977A] font-bold truncate">Artifact Storage</div>
            <div className="text-xs font-mono font-bold text-[#E8DDC8] truncate">
              Local / Vercel Blob
            </div>
          </div>
        </div>
      </div>

      {/* Primary Analytical Metrics Strip */}
      <div data-tour="dashboard-metrics-strip" className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {/* Pass Rate */}
        <div className="reliabench-panel p-4 border-l-3 border-l-[#C7D94C]">
          <div className="text-[10px] uppercase font-bold text-[#A7A393] font-mono">
            Overall Pass Rate
          </div>
          <div className="text-3xl font-black font-mono text-[#C7D94C] mt-1">
            {data.overall_pass_rate !== null ? `${(data.overall_pass_rate * 100).toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-[10px] text-[#89977A] font-mono mt-1">
            N = {data.total_experiments} experiments
          </div>
        </div>

        {/* Mean Duration */}
        <div className="reliabench-panel p-4 border-l-3 border-l-[#F06B45]">
          <div className="text-[10px] uppercase font-bold text-[#A7A393] font-mono">
            Mean Duration
          </div>
          <div className="text-3xl font-black font-mono text-[#E8DDC8] mt-1">
            {data.average_duration_seconds}s
          </div>
          <div className="text-[10px] text-[#89977A] font-mono mt-1">
            Median: {data.median_duration_seconds}s
          </div>
        </div>

        {/* Total Agents */}
        <div className="reliabench-panel p-4 border-l-3 border-l-[#C49A55]">
          <div className="text-[10px] uppercase font-bold text-[#A7A393] font-mono">
            Registered Agents
          </div>
          <div className="text-3xl font-black font-mono text-[#E8DDC8] mt-1">
            {data.total_agents}
          </div>
          <div className="text-[10px] text-[#89977A] font-mono mt-1">
            Harbor, AutoGen, Custom
          </div>
        </div>

        {/* Benchmark Tasks */}
        <div className="reliabench-panel p-4 border-l-3 border-l-[#89977A]">
          <div className="text-[10px] uppercase font-bold text-[#A7A393] font-mono">
            Benchmark Tasks
          </div>
          <div className="text-3xl font-black font-mono text-[#E8DDC8] mt-1">
            {data.total_benchmarks}
          </div>
          <div className="text-[10px] text-[#89977A] font-mono mt-1">
            Multi-turn challenge packs
          </div>
        </div>

        {/* Cost per Success */}
        <div className="reliabench-panel p-4 border-l-3 border-l-[#A7A393]">
          <div className="text-[10px] uppercase font-bold text-[#A7A393] font-mono">
            Cost per Success
          </div>
          <div className="text-3xl font-black font-mono text-[#C7D94C] mt-1">
            {data.average_cost_usd !== null && data.average_cost_usd !== undefined ? `$${data.average_cost_usd.toFixed(4)}` : 'Not measured'}
          </div>
          <div className="text-[10px] text-[#89977A] font-mono mt-1">
            Token telemetry attributed
          </div>
        </div>
      </div>

      {/* Main Analytical Section: Visual Chart & Recorded Failure Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Reliability Visualization */}
        <div className="lg:col-span-2 reliabench-panel p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-base font-bold text-[#E8DDC8] flex items-center gap-2">
                <Activity size={18} className="text-[#C7D94C]" />
                <span>Reliability & Recovery Rate by Category</span>
              </h2>
              <p className="text-xs text-[#A7A393] font-sans">
                Baseline pass rate vs. observed recovery under controlled failure injection
              </p>
            </div>
            <span className="text-[10px] font-mono text-[#89977A] uppercase bg-[#141713] px-2.5 py-1 border border-[#2D332B]">
              Wilson Score Modeled
            </span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.reliability_distribution}>
                <XAxis dataKey="category" stroke="#89977A" fontSize={11} fontStyle="mono" />
                <YAxis stroke="#89977A" fontSize={11} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} fontStyle="mono" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1D211C', borderColor: '#2D332B', color: '#E8DDC8', fontSize: '11px', fontFamily: 'monospace' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
                <Bar dataKey="pass_rate" name="Pass Rate (Clean)" fill="#F06B45" radius={[2, 2, 0, 0]} />
                <Bar dataKey="recovery_rate" name="Recovery Rate (Post-Fault)" fill="#C7D94C" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recorded Failure Activity Feed */}
        <div className="reliabench-panel p-6 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-base font-bold text-[#E8DDC8] flex items-center gap-2">
                <AlertTriangle size={18} className="text-[#F06B45]" />
                <span>Recorded Failure Activity</span>
              </h2>
            </div>
            <p className="text-xs text-[#A7A393] mb-4 font-sans">
              Recent unhandled crash events and unrecovered fault injection trials
            </p>

            <div className="space-y-3">
              {data.recent_failures.length === 0 ? (
                <div className="text-xs text-[#89977A] font-mono p-4 bg-[#141713] border border-[#2D332B] rounded text-center">
                  No active failure events recorded for this filter.
                </div>
              ) : (
                data.recent_failures.map((f, i) => (
                  <div key={i} className="p-3 bg-[#171A16] border border-[#2D332B] rounded">
                    <div className="flex justify-between items-center text-xs font-mono font-bold text-[#F06B45]">
                      <span>{f.agent_name}</span>
                      <span className="text-[10px] text-[#89977A]">
                        {new Date(f.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-xs text-[#E8DDC8] font-medium mt-1 truncate">
                      {f.experiment_title}
                    </div>
                    <div className="text-[10px] text-[#A7A393] font-mono mt-1">
                      {f.error_message}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <Link
            to="/app/traces"
            className="text-xs font-mono font-bold text-[#C7D94C] flex items-center gap-1 mt-4 hover:underline"
          >
            <span>Open Trace Explorer</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>

      {/* Recent Benchmark Experiments Table */}
      <div className="reliabench-panel p-6">
        <div className="flex justify-between items-center mb-4 pb-3 border-b border-[#2D332B]">
          <div>
            <h2 className="text-base font-bold text-[#E8DDC8]">Recent Benchmark Experiments</h2>
            <p className="text-xs text-[#A7A393]">Evaluated under repeated execution constraints and controlled faults</p>
          </div>
          <Link to="/app/experiments" className="text-xs font-mono font-bold text-[#F06B45] hover:underline">
            View All Experiments &rarr;
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-[#2D332B] text-[#89977A] uppercase text-[10px]">
                <th className="py-2.5 px-3">Experiment</th>
                <th className="py-2.5 px-3">Agent</th>
                <th className="py-2.5 px-3">Benchmark Task</th>
                <th className="py-2.5 px-3">Reps (k)</th>
                <th className="py-2.5 px-3">Pass Rate</th>
                <th className="py-2.5 px-3">95% CI (Wilson)</th>
                <th className="py-2.5 px-3">Recovery</th>
                <th className="py-2.5 px-3">Provenance</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#2D332B]/50">
              {data.recent_experiments.map((exp) => {
                const latestRun = exp.runs && exp.runs.length > 0 ? exp.runs[exp.runs.length - 1] : null;
                return (
                  <tr key={exp.id} className="hover:bg-[#1A1E19] transition-colors">
                    <td className="py-3 px-3 font-bold text-[#E8DDC8]">{exp.title}</td>
                    <td className="py-3 px-3 text-[#C49A55]">{exp.agent?.name || 'N/A'}</td>
                    <td className="py-3 px-3 text-[#A7A393] truncate max-w-xs">{exp.benchmark_task?.name || 'N/A'}</td>
                    <td className="py-3 px-3">{exp.repetitions_k}</td>
                    <td className="py-3 px-3">
                      {latestRun && latestRun.pass_rate !== null ? (
                        <span className="font-bold text-[#C7D94C]">
                          {(latestRun.pass_rate * 100).toFixed(0)}%
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="py-3 px-3 text-[#89977A]">
                      {latestRun && latestRun.ci_lower !== undefined && latestRun.ci_lower !== null
                        ? `[${(latestRun.ci_lower * 100).toFixed(0)}%, ${(latestRun.ci_upper! * 100).toFixed(0)}%]`
                        : 'N/A'}
                    </td>
                    <td className="py-3 px-3 text-[#E8DDC8]">
                      {latestRun && latestRun.recovery_rate !== null && latestRun.recovery_rate !== undefined
                        ? `${(latestRun.recovery_rate * 100).toFixed(0)}%`
                        : 'Clean Run'}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                        exp.source_mode === 'REAL_EXECUTION'
                          ? 'bg-[#1D2B1C] text-[#C7D94C] border border-[#3B5436]'
                          : 'bg-[#2B231D] text-[#F06B45] border border-[#5E3F2A]'
                      }`}>
                        {exp.source_mode}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#142B20] text-[#C7D94C] border border-[#234A35]">
                        {exp.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
