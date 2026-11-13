import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ProvenanceBadge } from '../components/ui/ProvenanceBadge';
import {
  Layers,
  ChevronRight,
  ShieldCheck,
  Play,
  Clock,
  Terminal,
  Activity,
  AlertTriangle,
  RotateCcw,
  Zap,
} from 'lucide-react';

export const BenchmarksPage: React.FC = () => {
  const [packs, setPacks] = useState<any[]>([]);
  const [selectedPack, setSelectedPack] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  // Runner state
  const [profile, setProfile] = useState<'fragile' | 'retrying' | 'resilient'>('resilient');
  const [k, setK] = useState<number>(3);
  const [seed, setSeed] = useState<number>(42);
  const [faultKind, setFaultKind] = useState<string>('');
  const [atStep, setAtStep] = useState<number | undefined>(undefined);
  const [toolName, setToolName] = useState<string>('');
  const [running, setRunning] = useState(false);
  const [scorecard, setScorecard] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api.getPacks()
      .then((data) => {
        setPacks(data);
        if (data.length > 0) setSelectedPack(data[0]);
      })
      .catch((err) => setErrorMsg(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleLaunchRun = async () => {
    if (!selectedPack) return;
    setRunning(true);
    setErrorMsg(null);
    try {
      const res = await api.runPack(selectedPack.id, {
        profile,
        k: Number(k),
        seed: Number(seed),
        fault_kind: faultKind || undefined,
        at_step: atStep ? Number(atStep) : undefined,
        tool: toolName || undefined,
        probability: 1.0,
      });
      setScorecard(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Run execution failed');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div data-tour="benchmarks-header" className="flex justify-between items-center pb-6 border-b border-[#2D332B]">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-[#E8DDC8] flex items-center gap-2">
              <Layers size={26} className="text-[#C49A55]" />
              <span>Challenge Pack Library</span>
            </h1>
            <ProvenanceBadge mode="DETERMINISTIC_HARNESS" />
          </div>
          <p className="text-xs text-[#A7A393] font-sans mt-0.5">
            Framework-independent challenge packs with explicit preconditions ('requires') and multi-turn validators.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="font-mono text-xs text-[#C7D94C]">[ LOADING CHALLENGE PACKS... ]</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Pack Selector List */}
          <div className="space-y-3 lg:col-span-1">
            <div className="text-xs font-mono font-bold text-[#89977A] uppercase tracking-wider mb-2">
              Available Packs ({packs.length})
            </div>
            {packs.map((p) => {
              const isSelected = selectedPack?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => {
                    setSelectedPack(p);
                    setScorecard(null);
                  }}
                  className={`p-4 rounded border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-[#1D211C] border-[#F06B45]'
                      : 'bg-[#141713] border-[#2D332B] hover:border-[#89977A]'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-[10px] font-mono font-bold text-[#C7D94C] uppercase">
                      {p.category}
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-mono border bg-[#292A1A] text-[#C49A55] border-[#5E5A2A]">
                      {p.difficulty}
                    </span>
                  </div>
                  <h3 className="font-bold text-sm text-[#E8DDC8] mb-1">{p.name}</h3>
                  <div className="text-[11px] font-mono text-[#89977A] flex items-center gap-3">
                    <span>{p.plan?.length || 0} steps</span>
                    <span>•</span>
                    <span>{p.tools?.length || 0} tools</span>
                    <span>•</span>
                    <span>{p.time_limit_seconds}s</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Column: Detail, Precondition Chain & Run Launcher */}
          {selectedPack && (
            <div className="lg:col-span-2 space-y-6">
              {/* Pack Detail Panel */}
              <div className="reliabench-panel p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className="text-[10px] font-mono font-bold text-[#C7D94C] uppercase tracking-wider">
                      {selectedPack.category} • {selectedPack.difficulty}
                    </span>
                    <h2 className="text-xl font-black text-[#E8DDC8]">{selectedPack.name}</h2>
                  </div>
                  <ProvenanceBadge mode="DETERMINISTIC_HARNESS" />
                </div>

                <div className="space-y-3 mb-6">
                  <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                    <div className="text-[10px] font-mono uppercase font-bold text-[#F06B45] mb-1">
                      Task Instruction
                    </div>
                    <div className="text-xs text-[#E8DDC8] font-mono">{selectedPack.instruction}</div>
                  </div>

                  <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                    <div className="text-[10px] font-mono uppercase font-bold text-[#C7D94C] mb-1">
                      Expected Outcome & Verifiers
                    </div>
                    <div className="text-xs text-[#E8DDC8] font-mono">{selectedPack.expected_outcome}</div>
                  </div>
                </div>

                {/* Precondition Chain (Plan with requires) */}
                <div className="mb-6">
                  <div className="text-xs font-mono font-bold text-[#E8DDC8] mb-2 uppercase flex items-center gap-1.5">
                    <Terminal size={14} className="text-[#C49A55]" />
                    Reference Plan & Precondition Chain
                  </div>
                  <div className="space-y-2">
                    {selectedPack.plan?.map((step: any, sIdx: number) => (
                      <div key={step.id || sIdx} className="bg-[#141713] p-3 rounded border border-[#2D332B] text-xs">
                        <div className="flex items-center justify-between font-mono mb-1">
                          <span className="text-[#F06B45] font-bold">Step {sIdx + 1}: {step.tool}</span>
                          {step.requires ? (
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#2B1D1D] text-[#FF725E] border border-[#5E2A2A]">
                              requires: "{step.requires.substring(0, 35)}..."
                            </span>
                          ) : (
                            <span className="text-[10px] text-[#89977A]">requires: None (Root)</span>
                          )}
                        </div>
                        <div className="text-[#A7A393] mb-1">{step.thought}</div>
                        <div className="text-[11px] font-mono text-[#89977A]">
                          Expected Obs: {step.observation}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Run Launcher Form */}
                <div data-tour="benchmarks-run-card" className="bg-[#181C17] p-5 rounded border border-[#C49A55]/40 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-[#E8DDC8] font-mono uppercase flex items-center gap-2">
                      <Zap size={16} className="text-[#C7D94C]" />
                      Launch Reliability Test Run
                    </h3>
                    <span className="text-[11px] font-mono text-[#89977A]">Seeded deterministic harness</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs font-mono">
                    <div>
                      <label className="block text-[#A7A393] uppercase mb-1">Agent Profile</label>
                      <select
                        value={profile}
                        onChange={(e) => setProfile(e.target.value as any)}
                        className="w-full bg-[#141713] border border-[#2D332B] px-2 py-1.5 rounded text-[#E8DDC8]"
                      >
                        <option value="fragile">fragile (0-retry, no fallback)</option>
                        <option value="retrying">retrying (2 retries, guarded)</option>
                        <option value="resilient">resilient (3 retries, fallback)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[#A7A393] uppercase mb-1">Repetitions (k)</label>
                      <input
                        type="number"
                        min={1}
                        max={10}
                        value={k}
                        onChange={(e) => setK(Number(e.target.value))}
                        className="w-full bg-[#141713] border border-[#2D332B] px-2 py-1.5 rounded text-[#E8DDC8]"
                      />
                    </div>

                    <div>
                      <label className="block text-[#A7A393] uppercase mb-1">Deterministic Seed</label>
                      <input
                        type="number"
                        value={seed}
                        onChange={(e) => setSeed(Number(e.target.value))}
                        className="w-full bg-[#141713] border border-[#2D332B] px-2 py-1.5 rounded text-[#E8DDC8]"
                      />
                    </div>

                    <div>
                      <label className="block text-[#A7A393] uppercase mb-1">Fault Kind</label>
                      <select
                        value={faultKind}
                        onChange={(e) => setFaultKind(e.target.value)}
                        className="w-full bg-[#141713] border border-[#2D332B] px-2 py-1.5 rounded text-[#E8DDC8]"
                      >
                        <option value="">None (Clean Run)</option>
                        <option value="TOOL_ERROR">TOOL_ERROR</option>
                        <option value="TOOL_TIMEOUT">TOOL_TIMEOUT</option>
                        <option value="MODEL_UNAVAILABLE">MODEL_UNAVAILABLE</option>
                        <option value="MISLEADING_INSTRUCTION">MISLEADING_INSTRUCTION</option>
                      </select>
                    </div>
                  </div>

                  {faultKind && (
                    <div className="grid grid-cols-2 gap-3 text-xs font-mono pt-2 border-t border-[#2D332B]">
                      <div>
                        <label className="block text-[#A7A393] uppercase mb-1">Fault at Step (Optional)</label>
                        <input
                          type="number"
                          placeholder="e.g. 3"
                          value={atStep || ''}
                          onChange={(e) => setAtStep(e.target.value ? Number(e.target.value) : undefined)}
                          className="w-full bg-[#141713] border border-[#2D332B] px-2 py-1.5 rounded text-[#E8DDC8]"
                        />
                      </div>
                      <div>
                        <label className="block text-[#A7A393] uppercase mb-1">Target Tool (Optional)</label>
                        <input
                          type="text"
                          placeholder="e.g. update_quarantine_config"
                          value={toolName}
                          onChange={(e) => setToolName(e.target.value)}
                          className="w-full bg-[#141713] border border-[#2D332B] px-2 py-1.5 rounded text-[#E8DDC8]"
                        />
                      </div>
                    </div>
                  )}

                  <div className="flex justify-end pt-2">
                    <button
                      onClick={handleLaunchRun}
                      disabled={running}
                      className="reliabench-btn reliabench-btn-persimmon flex items-center gap-2"
                    >
                      {running ? <RotateCcw className="animate-spin" size={14} /> : <Play size={14} />}
                      <span>{running ? 'Executing Deterministic Trials...' : 'Execute Challenge Run'}</span>
                    </button>
                  </div>
                </div>

                {errorMsg && (
                  <div className="mt-4 p-3 rounded bg-[#2B1D1D] border border-[#5E2A2A] text-xs font-mono text-[#FF725E]">
                    {errorMsg}
                  </div>
                )}

                {/* Scorecard Results */}
                {scorecard && (
                  <div className="mt-6 p-5 rounded border border-[#C7D94C] bg-[#141713] space-y-4">
                    <div className="flex justify-between items-center pb-3 border-b border-[#2D332B]">
                      <div className="font-mono text-sm font-bold text-[#E8DDC8] flex items-center gap-2">
                        <Activity size={16} className="text-[#C7D94C]" />
                        <span>Execution Scorecard ({scorecard.agent_name})</span>
                      </div>
                      <ProvenanceBadge mode={scorecard.source_mode} />
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-center">
                      <div className="p-3 bg-[#1D211C] rounded border border-[#2D332B]">
                        <div className="text-[10px] text-[#A7A393] uppercase">Pass Rate (Wilson 95% CI)</div>
                        <div className="text-xl font-black text-[#E8DDC8]">
                          {(scorecard.pass_rate * 100).toFixed(0)}%
                        </div>
                        <div className="text-[10px] text-[#89977A]">
                          [{scorecard.wilson_lower.toFixed(2)} - {scorecard.wilson_upper.toFixed(2)}]
                        </div>
                      </div>

                      <div className="p-3 bg-[#1D211C] rounded border border-[#2D332B]">
                        <div className="text-[10px] text-[#A7A393] uppercase">Pass@k vs Pass^k</div>
                        <div className="text-xl font-black text-[#C7D94C]">
                          {scorecard.pass_at_k.toFixed(2)} / {scorecard.pass_pow_k.toFixed(2)}
                        </div>
                        <div className="text-[10px] text-[#89977A]">
                          {scorecard.pass_pow_k <= scorecard.pass_at_k ? 'pass^k ≤ pass@k confirmed' : ''}
                        </div>
                      </div>

                      <div className="p-3 bg-[#1D211C] rounded border border-[#2D332B]">
                        <div className="text-[10px] text-[#A7A393] uppercase">Recovery Rate</div>
                        <div className="text-xl font-black text-[#F06B45]">
                          {(scorecard.recovery_rate * 100).toFixed(0)}%
                        </div>
                        <div className="text-[10px] text-[#89977A]">
                          Faults injected: {scorecard.faults_injected_count}
                        </div>
                      </div>

                      <div className="p-3 bg-[#1D211C] rounded border border-[#2D332B]">
                        <div className="text-[10px] text-[#A7A393] uppercase">Cost & Tokens</div>
                        <div className="text-xl font-black text-[#E8DDC8]">
                          ${scorecard.total_cost_usd.toFixed(5)}
                        </div>
                        <div className="text-[10px] text-[#89977A]">
                          {scorecard.total_tokens} tokens
                        </div>
                      </div>
                    </div>

                    {/* Taxonomy Breakdown */}
                    {Object.keys(scorecard.taxonomy_counts || {}).length > 0 && (
                      <div className="p-3 bg-[#2B1D1D] rounded border border-[#5E2A2A] text-xs font-mono">
                        <div className="text-[#FF725E] font-bold uppercase mb-1 flex items-center gap-1.5">
                          <AlertTriangle size={14} />
                          Taxonomy Breakdown
                        </div>
                        {Object.entries(scorecard.taxonomy_counts).map(([cat, count]: [string, any]) => (
                          <div key={cat} className="flex justify-between text-[#E8DDC8] py-1 border-b border-[#3B2525]">
                            <span>{cat}</span>
                            <span className="font-bold">{count} trials</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
