import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Experiment } from '../services/types';
import { FileText, Download, CheckCircle, Database } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExpId, setSelectedExpId] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getExperiments().then((exps) => {
      setExperiments(exps);
      if (exps.length > 0) {
        setSelectedExpId(exps[0].id);
      }
      setLoading(false);
    });
  }, []);

  const selectedExp = experiments.find((e) => e.id === selectedExpId);
  const latestRun = selectedExp?.runs?.[selectedExp.runs.length - 1];

  const handleExportJSON = () => {
    if (!selectedExp) return;
    const blob = new Blob([JSON.stringify(selectedExp, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reliabench_report_${selectedExp.id.slice(0, 8)}.json`;
    a.click();
  };

  const handleExportCSV = () => {
    if (!selectedExp || !latestRun) return;
    const headers = 'Experiment_ID,Agent,Task,Repetitions,PassRate,CiLower,CiUpper,PassAtK,PassToK,RecoveryRate,Duration,SourceMode\n';
    const row = `${selectedExp.id},${selectedExp.agent?.name},${selectedExp.benchmark_task?.name},${selectedExp.repetitions_k},${latestRun.pass_rate},${latestRun.ci_lower || 'N/A'},${latestRun.ci_upper || 'N/A'},${latestRun.pass_at_k},${latestRun.pass_to_k},${latestRun.recovery_rate || 'N/A'},${latestRun.avg_duration_seconds},${selectedExp.source_mode}\n`;
    const blob = new Blob([headers + row], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reliabench_report_${selectedExp.id.slice(0, 8)}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div data-tour="reports-header" className="flex justify-between items-center pb-6 border-b border-[#2D332B]">
        <div>
          <h1 className="text-2xl font-black text-[#E8DDC8] flex items-center gap-2">
            <FileText size={26} className="text-[#C7D94C]" />
            <span>Benchmark Reports & Certification</span>
          </h1>
          <p className="text-xs text-[#A7A393] font-sans mt-0.5">
            Evidence-backed reliability reports conforming to evaluation standards with JSON and CSV exports.
          </p>
        </div>

        {selectedExp && (
          <div className="flex gap-3">
            <button
              onClick={handleExportJSON}
              className="reliabench-btn reliabench-btn-outline"
            >
              <Download size={13} />
              <span>Export JSON</span>
            </button>
            <button
              onClick={handleExportCSV}
              className="reliabench-btn reliabench-btn-persimmon"
            >
              <Download size={13} />
              <span>Export CSV</span>
            </button>
          </div>
        )}
      </div>

      {/* Select Experiment */}
      {experiments.length === 0 ? (
        <div className="reliabench-panel p-10 text-center">
          <FileText size={40} className="text-[#89977A] mx-auto mb-4" />
          <h3 className="text-lg font-bold text-[#E8DDC8] mb-2">No reports available</h3>
          <p className="text-xs text-[#A7A393] max-w-md mx-auto">
            Benchmark reports are generated after experiments complete. Run an experiment to generate your first certification report.
          </p>
        </div>
      ) : (
        <>
      <div className="reliabench-panel p-4 flex items-center gap-3">
        <label className="text-xs font-bold uppercase font-mono text-[#89977A]">
          Select Experiment:
        </label>
        <select
          value={selectedExpId}
          onChange={(e) => setSelectedExpId(e.target.value)}
          className="bg-[#141713] border border-[#2D332B] px-3 py-1.5 text-xs text-[#E8DDC8] font-mono rounded max-w-md outline-none"
        >
          {experiments.map((e) => (
            <option key={e.id} value={e.id}>
              {e.title} [{e.agent?.name}] ({e.source_mode})
            </option>
          ))}
        </select>
      </div>

      {/* Report Preview */}
      {selectedExp ? (
        <div className="reliabench-panel p-8 space-y-6 bg-[#1D211C]">
          <div className="border-b border-[#2D332B] pb-4 flex justify-between items-start">
            <div>
              <div className="text-xs font-mono font-bold text-[#C7D94C] uppercase tracking-wider mb-1">
                Official Benchmark Certification
              </div>
              <h2 className="text-xl font-black text-[#E8DDC8]">{selectedExp.title}</h2>
              <div className="text-[11px] font-mono text-[#89977A] mt-1">
                Generated: {new Date(selectedExp.created_at).toUTCString()} · Experiment ID: {selectedExp.id}
              </div>
            </div>
            <div className="flex gap-2">
              <span className="px-3 py-1 rounded text-xs font-mono font-bold bg-[#142B20] text-[#C7D94C] border border-[#234A35]">
                {selectedExp.status}
              </span>
              <span className={`px-3 py-1 rounded text-xs font-mono font-bold border ${
                selectedExp.source_mode === 'REAL_EXECUTION'
                  ? 'bg-[#1D2B1C] text-[#C7D94C] border-[#3B5436]'
                  : 'bg-[#2B231D] text-[#F06B45] border-[#5E3F2A]'
              }`}>
                {selectedExp.source_mode}
              </span>
            </div>
          </div>

          {/* Test Setup Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-xs">
            <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
              <div className="text-[10px] uppercase font-bold text-[#89977A]">Agent Under Test</div>
              <div className="text-sm font-bold text-[#E8DDC8] mt-1">{selectedExp.agent?.name}</div>
              <div className="text-[10px] text-[#C49A55]">{selectedExp.agent?.framework} ({selectedExp.agent?.adapter_type})</div>
            </div>

            <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
              <div className="text-[10px] uppercase font-bold text-[#89977A]">Task Specification</div>
              <div className="text-sm font-bold text-[#E8DDC8] mt-1 truncate">{selectedExp.benchmark_task?.name}</div>
              <div className="text-[10px] text-[#89977A]">Difficulty: {selectedExp.benchmark_task?.difficulty}</div>
            </div>

            <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
              <div className="text-[10px] uppercase font-bold text-[#89977A]">Fault Injection</div>
              <div className="text-sm font-bold text-[#F06B45] mt-1">
                {selectedExp.failure_scenario?.name || 'Clean Baseline'}
              </div>
              <div className="text-[10px] text-[#89977A]">
                {selectedExp.failure_scenario ? selectedExp.failure_scenario.trigger_point : 'No fault'}
              </div>
            </div>

            <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
              <div className="text-[10px] uppercase font-bold text-[#89977A]">Statistical Constraints</div>
              <div className="text-sm font-bold text-[#E8DDC8] mt-1">k = {selectedExp.repetitions_k} Repetitions</div>
              <div className="text-[10px] text-[#89977A]">Timeout: {selectedExp.timeout_seconds}s</div>
            </div>
          </div>

          {/* Evaluated Metrics */}
          {latestRun && (
            <div className="space-y-4 font-mono">
              <h3 className="text-xs font-bold uppercase text-[#C7D94C]">
                Evaluated Reliability Results
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-[#141713] p-4 rounded border border-[#2D332B]">
                  <div className="text-xs text-[#89977A]">Pass Rate</div>
                  <div className="text-2xl font-black text-[#C7D94C] mt-1">
                    {latestRun.pass_rate !== null ? `${(latestRun.pass_rate * 100).toFixed(1)}%` : 'N/A'}
                  </div>
                  <div className="text-[10px] text-[#89977A] mt-1">{latestRun.successful_trials} / {latestRun.total_trials} passed</div>
                </div>

                <div className="bg-[#141713] p-4 rounded border border-[#2D332B]">
                  <div className="text-xs text-[#89977A]">Pass@{selectedExp.repetitions_k}</div>
                  <div className="text-2xl font-black text-[#E8DDC8] mt-1">
                    {latestRun.pass_at_k !== null ? `${(latestRun.pass_at_k * 100).toFixed(1)}%` : 'N/A'}
                  </div>
                  <div className="text-[10px] text-[#89977A] mt-1">Unbiased prob estimator</div>
                </div>

                <div className="bg-[#141713] p-4 rounded border border-[#2D332B]">
                  <div className="text-xs text-[#89977A]">Pass^{selectedExp.repetitions_k} (Strict)</div>
                  <div className="text-2xl font-black text-[#E8DDC8] mt-1">
                    {latestRun.pass_to_k !== null ? `${(latestRun.pass_to_k * 100).toFixed(1)}%` : 'N/A'}
                  </div>
                  <div className="text-[10px] text-[#89977A] mt-1">Fraction all k pass</div>
                </div>

                <div className="bg-[#141713] p-4 rounded border border-[#2D332B]">
                  <div className="text-xs text-[#89977A]">Recovery Rate</div>
                  <div className="text-2xl font-black text-[#C49A55] mt-1">
                    {latestRun.recovery_rate !== null && latestRun.recovery_rate !== undefined ? `${(latestRun.recovery_rate * 100).toFixed(1)}%` : 'N/A'}
                  </div>
                  <div className="text-[10px] text-[#89977A] mt-1">Post-fault recovery</div>
                </div>
              </div>
            </div>
          )}

          <div className="pt-4 border-t border-[#2D332B] text-xs font-mono text-[#89977A] flex justify-between items-center">
            <span>Reliabench Certification Framework v0.2.0 · Harbor v0.25.0 Adapter</span>
            <span>Provenance Hash: {selectedExp.id.slice(0, 16)}</span>
          </div>
        </div>
      ) : (
        <div className="reliabench-panel p-6 font-mono text-xs text-[#89977A]">
          No experiments recorded.
        </div>
      )}
        </>
      )}
    </div>
  );
};
