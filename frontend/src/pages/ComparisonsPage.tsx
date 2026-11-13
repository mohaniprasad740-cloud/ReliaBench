import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Experiment } from '../services/types';
import { GitCompare, Trophy, TrendingUp, AlertTriangle, ShieldAlert } from 'lucide-react';

export const ComparisonsPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [comparisonResults, setComparisonResults] = useState<any[]>([]);
  const [isCompatible, setIsCompatible] = useState<boolean>(true);
  const [compatibilityWarning, setCompatibilityWarning] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getExperiments()
      .then((exps) => {
        setExperiments(exps);
        const initial = exps.slice(0, 3).map((e) => e.id);
        setSelectedIds(initial);
        if (initial.length > 0) {
          api.getComparisons(initial).then((res) => {
            setComparisonResults(res.comparisons);
            setIsCompatible(res.is_compatible);
            setCompatibilityWarning(res.compatibility_warning);
          });
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const handleToggle = async (id: string) => {
    let next: string[];
    if (selectedIds.includes(id)) {
      if (selectedIds.length === 1) return;
      next = selectedIds.filter((item) => item !== id);
    } else {
      next = [...selectedIds, id];
    }
    setSelectedIds(next);
    const res = await api.getComparisons(next);
    setComparisonResults(res.comparisons);
    setIsCompatible(res.is_compatible);
    setCompatibilityWarning(res.compatibility_warning);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="pb-6 border-b border-[#2D332B]">
        <h1 className="text-2xl font-black text-[#E8DDC8] flex items-center gap-2">
          <GitCompare size={26} className="text-[#C49A55]" />
          <span>Agent Comparison Matrix</span>
        </h1>
        <p className="text-xs text-[#A7A393] font-sans mt-0.5">
          Side-by-side reliability analysis under identical benchmark conditions, repeated trials, and injected faults.
        </p>
      </div>

      {/* Select Experiments Bar */}
      {experiments.length === 0 ? (
        <div className="reliabench-panel p-10 text-center">
          <GitCompare size={40} className="text-[#89977A] mx-auto mb-4" />
          <h3 className="text-lg font-bold text-[#E8DDC8] mb-2">No experiments available for comparison</h3>
          <p className="text-xs text-[#A7A393] max-w-lg mx-auto">
            Run at least two benchmark experiments on different agents (or the same agent under different conditions) to begin side-by-side reliability comparison.
          </p>
        </div>
      ) : experiments.length === 1 ? (
        <div className="reliabench-panel p-8 text-center">
          <GitCompare size={36} className="text-[#C49A55] mx-auto mb-3" />
          <h3 className="text-base font-bold text-[#E8DDC8] mb-2">One experiment recorded</h3>
          <p className="text-xs text-[#A7A393] max-w-md mx-auto">
            Run at least one more benchmark experiment to enable side-by-side comparison.
          </p>
        </div>
      ) : (
        <>
      <div className="reliabench-panel p-4">
        <div className="text-[10px] uppercase font-bold text-[#89977A] mb-2 font-mono">
          Select Experiments to Compare ({selectedIds.length} Selected)
        </div>
        <div className="flex flex-wrap gap-2">
          {experiments.map((exp) => {
            const isSelected = selectedIds.includes(exp.id);
            return (
              <button
                key={exp.id}
                onClick={() => handleToggle(exp.id)}
                className={`px-3 py-1.5 text-xs font-mono font-bold rounded border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-[#1D211C] text-[#C7D94C] border-[#3B5436] shadow-[2px_2px_0px_0px_#10120F]'
                    : 'bg-[#141713] text-[#A7A393] border-[#2D332B] hover:border-slate-500'
                }`}
              >
                {exp.agent?.name} — {exp.title.slice(0, 30)}...
              </button>
            );
          })}
        </div>
      </div>

      {/* Incompatible Conditions Warning Banner */}
      {!isCompatible && compatibilityWarning && (
        <div className="bg-[#2B231D] border border-[#5E3F2A] p-4 rounded flex items-start gap-3 text-xs font-mono text-[#F06B45]">
          <AlertTriangle size={18} className="shrink-0 text-[#F06B45] mt-0.5" />
          <div>
            <strong>Cross-Condition Comparison Warning:</strong> {compatibilityWarning}
          </div>
        </div>
      )}

      {/* Comparison Table */}
      {comparisonResults.length > 0 && (
        <div className="reliabench-panel p-6 overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-[#2D332B] text-[10px] text-[#89977A] uppercase">
                <th className="py-3 px-4">Metric / Dimension</th>
                {comparisonResults.map((c, i) => (
                  <th key={i} className="py-3 px-4">
                    <div className="text-[#E8DDC8] text-sm font-black">{c.agent_name}</div>
                    <div className="text-[10px] text-[#89977A] font-normal truncate max-w-xs">{c.title}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#2D332B]/50">
              {/* Task & Setup */}
              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Benchmark Task</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4 text-[#A7A393]">{c.task_name}</td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Fault Injected</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4">
                    <span className={c.failure_injected !== 'None (Clean)' ? 'text-[#F06B45] font-bold' : 'text-[#89977A]'}>
                      {c.failure_injected}
                    </span>
                  </td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Repetitions (k)</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4">{c.repetitions_k}</td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Provenance</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                      c.source_mode === 'REAL_EXECUTION'
                        ? 'bg-[#1D2B1C] text-[#C7D94C] border border-[#3B5436]'
                        : 'bg-[#2B231D] text-[#F06B45] border border-[#5E3F2A]'
                    }`}>
                      {c.source_mode}
                    </span>
                  </td>
                ))}
              </tr>

              {/* Core Metrics */}
              <tr className="bg-[#141713]">
                <td className="py-3 px-4 font-bold text-[#C7D94C]">Pass Rate</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4 font-black text-base text-[#C7D94C]">
                    {c.pass_rate !== null ? `${(c.pass_rate * 100).toFixed(1)}%` : 'N/A'}
                  </td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">95% CI (Wilson Score)</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4 text-[#89977A]">
                    {c.ci_lower !== null && c.ci_lower !== undefined
                      ? `[${(c.ci_lower * 100).toFixed(0)}%, ${(c.ci_upper * 100).toFixed(0)}%]`
                      : 'N/A'}
                  </td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Pass@k (At least 1 success)</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4 font-bold text-[#E8DDC8]">
                    {c.pass_at_k !== null ? `${(c.pass_at_k * 100).toFixed(1)}%` : 'N/A'}
                  </td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Pass^k (All k succeed)</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4 font-bold text-[#E8DDC8]">
                    {c.pass_to_k !== null ? `${(c.pass_to_k * 100).toFixed(1)}%` : 'N/A'}
                  </td>
                ))}
              </tr>

              <tr className="bg-[#141713]">
                <td className="py-3 px-4 font-bold text-[#C49A55]">Fault Recovery Rate</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4 font-bold text-[#C49A55]">
                    {c.recovery_rate !== null ? `${(c.recovery_rate * 100).toFixed(1)}%` : 'Clean Run'}
                  </td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Mean Duration</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4">{c.avg_duration_seconds}s</td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Median Duration</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4">{c.median_duration_seconds}s</td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Duration Variance (s²)</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4 text-[#89977A]">{c.duration_variance}</td>
                ))}
              </tr>

              <tr>
                <td className="py-3 px-4 font-bold text-[#E8DDC8]">Avg Cost per Run (USD)</td>
                {comparisonResults.map((c, i) => (
                  <td key={i} className="py-3 px-4 text-[#C7D94C]">
                    {c.avg_cost_usd ? `$${c.avg_cost_usd.toFixed(4)}` : 'Not measured'}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}
        </>
      )}
    </div>
  );
};
