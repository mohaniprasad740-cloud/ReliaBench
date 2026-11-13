import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Settings as SettingsIcon, ShieldCheck, Terminal, Cpu, Database, CheckCircle2, XCircle, Globe, Play } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tavilyTesting, setTavilyTesting] = useState(false);
  const [tavilyResult, setTavilyResult] = useState<any>(null);
  const [bifrostTesting, setBifrostTesting] = useState(false);
  const [bifrostResult, setBifrostResult] = useState<any>(null);

  const loadHealth = () => {
    setLoading(true);
    api.getHealth()
      .then(setHealth)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadHealth();
  }, []);

  const handleTestTavily = async () => {
    setTavilyTesting(true);
    setTavilyResult(null);
    try {
      const res = await api.testTavily();
      setTavilyResult(res);
      loadHealth();
    } catch (err: any) {
      setTavilyResult({ status: 'ERROR', message: err.message });
    } finally {
      setTavilyTesting(false);
    }
  };

  const handleTestBifrost = async () => {
    setBifrostTesting(true);
    setBifrostResult(null);
    try {
      const res = await api.testBifrost();
      setBifrostResult(res);
      loadHealth();
    } catch (err: any) {
      setBifrostResult({ status: 'ERROR', message: err.message });
    } finally {
      setBifrostTesting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="pb-6 border-b border-[#2D332B]">
        <h1 className="text-2xl font-black text-[#E8DDC8] flex items-center gap-2">
          <SettingsIcon size={26} className="text-[#89977A]" />
          <span>System Diagnostics & Adapters</span>
        </h1>
        <p className="text-xs text-[#A7A393] font-sans mt-0.5">
          Operational readiness and integration status of execution sandboxes, model gateways, and storage.
        </p>
      </div>

      {loading ? (
        <div className="font-mono text-xs text-[#C7D94C]">[ QUERYING SYSTEM INTEGRATIONS... ]</div>
      ) : health ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Harbor Adapter */}
          <div className="reliabench-panel p-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-[#2D332B]">
              <div className="flex items-center gap-2">
                <Terminal size={18} className="text-[#C7D94C]" />
                <h3 className="font-bold text-[#E8DDC8] text-base font-mono">Harbor Execution Engine</h3>
              </div>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                  health.adapters.harbor.available
                    ? 'bg-[#1D2B1C] text-[#C7D94C] border border-[#3B5436]'
                    : 'bg-[#2B231D] text-[#F06B45] border border-[#5E3F2A]'
                }`}
              >
                {health.adapters.harbor.mode}
              </span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1.5 border-b border-[#2D332B]/40 text-[#89977A]">
                <span>Required Version:</span>
                <span className="text-[#E8DDC8] font-bold">{health.adapters.harbor.required_version}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#2D332B]/40 text-[#89977A]">
                <span>CLI Installed:</span>
                <span className={health.adapters.harbor.available ? 'text-[#C7D94C]' : 'text-[#F06B45]'}>
                  {health.adapters.harbor.available ? 'YES' : 'NO (Using Simulator Runner)'}
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#2D332B]/40 text-[#89977A]">
                <span>Docker Sandbox Daemon:</span>
                <span className={health.adapters.harbor.docker_available ? 'text-[#C7D94C]' : 'text-[#C49A55]'}>
                  {health.adapters.harbor.docker_available ? 'AVAILABLE' : 'OFFLINE (Safe Host Mode)'}
                </span>
              </div>
              <div className="flex justify-between py-1.5 text-[#89977A]">
                <span>Trajectory Standard:</span>
                <span className="text-[#C7D94C]">ATIF-v1.8 Compatible</span>
              </div>
            </div>

            <p className="text-[11px] text-[#A7A393] font-sans">
              When Harbor CLI and Docker are active, trials run in isolated containers. Otherwise, Reliabench transparently switches to the deterministic Simulator Adapter to protect the host OS while maintaining full ATIF data fidelity.
            </p>
          </div>

          {/* Model Gateway (Bifrost) */}
          <div className="reliabench-panel p-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-[#2D332B]">
              <div className="flex items-center gap-2">
                <Cpu size={18} className="text-[#F06B45]" />
                <h3 className="font-bold text-[#E8DDC8] text-base font-mono">Bifrost Model Gateway</h3>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#141713] text-[#89977A] border border-[#2D332B]">
                {health.adapters.bifrost.status}
              </span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1.5 border-b border-[#2D332B]/40 text-[#89977A]">
                <span>Gateway Status:</span>
                <span className="text-[#89977A]">{health.adapters.bifrost.status}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#2D332B]/40 text-[#89977A]">
                <span>Target Endpoint:</span>
                <span className="text-[#E8DDC8]">{health.adapters.bifrost.endpoint}</span>
              </div>
              <div className="flex justify-between py-1.5 text-[#89977A]">
                <span>Telemetry Accounting:</span>
                <span className="text-[#C7D94C]">Token / Latency Tracking</span>
              </div>
            </div>

            <p className="text-[11px] text-[#A7A393] font-sans">
              Bifrost provides unified OpenAI-compatible routing and microsecond-level request accounting. It is optional for the initial milestone and can be enabled via <code className="text-[#C7D94C]">ENABLE_BIFROST_GATEWAY=true</code>.
            </p>

            <div className="pt-2 border-t border-[#2D332B] flex justify-between items-center">
              <button
                onClick={handleTestBifrost}
                disabled={bifrostTesting}
                className="reliabench-btn reliabench-btn-persimmon text-xs py-1 px-3 flex items-center gap-1.5 cursor-pointer"
              >
                <Play size={12} />
                <span>{bifrostTesting ? 'Testing Gateway...' : 'Test Connection'}</span>
              </button>
              {bifrostResult && (
                <span className={`text-[10px] font-mono ${bifrostResult.status === 'READY' ? 'text-[#C7D94C]' : 'text-[#89977A]'}`}>
                  {bifrostResult.message || bifrostResult.status}
                </span>
              )}
            </div>
          </div>

          {/* Web Research Tool (Tavily) */}
          <div className="reliabench-panel p-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-[#2D332B]">
              <div className="flex items-center gap-2">
                <Globe size={18} className="text-[#C7D94C]" />
                <h3 className="font-bold text-[#E8DDC8] text-base font-mono">Tavily Web Research Tool</h3>
              </div>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                  health.adapters.tavily?.configured
                    ? 'bg-[#1D2B1C] text-[#C7D94C] border border-[#3B5436]'
                    : 'bg-[#2B231D] text-[#89977A] border border-[#2D332B]'
                }`}
              >
                {health.adapters.tavily?.status || 'NOT_CONFIGURED'}
              </span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1.5 border-b border-[#2D332B]/40 text-[#89977A]">
                <span>Status:</span>
                <span className={health.adapters.tavily?.configured ? 'text-[#C7D94C]' : 'text-[#89977A]'}>
                  {health.adapters.tavily?.configured ? 'READY' : 'NOT CONFIGURED'}
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#2D332B]/40 text-[#89977A]">
                <span>Credentials:</span>
                <span className="text-[#E8DDC8]">
                  {health.adapters.tavily?.has_credentials ? 'Configured in Environment (Hidden)' : 'Credentials not configured'}
                </span>
              </div>
              <div className="flex justify-between py-1.5 text-[#89977A]">
                <span>Search Endpoint:</span>
                <span className="text-[#A7A393]">{health.adapters.tavily?.api_base || 'https://api.tavily.com'}</span>
              </div>
            </div>

            <p className="text-[11px] text-[#A7A393] font-sans">
              Tavily powers grounded web-research benchmark tasks. Agents can query real authoritative sources and verify findings. Configure <code className="text-[#C7D94C]">TAVILY_API_KEY</code> on the server to activate.
            </p>

            <div className="pt-2 border-t border-[#2D332B] flex justify-between items-center">
              <button
                onClick={handleTestTavily}
                disabled={tavilyTesting}
                className="reliabench-btn reliabench-btn-lime text-xs py-1 px-3 flex items-center gap-1.5 cursor-pointer"
              >
                <Play size={12} />
                <span>{tavilyTesting ? 'Probing Tavily API...' : 'Test Connection'}</span>
              </button>
              {tavilyResult && (
                <span className={`text-[10px] font-mono ${tavilyResult.status === 'READY' ? 'text-[#C7D94C]' : 'text-[#F06B45]'}`}>
                  {tavilyResult.message || tavilyResult.status}
                </span>
              )}
            </div>
          </div>

          {/* Storage & Database Diagnostics */}
          <div className="reliabench-panel p-6 space-y-4 md:col-span-2">
            <div className="flex items-center gap-2 pb-3 border-b border-[#2D332B]">
              <Database size={18} className="text-[#C49A55]" />
              <h3 className="font-bold text-[#E8DDC8] text-base font-mono">Storage & Relational Database</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                <div className="text-[#89977A]">Relational Engine</div>
                <div className="text-[#E8DDC8] font-bold mt-1">SQLite 3 (PostgreSQL-Ready)</div>
                <div className="text-[10px] text-[#C7D94C] mt-1">Connected & Migrated</div>
              </div>

              <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                <div className="text-[#89977A]">ATIF Trajectories</div>
                <div className="text-[#E8DDC8] font-bold mt-1">artifacts/trajectories/</div>
                <div className="text-[10px] text-[#C7D94C] mt-1">Local Filesystem Storage</div>
              </div>

              <div className="bg-[#141713] p-3 rounded border border-[#2D332B]">
                <div className="text-[#89977A]">Logs & Reports</div>
                <div className="text-[#E8DDC8] font-bold mt-1">artifacts/reports/</div>
                <div className="text-[10px] text-[#C49A55] mt-1">JSON & CSV Generators Active</div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
