import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Agent } from '../services/types';
import { Bot, Plus, Trash2, CheckCircle, ShieldAlert, Cpu, Check, AlertCircle } from 'lucide-react';

export const AgentsPage: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [validatingId, setValidatingId] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: '',
    description: '',
    framework: 'custom',
    version: '1.0.0',
    adapter_type: 'simulator',
    model_provider: 'anthropic',
    model_name: 'claude-3-7-sonnet',
    endpoint_url: ''
  });

  const loadAgents = () => {
    setLoading(true);
    api.getAgents()
      .then(setAgents)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAgents();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createAgent(form);
      setShowModal(false);
      setForm({
        name: '',
        description: '',
        framework: 'custom',
        version: '1.0.0',
        adapter_type: 'simulator',
        model_provider: 'anthropic',
        model_name: 'claude-3-7-sonnet',
        endpoint_url: ''
      });
      loadAgents();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleValidate = async (id: string) => {
    setValidatingId(id);
    try {
      await api.validateAgent(id);
      loadAgents();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setValidatingId(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete this agent configuration?')) {
      await api.deleteAgent(id);
      loadAgents();
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center pb-6 border-b border-[#2D332B]">
        <div>
          <h1 className="text-2xl font-black text-[#E8DDC8] flex items-center gap-2">
            <Bot size={26} className="text-[#F06B45]" />
            <span>Agent Registry</span>
          </h1>
          <p className="text-xs text-[#A7A393] font-sans mt-0.5">
            Register and validate autonomous agent endpoints, framework adapters, and underlying models.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="reliabench-btn reliabench-btn-persimmon"
        >
          <Plus size={15} />
          <span>Register Candidate Agent</span>
        </button>
      </div>

      {loading ? (
        <div className="font-mono text-xs text-[#C7D94C]">[ QUERYING AGENT REGISTRY... ]</div>
      ) : agents.length === 0 ? (
        <div className="reliabench-panel p-10 text-center">
          <Bot size={40} className="text-[#89977A] mx-auto mb-4" />
          <h3 className="text-lg font-bold text-[#E8DDC8] mb-2">No agents registered yet</h3>
          <p className="text-xs text-[#A7A393] mb-6 max-w-md mx-auto">
            Register your first AI agent to begin benchmarking. You can connect agents via Harbor CLI, a custom REST API, or run them through the deterministic simulator.
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="reliabench-btn reliabench-btn-persimmon"
          >
            <Plus size={15} />
            <span>Register Your First Agent</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <div key={agent.id} className="reliabench-panel p-5 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-bold text-base text-[#E8DDC8]">{agent.name}</h3>
                    <div className="text-[11px] font-mono text-[#89977A]">v{agent.version}</div>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                      agent.status === 'VALIDATED' || agent.status === 'AVAILABLE'
                        ? 'bg-[#1D2B1C] text-[#C7D94C] border-[#3B5436]'
                        : agent.status === 'SIMULATOR'
                        ? 'bg-[#2B231D] text-[#F06B45] border-[#5E3F2A]'
                        : 'bg-[#1D211C] text-[#A7A393] border-[#2D332B]'
                    }`}
                  >
                    {agent.status}
                  </span>
                </div>

                <p className="text-xs text-[#A7A393] mb-4 min-h-[2.5rem] font-sans">
                  {agent.description || 'No description provided.'}
                </p>

                <div className="space-y-1.5 text-xs font-mono bg-[#141713] p-3 rounded border border-[#2D332B] mb-4">
                  <div className="flex justify-between text-[#A7A393]">
                    <span>Framework:</span>
                    <span className="text-[#E8DDC8] font-bold">{agent.framework}</span>
                  </div>
                  <div className="flex justify-between text-[#A7A393]">
                    <span>Adapter:</span>
                    <span className="text-[#C49A55]">{agent.adapter_type}</span>
                  </div>
                  <div className="flex justify-between text-[#A7A393]">
                    <span>Model:</span>
                    <span className="text-[#C7D94C]">{agent.model_name || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between text-[#A7A393]">
                    <span>Provenance:</span>
                    <span className={agent.source_mode === 'REAL_EXECUTION' ? 'text-[#C7D94C]' : 'text-[#F06B45]'}>
                      {agent.source_mode}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center pt-3 border-t border-[#2D332B]">
                <button
                  onClick={() => handleValidate(agent.id)}
                  disabled={validatingId === agent.id}
                  className="text-xs font-mono font-bold text-[#C7D94C] hover:text-[#d6e858] flex items-center gap-1 cursor-pointer"
                >
                  <Check size={14} />
                  <span>{validatingId === agent.id ? 'Validating...' : 'Validate Adapter'}</span>
                </button>
                <button
                  onClick={() => handleDelete(agent.id)}
                  className="text-xs text-[#F06B45] hover:text-red-400 font-mono flex items-center gap-1 cursor-pointer"
                >
                  <Trash2 size={13} />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Registration Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="reliabench-panel bg-[#1D211C] border border-[#F06B45] p-6 max-w-md w-full">
            <h2 className="text-lg font-bold text-[#E8DDC8] mb-4 font-mono">Register New Agent</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                  Agent Name
                </label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded outline-none"
                  placeholder="e.g. MySoftwareAgent-v1"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                  Description
                </label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded h-16 outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                    Framework
                  </label>
                  <select
                    value={form.framework}
                    onChange={(e) => setForm({ ...form, framework: e.target.value })}
                    className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded"
                  >
                    <option value="custom">Custom</option>
                    <option value="harbor_native">Harbor Native</option>
                    <option value="autogen">AutoGen</option>
                    <option value="crewai">CrewAI</option>
                    <option value="langchain">LangChain</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                    Adapter Type
                  </label>
                  <select
                    value={form.adapter_type}
                    onChange={(e) => setForm({ ...form, adapter_type: e.target.value })}
                    className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded"
                  >
                    <option value="simulator">Simulator (Deterministic)</option>
                    <option value="harbor_cli">Harbor CLI (v0.25.0)</option>
                    <option value="rest_api">Custom REST API</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                    Model Provider
                  </label>
                  <input
                    type="text"
                    value={form.model_provider}
                    onChange={(e) => setForm({ ...form, model_provider: e.target.value })}
                    className="w-full bg-[#141713] border border-[#2D332B] px-3 py-2 text-[#E8DDC8] font-mono text-xs rounded"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-[#A7A393] mb-1 font-mono">
                    Model Identifier
                  </label>
                  <input
                    type="text"
                    value={form.model_name}
                    onChange={(e) => setForm({ ...form, model_name: e.target.value })}
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
                  Save Agent
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
