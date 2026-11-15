import React, { useState, useEffect } from 'react';
import { Terminal, Zap, ArrowLeft, HelpCircle, RotateCcw, Database } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useGuidedTour } from '../tour';
import { api } from '../../services/api';

interface NavbarProps {
  activeMode?: string;
  sourceMode?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeMode = 'SIMULATOR_DEMO',
  sourceMode = 'SIMULATOR'
}) => {
  const isSimulator = activeMode.includes('SIMULATOR') || sourceMode === 'SIMULATOR';
  const { startTour } = useGuidedTour();
  const [demoStatus, setDemoStatus] = useState<any>(null);
  const [resetting, setResetting] = useState(false);

  useEffect(() => {
    api.getDemoStatus().then(setDemoStatus).catch(() => {});
  }, []);

  const handleResetDemo = async () => {
    if (resetting) return;
    if (!window.confirm('Reset the canonical demo dataset? This restores the original 4 agents and 32 baseline experiments without affecting user data.')) {
      return;
    }
    setResetting(true);
    try {
      await api.resetDemo();
      window.location.reload();
    } catch (err: any) {
      alert(`Demo reset failed: ${err.message}`);
      setResetting(false);
    }
  };

  const isDemoActive = demoStatus?.seeded || isSimulator;

  return (
    <header className="h-16 bg-[#171A16] border-b border-[#2D332B] px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-4">
        {/* Back to Home Button */}
        <Link
          to="/"
          className="flex items-center gap-1.5 text-xs font-mono font-bold text-[#A7A393] hover:text-[#E8DDC8] px-2.5 py-1 rounded bg-[#1D211C] border border-[#2D332B] transition-colors"
        >
          <ArrowLeft size={14} className="text-[#F06B45]" />
          <span>Home</span>
        </Link>

        {/* Demo Environment Badge */}
        {isDemoActive ? (
          <div
            className="flex items-center gap-2 px-3 py-1 text-xs font-mono font-bold uppercase border bg-[#2B231D] text-[#F06B45] border-[#5E3F2A] shadow-[2px_2px_0px_0px_#10120F]"
            title="Active demonstration workspace populated with canonical baseline agents and experiments"
          >
            <Database size={13} className="text-[#F06B45]" />
            <span>DEMO ENVIRONMENT · CANONICAL DATA</span>
          </div>
        ) : (
          <div
            className="flex items-center gap-2 px-3 py-1 text-xs font-mono font-bold uppercase border bg-[#1D2B1C] text-[#C7D94C] border-[#3B5436] shadow-[2px_2px_0px_0px_#10120F]"
          >
            <Zap size={13} />
            <span>HARBOR ENGINE · LIVE VERIFIED</span>
          </div>
        )}

        <div className="text-xs text-[#89977A] hidden lg:block font-mono">
          Global AI Hackathon | PS02
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Reset Demo Data Action */}
        {isDemoActive && (
          <button
            onClick={handleResetDemo}
            disabled={resetting}
            className="flex items-center gap-1.5 text-xs font-mono font-bold text-[#A7A393] hover:text-[#F06B45] px-2.5 py-1.5 rounded bg-[#1D211C] border border-[#2D332B] hover:border-[#5E3F2A] transition-colors cursor-pointer disabled:opacity-50"
            title="Reset demo workspace to fresh canonical state"
          >
            <RotateCcw size={13} className={resetting ? 'animate-spin text-[#F06B45]' : ''} />
            <span className="hidden md:inline">{resetting ? 'Resetting...' : 'Reset Demo'}</span>
          </button>
        )}

        {/* Interactive Tour Trigger */}
        <button
          onClick={() => startTour(0)}
          className="flex items-center gap-1.5 text-xs font-mono font-bold text-[#C7D94C] hover:text-[#d7e85c] px-2.5 py-1.5 rounded bg-[#1D2B1C] border border-[#3B5436] transition-colors cursor-pointer"
          title="Start Guided Product Tour"
        >
          <HelpCircle size={14} />
          <span className="hidden sm:inline">Product Tour</span>
        </button>

        <div className="flex items-center gap-2 bg-[#1D211C] border border-[#2D332B] px-3 py-1.5 text-xs text-[#A7A393] font-mono">
          <Terminal size={13} className="text-[#C7D94C]" />
          <span>v0.2.0-beta</span>
        </div>
        <div className="w-8 h-8 rounded-full bg-[#1D211C] border border-[#2D332B] flex items-center justify-center font-bold text-xs text-[#C7D94C]">
          RB
        </div>
      </div>
    </header>
  );
};
