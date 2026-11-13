import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import { Experiment, ATIFTrajectory } from '../services/types';
import { Activity, Terminal, CheckCircle2, XCircle, ShieldCheck, Filter } from 'lucide-react';

export const TracesPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const runIdParam = searchParams.get('run_id');

  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(runIdParam);
  const [trajectory, setTrajectory] = useState<ATIFTrajectory | null>(null);
  const [selectedStepIndex, setSelectedStepIndex] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [filterSource, setFilterSource] = useState<string>('ALL'); // ALL, user, agent, system

  useEffect(() => {
    api.getExperiments().then((exps) => {
      setExperiments(exps);
      const firstValidRun = exps.flatMap((e) => e.runs)[0];
      const targetRunId = runIdParam || (firstValidRun ? firstValidRun.id : null);
      if (targetRunId) {
        setSelectedRunId(targetRunId);
        loadTrajectory(targetRunId);
      } else {
        setLoading(false);
      }
    });
  }, [runIdParam]);

  const loadTrajectory = async (runId: string) => {
    setLoading(true);
    try {
      const traj = await api.getRunTrajectory(runId);
      setTrajectory(traj);
      setSelectedStepIndex(0);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRun = (runId: string) => {
    setSelectedRunId(runId);
    loadTrajectory(runId);
  };

  const filteredSteps = trajectory
    ? trajectory.steps.filter((s) => filterSource === 'ALL' || s.source === filterSource)
    : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="pb-6 border-b border-[#2D332B]">
        <h1 className="text-2xl font-black text-[#E8DDC8] flex items-center gap-2">
          <Activity size={26} className="text-[#C7D94C]" />
          <span>Execution Trace Inspector (ATIF v1.8)</span>
        </h1>
        <p className="text-xs text-[#A7A393] font-sans mt-0.5">
          Inspect recorded-run evidence conforming to Harbor's Agent Trajectory Interchange Format (ATIF).
        </p>
      </div>

      {/* Select Run */}
      {experiments.length === 0 || experiments.flatMap((e) => e.runs).length === 0 ? (
        <div className="reliabench-panel p-10 text-center">
          <Terminal size={40} className="text-[#89977A] mx-auto mb-4" />
          <h3 className="text-lg font-bold text-[#E8DDC8] mb-2">No execution traces recorded</h3>
          <p className="text-xs text-[#A7A393] max-w-md mx-auto">
            Execution traces will appear here in ATIF v1.8 format after running a benchmark experiment.
          </p>
        </div>
      ) : (
        <div className="reliabench-panel p-4 flex flex-wrap gap-2 items-center">
          <span className="text-[10px] font-mono font-bold text-[#89977A] uppercase mr-2">
            Select Trial Run:
          </span>
          {experiments.flatMap((e) =>
            e.runs.map((r) => (
              <button
                key={r.id}
                onClick={() => handleSelectRun(r.id)}
                className={`px-3 py-1.5 text-xs font-mono font-bold rounded border transition-all cursor-pointer ${
                  selectedRunId === r.id
                    ? 'bg-[#1D211C] text-[#C7D94C] border-[#3B5436] shadow-[2px_2px_0px_0px_#10120F]'
                    : 'bg-[#141713] text-[#A7A393] border-[#2D332B] hover:border-slate-500'
                }`}
              >
                {e.agent?.name} — Run {r.id.slice(0, 8)} [{r.source_mode}]
              </button>
            ))
          )}
        </div>
      )}

      {loading ? (
        <div className="font-mono text-xs text-[#C7D94C]">[ PARSING ATIF TRAJECTORY ARTIFACTS... ]</div>
      ) : trajectory ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Step Timeline / Waterfall List */}
          <div className="reliabench-panel p-4 space-y-3 max-h-[700px] overflow-y-auto">
            <div className="flex justify-between items-center pb-2 border-b border-[#2D332B]">
              <div className="text-[10px] font-bold uppercase text-[#89977A] font-mono">
                Trajectory ({filteredSteps.length} Steps)
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setFilterSource('ALL')}
                  className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${
                    filterSource === 'ALL' ? 'bg-[#C7D94C] text-[#10120F]' : 'text-[#89977A]'
                  }`}
                >
                  ALL
                </button>
                <button
                  onClick={() => setFilterSource('agent')}
                  className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${
                    filterSource === 'agent' ? 'bg-[#F06B45] text-[#10120F]' : 'text-[#89977A]'
                  }`}
                >
                  AGENT
                </button>
                <button
                  onClick={() => setFilterSource('system')}
                  className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${
                    filterSource === 'system' ? 'bg-[#C49A55] text-[#10120F]' : 'text-[#89977A]'
                  }`}
                >
                  SYSTEM
                </button>
              </div>
            </div>

            {filteredSteps.map((step, idx) => {
              const isSelected = selectedStepIndex === idx;
              const isError = step.observation?.results?.some((r) => r.is_error);

              return (
                <div
                  key={step.step_id}
                  onClick={() => setSelectedStepIndex(idx)}
                  className={`p-3 rounded border cursor-pointer font-mono text-xs transition-all ${
                    isSelected
                      ? 'bg-[#141713] border-[#C7D94C] shadow-[2px_2px_0px_0px_#C7D94C]'
                      : 'bg-[#171A16] border-[#2D332B] hover:border-slate-500 text-[#A7A393]'
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-[#E8DDC8] flex items-center gap-1.5">
                      <span>Step #{step.step_id}</span>
                      <span
                        className={`px-1.5 py-0.2 rounded text-[9px] uppercase font-bold ${
                          step.source === 'user'
                            ? 'bg-[#1D211C] text-[#A7A393] border border-[#2D332B]'
                            : step.source === 'agent'
                            ? 'bg-[#2B231D] text-[#F06B45] border border-[#5E3F2A]'
                            : 'bg-[#1D2B1C] text-[#C7D94C] border border-[#3B5436]'
                        }`}
                      >
                        {step.source}
                      </span>
                    </span>
                    {isError && (
                      <span className="text-[10px] text-[#FF725E] font-bold">ERROR</span>
                    )}
                  </div>

                  <div className="truncate text-slate-300 text-[11px]">
                    {step.message || (step.tool_calls ? `Tool: ${step.tool_calls[0].function_name}` : 'Observation payload')}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Step Payload Inspector */}
          <div className="lg:col-span-2 reliabench-panel p-6 space-y-4">
            {filteredSteps[selectedStepIndex] ? (
              (() => {
                const s = filteredSteps[selectedStepIndex];
                return (
                  <div className="space-y-4 font-mono">
                    <div className="flex justify-between items-start pb-4 border-b border-[#2D332B]">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-black text-lg text-[#E8DDC8]">Step #{s.step_id}</h3>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-[#141713] text-[#C7D94C] border border-[#2D332B]">
                            Source: {s.source}
                          </span>
                        </div>
                        <div className="text-[10px] text-[#89977A] mt-1">
                          Timestamp: {new Date(s.timestamp).toLocaleTimeString()}
                        </div>
                      </div>

                      {s.metrics && (
                        <div className="text-right text-xs">
                          <div className="text-[#C7D94C] font-bold">
                            Tokens: {s.metrics.prompt_tokens + s.metrics.completion_tokens}
                          </div>
                          <div className="text-[#89977A] text-[10px]">
                            Cost: ${s.metrics.cost.toFixed(4)}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Agent Message / Plan */}
                    {s.message && (
                      <div className="space-y-1">
                        <div className="text-[10px] uppercase font-bold text-[#F06B45]">Message</div>
                        <div className="bg-[#141713] p-3 rounded border border-[#2D332B] text-xs text-[#E8DDC8]">
                          {s.message}
                        </div>
                      </div>
                    )}

                    {/* Reasoning Content */}
                    {s.reasoning_content && (
                      <div className="space-y-1">
                        <div className="text-[10px] uppercase font-bold text-[#C49A55]">Reasoning (Thinking)</div>
                        <div className="bg-[#141713] p-3 rounded border border-[#2D332B] text-xs text-[#A7A393]">
                          {s.reasoning_content}
                        </div>
                      </div>
                    )}

                    {/* Outbound Tool Calls */}
                    {s.tool_calls && s.tool_calls.length > 0 && (
                      <div className="space-y-2">
                        <div className="text-[10px] uppercase font-bold text-[#C7D94C]">Tool Invocations</div>
                        {s.tool_calls.map((tc, idx) => (
                          <div key={idx} className="bg-[#141713] p-3 rounded border border-[#2D332B] space-y-2">
                            <div className="text-xs font-bold text-[#E8DDC8] flex justify-between">
                              <span>Function: {tc.function_name}</span>
                              <span className="text-[#89977A] text-[10px]">ID: {tc.tool_call_id}</span>
                            </div>
                            <pre className="text-[11px] text-[#C7D94C] bg-black/40 p-2 rounded overflow-x-auto">
                              {JSON.stringify(tc.arguments, null, 2)}
                            </pre>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Environment Observation */}
                    {s.observation && (
                      <div className="space-y-2">
                        <div className="text-[10px] uppercase font-bold text-[#89977A]">Environment Observation</div>
                        {s.observation.results.map((r, idx) => (
                          <div
                            key={idx}
                            className={`p-3 rounded border text-xs space-y-1 ${
                              r.is_error
                                ? 'bg-[#2B1D1D] border-[#5E2A2A] text-[#FF725E]'
                                : 'bg-[#141713] border-[#2D332B] text-[#E8DDC8]'
                            }`}
                          >
                            <div className="flex justify-between text-[10px] text-[#89977A]">
                              <span>Result for {r.tool_call_id}</span>
                              <span className={r.is_error ? 'text-[#FF725E] font-bold' : 'text-[#C7D94C]'}>
                                {r.is_error ? 'ERROR' : 'SUCCESS'}
                              </span>
                            </div>
                            <div className="whitespace-pre-wrap">{r.content}</div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Raw ATIF JSON Payload */}
                    <div className="pt-4 border-t border-[#2D332B]">
                      <details className="text-xs text-[#89977A] cursor-pointer">
                        <summary className="font-bold hover:text-[#E8DDC8]">View Full Step ATIF JSON</summary>
                        <pre className="mt-2 p-3 bg-black/60 rounded border border-[#2D332B] text-[10px] text-slate-300 overflow-x-auto">
                          {JSON.stringify(s, null, 2)}
                        </pre>
                      </details>
                    </div>
                  </div>
                );
              })()
            ) : null}
          </div>
        </div>
      ) : (
        <div className="reliabench-panel p-6 font-mono text-xs text-[#89977A]">
          No recorded trajectory found. Execute a benchmark experiment to inspect ATIF execution traces.
        </div>
      )}
    </div>
  );
};
