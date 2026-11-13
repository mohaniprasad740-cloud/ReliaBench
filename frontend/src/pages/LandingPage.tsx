import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  ShieldCheck,
  Zap,
  Repeat,
  AlertTriangle,
  GitCompare,
  Activity,
  Terminal,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Clock,
  Layers,
  ChevronDown
} from 'lucide-react';
import { LiquidCanvas } from '../components/ui/LiquidCanvas';

export const LandingPage: React.FC = () => {
  // Interactive Trial Matrix Simulator Demo State
  const [trialStates, setTrialStates] = useState<string[]>([
    'PASSED', 'FAILED', 'RECOVERED', 'PASSED', 'TIMEOUT', 'PASSED', 'RECOVERED', 'PASSED'
  ]);

  const toggleTrial = (idx: number) => {
    const cycle = ['PASSED', 'FAILED', 'RECOVERED', 'TIMEOUT'];
    setTrialStates((prev) => {
      const next = [...prev];
      const curIdx = cycle.indexOf(next[idx]);
      next[idx] = cycle[(curIdx + 1) % cycle.length];
      return next;
    });
  };

  return (
    <div className="min-h-screen bg-[#171A16] text-[#E8DDC8] selection:bg-[#F06B45] selection:text-[#10120F]">
      {/* SECTION 1: TOP NAVIGATION */}
      <header className="sticky top-0 z-50 bg-[#171A16]/90 backdrop-blur-md border-b border-[#2D332B] px-6 lg:px-12 h-18 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-[#F06B45] border border-[#10120F] flex items-center justify-center font-black text-[#10120F] text-base shadow-[2px_2px_0px_0px_#10120F]">
            R
          </div>
          <div>
            <span className="font-black text-lg tracking-wider text-[#E8DDC8]">RELIABENCH</span>
            <span className="text-[10px] uppercase font-mono tracking-widest text-[#89977A] block -mt-1">
              Global AI Hackathon · PS02
            </span>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-8 text-xs font-mono uppercase tracking-wider text-[#A7A393]">
          <a href="#problem" className="hover:text-[#E8DDC8] transition-colors">The Problem</a>
          <a href="#measures" className="hover:text-[#E8DDC8] transition-colors">What We Measure</a>
          <a href="#how-it-works" className="hover:text-[#E8DDC8] transition-colors">How It Works</a>
          <a href="#methodology" className="hover:text-[#E8DDC8] transition-colors">Methodology</a>
        </nav>

        <div className="flex items-center gap-3">
          <Link
            to="/app"
            className="reliabench-btn reliabench-btn-lime"
          >
            <span>Open Dashboard</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      </header>

      {/* SECTION 2: EDITORIAL HERO */}
      <section className="relative px-6 lg:px-12 pt-20 pb-28 border-b border-[#2D332B] overflow-hidden">
        {/* Subtle Liquid Interactive Layer */}
        <LiquidCanvas />

        <div className="relative z-10 max-w-6xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#1D211C] border border-[#2D332B] text-xs font-mono text-[#C7D94C] mb-8">
            <span className="w-2 h-2 rounded-full bg-[#C7D94C] animate-pulse"></span>
            <span>FRAMEWORK-INDEPENDENT AI AGENT RELIABILITY PLATFORM</span>
          </div>

          <div className="mb-8">
            <h1 className="editorial-hero-title text-[#E8DDC8]">
              YOUR AGENT PASSED ONCE.
            </h1>
            <h1 className="editorial-hero-title text-[#F06B45]">
              DOES IT PASS AGAIN?
            </h1>
          </div>

          <p className="text-lg md:text-xl text-[#A7A393] max-w-3xl mb-12 font-sans leading-relaxed">
            Reliabench evaluates autonomous agents across repeatable benchmark tasks, controlled failures, and repeated trials—so reliability is measured, not assumed.
          </p>

          <div className="flex flex-wrap items-center gap-4 mb-20">
            <Link
              to="/app"
              className="reliabench-btn reliabench-btn-persimmon text-sm py-3.5 px-6"
            >
              <span>Explore the Benchmark Lab</span>
              <ArrowRight size={16} />
            </Link>
            <a
              href="#methodology"
              className="reliabench-btn reliabench-btn-outline text-sm py-3.5 px-6"
            >
              <span>Understand the Methodology</span>
              <ChevronDown size={16} />
            </a>
          </div>

          {/* HERO VISUALIZATION: REPEATED TRIAL MATRIX */}
          <div className="reliabench-panel p-6 bg-[#1D211C] border-2 border-[#2D332B]">
            <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 pb-4 mb-6 border-b border-[#2D332B]">
              <div>
                <div className="text-xs font-mono uppercase tracking-wider text-[#C7D94C] font-bold">
                  Interactive Trial Matrix Simulator
                </div>
                <div className="text-xs text-[#A7A393] font-mono mt-0.5">
                  Click any trial to cycle state (PASS / FAIL / RECOVERED / TIMEOUT) to test metric calculation
                </div>
              </div>
              <div className="text-[11px] font-mono bg-[#171A16] px-2.5 py-1 border border-[#2D332B] text-[#A7A393]">
                ILLUSTRATIVE MODEL — NOT EXPERIMENT DATA · k = 8 ATTEMPTS
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
              {trialStates.map((st, i) => (
                <button
                  key={i}
                  onClick={() => toggleTrial(i)}
                  className={`p-3 border text-left rounded transition-all cursor-pointer font-mono ${
                    st === 'PASSED'
                      ? 'bg-[#1D2B1C] border-[#3B5436] text-[#C7D94C]'
                      : st === 'RECOVERED'
                      ? 'bg-[#292A1A] border-[#5E5A2A] text-[#C49A55]'
                      : st === 'TIMEOUT'
                      ? 'bg-[#2B231D] border-[#5E3F2A] text-[#F06B45]'
                      : 'bg-[#2B1D1D] border-[#5E2A2A] text-[#FF725E]'
                  }`}
                >
                  <div className="text-[10px] text-[#A7A393] mb-1">Trial #{i + 1}</div>
                  <div className="text-xs font-black tracking-wide">{st}</div>
                </button>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-[#2D332B] flex flex-wrap justify-between items-center text-xs font-mono text-[#A7A393]">
              <div>
                Observed Successes: <strong className="text-[#C7D94C]">{trialStates.filter(s => s === 'PASSED' || s === 'RECOVERED').length} / {trialStates.length}</strong>
              </div>
              <div>
                Pass Rate: <strong className="text-[#E8DDC8]">{((trialStates.filter(s => s === 'PASSED' || s === 'RECOVERED').length / trialStates.length) * 100).toFixed(0)}%</strong>
              </div>
              <div>
                Recoveries: <strong className="text-[#C49A55]">{trialStates.filter(s => s === 'RECOVERED').length}</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 3: THE PROBLEM */}
      <section id="problem" className="px-6 lg:px-12 py-24 bg-[#E8DDC8] text-[#10120F] border-b border-[#2D332B]">
        <div className="max-w-6xl mx-auto">
          <div className="text-xs font-mono uppercase tracking-widest text-[#F06B45] font-black mb-3">
            01 / CRITICAL EVALUATION FLAW
          </div>
          <h2 className="editorial-section-title mb-8 max-w-3xl">
            ONE SUCCESSFUL RUN IS NOT RELIABILITY.
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div className="border-t-2 border-[#10120F] pt-4">
              <div className="text-4xl font-black font-mono text-[#F06B45] mb-2">01</div>
              <h3 className="font-bold text-lg mb-2">High Execution Variance</h3>
              <p className="text-sm text-[#10120F]/80 leading-relaxed font-sans">
                Agents frequently succeed on Attempt #1 and crash completely on Attempt #2 under identical system instructions. Single-turn leaderboards hide this catastrophic spread.
              </p>
            </div>

            <div className="border-t-2 border-[#10120F] pt-4">
              <div className="text-4xl font-black font-mono text-[#F06B45] mb-2">02</div>
              <h3 className="font-bold text-lg mb-2">Brittle Tool Dependencies</h3>
              <p className="text-sm text-[#10120F]/80 leading-relaxed font-sans">
                A single HTTP 429 rate limit or malformed tool payload frequently causes unhandled infinite retry loops or hallucinated completion assertions without verifiable reward.
              </p>
            </div>

            <div className="border-t-2 border-[#10120F] pt-4">
              <div className="text-4xl font-black font-mono text-[#F06B45] mb-2">03</div>
              <h3 className="font-bold text-lg mb-2">Retrying Is Not Recovery</h3>
              <p className="text-sm text-[#10120F]/80 leading-relaxed font-sans">
                Blindly looping model calls is not systematic recovery. Reliabench isolates whether the agent actually diagnosed the fault, adapted its strategy, and satisfied verifiable test assertions.
              </p>
            </div>
          </div>

          <div className="bg-[#10120F] text-[#E8DDC8] p-6 border-l-4 border-[#F06B45] flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <div className="text-xs font-mono text-[#C7D94C] uppercase tracking-wider mb-1 font-bold">
                The Solution
              </div>
              <div className="text-base font-bold">
                Rigorous statistical Pass@k, Pass^k, and Controlled Failure Injections.
              </div>
            </div>
            <Link
              to="/app/experiments"
              className="reliabench-btn reliabench-btn-lime whitespace-nowrap"
            >
              <span>Configure Benchmark Experiment</span>
              <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </section>

      {/* SECTION 4: WHAT RELIABENCH MEASURES */}
      <section id="measures" className="px-6 lg:px-12 py-24 border-b border-[#2D332B] bg-[#171A16]">
        <div className="max-w-6xl mx-auto">
          <div className="text-xs font-mono uppercase tracking-widest text-[#C7D94C] font-bold mb-3">
            02 / DIMENSIONS OF RELIABILITY
          </div>
          <h2 className="editorial-section-title mb-16 text-[#E8DDC8]">
            WHAT RELIABENCH MEASURES
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="reliabench-panel p-6 border-t-2 border-t-[#C7D94C]">
              <Repeat size={24} className="text-[#C7D94C] mb-4" />
              <h3 className="font-bold text-base text-[#E8DDC8] mb-2">Repeated Trial Consistency</h3>
              <p className="text-xs text-[#A7A393] leading-relaxed">
                Evaluates variance in execution duration and success probabilities across $k$ repeated attempts under invariant conditions.
              </p>
            </div>

            <div className="reliabench-panel p-6 border-t-2 border-t-[#F06B45]">
              <Zap size={24} className="text-[#F06B45] mb-4" />
              <h3 className="font-bold text-base text-[#E8DDC8] mb-2">Pass@k & Pass^k</h3>
              <p className="text-xs text-[#A7A393] leading-relaxed">
                Unbiased hypergeometric estimator of achieving at least one success vs. strict joint probability that every single trial passes.
              </p>
            </div>

            <div className="reliabench-panel p-6 border-t-2 border-t-[#C49A55]">
              <AlertTriangle size={24} className="text-[#C49A55] mb-4" />
              <h3 className="font-bold text-base text-[#E8DDC8] mb-2">Controlled Failure Injection</h3>
              <p className="text-xs text-[#A7A393] leading-relaxed">
                Synthetically induces tool timeouts, HTTP 500s, malformed schemas, and conflicting context without host machine intrusion.
              </p>
            </div>

            <div className="reliabench-panel p-6 border-t-2 border-t-[#89977A]">
              <ShieldCheck size={24} className="text-[#89977A] mb-4" />
              <h3 className="font-bold text-base text-[#E8DDC8] mb-2">Statistical Recovery Rate</h3>
              <p className="text-xs text-[#A7A393] leading-relaxed">
                Measures the exact proportion of failure-injected trials where the agent successfully recovered and satisfied formal verifiers.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 5: HOW IT WORKS */}
      <section id="how-it-works" className="px-6 lg:px-12 py-24 border-b border-[#2D332B] bg-[#1D211C]">
        <div className="max-w-6xl mx-auto">
          <div className="text-xs font-mono uppercase tracking-widest text-[#F06B45] font-bold mb-3">
            03 / EXECUTION PIPELINE
          </div>
          <h2 className="editorial-section-title mb-16 text-[#E8DDC8]">
            HOW IT WORKS
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 font-mono text-xs">
            <div className="bg-[#171A16] p-5 border border-[#2D332B] relative">
              <div className="text-[#F06B45] font-black text-lg mb-2">01</div>
              <h4 className="font-bold text-sm text-[#E8DDC8] mb-1">Register Agent</h4>
              <p className="text-[#A7A393]">
                Declare framework (Harbor, AutoGen, CrewAI, Custom) and adapter configuration.
              </p>
            </div>

            <div className="bg-[#171A16] p-5 border border-[#2D332B] relative">
              <div className="text-[#F06B45] font-black text-lg mb-2">02</div>
              <h4 className="font-bold text-sm text-[#E8DDC8] mb-1">Select Challenge</h4>
              <p className="text-[#A7A393]">
                Pick standardized benchmark tasks with verifiable assertion scripts and environment bounds.
              </p>
            </div>

            <div className="bg-[#171A16] p-5 border border-[#2D332B] relative">
              <div className="text-[#F06B45] font-black text-lg mb-2">03</div>
              <h4 className="font-bold text-sm text-[#E8DDC8] mb-1">Inject Faults & Reps</h4>
              <p className="text-[#A7A393]">
                Configure $k$ repetitions and optional fault vectors (HTTP 500, Tool Timeout, Corrupt Output).
              </p>
            </div>

            <div className="bg-[#171A16] p-5 border border-[#2D332B] relative">
              <div className="text-[#F06B45] font-black text-lg mb-2">04</div>
              <h4 className="font-bold text-sm text-[#E8DDC8] mb-1">Inspect ATIF Evidence</h4>
              <p className="text-[#A7A393]">
                Examine step-by-step reasoning, tool invocations, and verifier rewards in ATIF v1.8 format.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 7: METHODOLOGY */}
      <section id="methodology" className="px-6 lg:px-12 py-24 border-b border-[#2D332B] bg-[#171A16]">
        <div className="max-w-6xl mx-auto">
          <div className="text-xs font-mono uppercase tracking-widest text-[#C7D94C] font-bold mb-3">
            04 / FORMAL MATHEMATICS
          </div>
          <h2 className="editorial-section-title mb-12 text-[#E8DDC8]">
            EVALUATION METHODOLOGY
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 font-mono">
            <div className="reliabench-panel p-6">
              <div className="text-xs uppercase font-bold text-[#C7D94C] mb-2">Pass@k Unbiased Estimator</div>
              <div className="bg-[#10120F] p-4 border border-[#2D332B] text-sm text-[#E8DDC8] mb-3">
                Pass@k = 1 - [ C(n - c, k) / C(n, k) ]
              </div>
              <p className="text-xs text-[#A7A393] leading-relaxed">
                Calculates the estimated probability that at least one of $k$ sampled runs succeeds, where $n$ is total completed trials and $c$ is successful trials. Avoids optimistic bias found in naive sampling.
              </p>
            </div>

            <div className="reliabench-panel p-6">
              <div className="text-xs uppercase font-bold text-[#F06B45] mb-2">Wilson Score Confidence Interval</div>
              <div className="bg-[#10120F] p-4 border border-[#2D332B] text-sm text-[#E8DDC8] mb-3">
                p_adj ± z * sqrt(p(1-p)/n + z²/(4n²)) / (1 + z²/n)
              </div>
              <p className="text-xs text-[#A7A393] leading-relaxed">
                Provides asymmetrical 95% confidence bounds suited for small benchmark sample sizes without producing misleading &gt;100% or &lt;0% intervals.
              </p>
            </div>

            <div className="reliabench-panel p-6">
              <div className="text-xs uppercase font-bold text-[#C49A55] mb-2">Pass^k (Strict Joint Success)</div>
              <div className="bg-[#10120F] p-4 border border-[#2D332B] text-sm text-[#E8DDC8] mb-3">
                Pass^k = (s / n)^k
              </div>
              <p className="text-xs text-[#A7A393] leading-relaxed">
                Measures whether an agent reliably passes every single attempt across $k$ runs. Essential for mission-critical software workflows where even one failure breaks the build.
              </p>
            </div>

            <div className="reliabench-panel p-6">
              <div className="text-xs uppercase font-bold text-[#89977A] mb-2">Recovery Rate</div>
              <div className="bg-[#10120F] p-4 border border-[#2D332B] text-sm text-[#E8DDC8] mb-3">
                RecoveryRate = Recovered Trials / Total Injected Trials
              </div>
              <p className="text-xs text-[#A7A393] leading-relaxed">
                Evaluates true resilience: counted as recovered only if a fault was actively triggered, the agent adapted without crashing, and the final verifier passed with reward 1.0.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 8: FINAL CTA */}
      <section className="px-6 lg:px-12 py-24 text-center bg-[#E8DDC8] text-[#10120F]">
        <div className="max-w-4xl mx-auto">
          <h2 className="editorial-hero-title mb-6">
            STOP TRUSTING THE LUCKY RUN.
          </h2>
          <p className="text-base md:text-lg text-[#10120F]/80 max-w-2xl mx-auto mb-10 font-sans">
            Start benchmarking autonomous agent reliability with controlled failure injection, repeatability metrics, and evidence-backed trace verification.
          </p>
          <Link
            to="/app"
            className="reliabench-btn reliabench-btn-persimmon text-base py-4 px-8"
          >
            <span>Enter Reliabench Platform</span>
            <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="px-6 lg:px-12 py-12 border-t border-[#2D332B] bg-[#10120F] text-xs font-mono text-[#A7A393] flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <strong className="text-[#E8DDC8]">RELIABENCH</strong> · Global AI Hackathon PS02 (AI Agent Benchmarking Platform)
        </div>
        <div className="flex gap-6">
          <Link to="/app" className="hover:text-[#E8DDC8]">App Dashboard</Link>
          <Link to="/app/benchmarks" className="hover:text-[#E8DDC8]">Benchmark Library</Link>
          <Link to="/app/integrations" className="hover:text-[#E8DDC8]">Harbor v0.25.0 Adapter</Link>
          <a href="#methodology" className="hover:text-[#E8DDC8]">Methodology</a>
        </div>
        <div>
          Version: 0.2.0-beta
        </div>
      </footer>
    </div>
  );
};

