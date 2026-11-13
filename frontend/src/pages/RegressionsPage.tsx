import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ProvenanceBadge } from '../components/ui/ProvenanceBadge';
import {
  ShieldAlert,
  Play,
  RotateCcw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
  Zap,
} from 'lucide-react';

export const RegressionsPage: React.FC = () => {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [replayingId, setReplayingId] = useState<string | null>(null);
  const [replayingAll, setReplayingAll] = useState(false);
  const [summary, setSummary] = useState<any | null>(null);
  const [targetAgent, setTargetAgent] = useState<'fragile' | 'resilient'>('resilient');

  const loadCases = () => {
    setLoading(true);
    api.getRegressions()
      .then(setCases)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadCases();
  }, []);

  const handleReplaySingle = async (caseId: string) => {
    setReplayingId(caseId);
    try {
      const res = await api.replayRegression(caseId, targetAgent);
      // Update case status in state
      setCases((prev) =>
        prev.map((c) => (c.id === caseId ? { ...c, status: res.status, last_replayed_at: new Date().toISOString() } : c))
      );
    } catch (err: any) {
      alert(err.message || 'Replay failed');
    } finally {
      setReplayingId(null);
    }
  };

  const handleReplayAll = async () => {
    setReplayingAll(true);
    setSummary(null);
    try {
      const res = await api.replayAllRegressions(targetAgent);
      setSummary(res);
      loadCases();
    } catch (err: any) {
      alert(err.message || 'Replay all failed');
    } finally {
      setReplayingAll(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div data-tour="regressions-header" className="flex flex-col md:flex-row justify-between md:items-center gap-4 pb-6 border-b border-[#2D332B]">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-[#E8DDC8] flex items-center gap-2">
              <ShieldAlert size={26} className="text-[#FF725E]" />
              <span>Regression Gates & Quarantine Replay</span>
            </h1>
            <ProvenanceBadge mode="DETERMINISTIC_HARNESS" />
          </div>
          <p className="text-xs text-[#A7A393] font-sans mt-0.5">
            Deterministic regression replay. Promoted failure cases must report FIXED before passing CI gates.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-[#141713] px-3 py-1.5 rounded border border-[#2D332B] text-xs font-mono">
            <span className="text-[#89977A]">Replay With:</span>
            <select
              value={targetAgent}
              onChange={(e) => setTargetAgent(e.target.value as any)}
              className="bg-transparent text-[#E8DDC8] font-bold outline-none"
            >
              <option value="resilient">resilient (3 retries, fallback)</option>
              <option value="fragile">fragile (0 retries)</option>
            </select>
          </div>

          <button
            onClick={handleReplayAll}
            disabled={replayingAll}
            className="reliabench-btn reliabench-btn-persimmon flex items-center gap-2"
          >
            {replayingAll ? <RotateCcw className="animate-spin" size={14} /> : <Play size={14} />}
            <span>Replay All Cases</span>
          </button>
        </div>
      </div>

      {/* Summary Banner if Replayed All */}
      {summary && (
        <div className="p-4 rounded border border-[#C49A55] bg-[#1D211C] grid grid-cols-4 gap-4 font-mono text-center text-xs">
          <div>
            <div className="text-[#A7A393] uppercase">Total Gates</div>
            <div className="text-lg font-bold text-[#E8DDC8]">{summary.total}</div>
          </div>
          <div>
            <div className="text-[#C7D94C] uppercase">Fixed</div>
            <div className="text-lg font-bold text-[#C7D94C]">{summary.fixed}</div>
          </div>
          <div>
            <div className="text-[#FF725E] uppercase">Still Failing</div>
            <div className="text-lg font-bold text-[#FF725E]">{summary.still_failing}</div>
          </div>
          <div>
            <div className="text-[#89977A] uppercase">Active Profile</div>
            <div className="text-lg font-bold text-[#E8DDC8]">{targetAgent}</div>
          </div>
        </div>
      )}

      {/* Regression Case Cards */}
      {loading ? (
        <div className="font-mono text-xs text-[#C7D94C]">[ LOADING REGRESSION GATES... ]</div>
      ) : cases.length === 0 ? (
        <div className="reliabench-panel p-10 text-center">
          <ShieldAlert size={40} className="text-[#89977A] mx-auto mb-4" />
          <h3 className="text-lg font-bold text-[#E8DDC8] mb-2">No regression cases recorded</h3>
          <p className="text-xs text-[#A7A393] max-w-lg mx-auto">
            Regression cases are created when benchmark experiments reveal failure patterns. Run experiments with fault injection to populate the regression gate registry.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {cases.map((c) => {
            const isFixed = c.status === 'FIXED';
            const isReplaying = replayingId === c.id;

            return (
              <div
                key={c.id}
                className="reliabench-panel p-5 flex flex-col md:flex-row justify-between md:items-center gap-4"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-sm font-black text-[#E8DDC8]">{c.id}</span>
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border ${
                        isFixed
                          ? 'bg-[#1D2B1C] text-[#C7D94C] border-[#3B5436]'
                          : 'bg-[#2B1D1D] text-[#FF725E] border-[#5E2A2A]'
                      }`}
                    >
                      {isFixed ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                      {c.status}
                    </span>
                    <ProvenanceBadge mode="DETERMINISTIC_HARNESS" />
                  </div>

                  <p className="text-xs text-[#A7A393] font-sans">{c.description}</p>

                  <div className="flex flex-wrap items-center gap-3 text-[11px] font-mono text-[#89977A]">
                    <span>Pack: <strong className="text-[#E8DDC8]">{c.pack_id}</strong></span>
                    <span>•</span>
                    <span>Fault: <strong className="text-[#F06B45]">{c.fault_kind}</strong></span>
                    {c.at_step && <span>@ step {c.at_step}</span>}
                    {c.tool && <span>on tool <code className="text-[#C7D94C]">{c.tool}</code></span>}
                    <span>•</span>
                    <span>Expected: <strong className="text-[#FF725E]">{c.expected_failure_category}</strong></span>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <button
                    onClick={() => handleReplaySingle(c.id)}
                    disabled={isReplaying}
                    className="reliabench-btn reliabench-btn-outline flex items-center gap-1.5 text-xs"
                  >
                    {isReplaying ? <RotateCcw className="animate-spin" size={13} /> : <Play size={13} />}
                    <span>Replay Gate</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
