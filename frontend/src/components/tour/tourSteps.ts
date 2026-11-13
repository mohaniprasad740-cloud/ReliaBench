export interface TourStep {
  id: string;
  route: string;
  targetSelector: string;
  title: string;
  content: string;
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'center';
  highlightPadding?: number;
}

export const TOUR_STEPS: TourStep[] = [
  // Step 1: Welcome & Overview
  {
    id: 'dashboard-welcome',
    route: '/app',
    targetSelector: '[data-tour="dashboard-header"]',
    title: 'Welcome to Reliabench',
    content: 'Reliabench evaluates autonomous AI agents under identical, reproducible benchmark tasks with controlled failure injection and deep observability.',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 2: Key Reliability Metrics
  {
    id: 'dashboard-metrics',
    route: '/app',
    targetSelector: '[data-tour="dashboard-metrics-strip"]',
    title: 'Statistical Reliability Metrics',
    content: 'Review Wilson 95% Confidence Intervals, finite-sample Pass@k (probability at least 1 of k attempts succeeds), and Pass^k (probability all k attempts succeed without failure).',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 3: Agent Registry
  {
    id: 'nav-agents',
    route: '/app/agents',
    targetSelector: '[data-tour="agents-header"]',
    title: 'Agent Registry & Adapters',
    content: 'Register and probe autonomous candidate agents. Connect via Harbor CLI, native REST endpoints, or internal deterministic test harness profiles.',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 4: Register Agent Action
  {
    id: 'agents-register-btn',
    route: '/app/agents',
    targetSelector: '[data-tour="agents-register-btn"]',
    title: 'Connect Candidate Agent',
    content: 'Register your model endpoint, framework (Harbor, AutoGen, CrewAI, Custom), and probe connection health before beginning benchmark runs.',
    placement: 'left',
    highlightPadding: 6,
  },
  // Step 5: Benchmark Library
  {
    id: 'nav-benchmarks',
    route: '/app/benchmarks',
    targetSelector: '[data-tour="benchmarks-header"]',
    title: 'Benchmark Challenge Packs',
    content: 'Explore versioned multi-turn YAML challenge packs. Each task declares explicit tool dependencies, sequential execution plans, and verifiable outcome assertions.',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 6: Benchmark Runner Execution
  {
    id: 'benchmarks-run-btn',
    route: '/app/benchmarks',
    targetSelector: '[data-tour="benchmarks-run-card"]',
    title: 'Repeated Trial Execution (k)',
    content: 'Configure repeated trials (k=1..10) with exact random seeds to measure statistical consistency and identify flaky behavior across attempts.',
    placement: 'top',
    highlightPadding: 8,
  },
  // Step 7: Experiments & Repeated Runs
  {
    id: 'nav-experiments',
    route: '/app/experiments',
    targetSelector: '[data-tour="experiments-header"]',
    title: 'Experiments & Controlled Faults',
    content: 'Orchestrate repeated evaluations paired with controlled failure injection. Inspect iteration-level Pass@k and post-fault recovery rates.',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 8: Regression Gates & Quarantine Replay
  {
    id: 'nav-regressions',
    route: '/app/regressions',
    targetSelector: '[data-tour="regressions-header"]',
    title: 'Regression Gates & CI Replay',
    content: 'Promote observed trial failures into permanent deterministic regression gates. Replay against fragile vs resilient agent profiles before merging code.',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 9: Agent Comparison Matrix
  {
    id: 'nav-comparison',
    route: '/app/comparison',
    targetSelector: '[data-tour="comparison-header"]',
    title: 'Side-by-Side Comparison Matrix',
    content: 'Directly compare multiple agents or configurations evaluated under identical benchmark tasks, repetition counts, and failure conditions.',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 10: ATIF Trace Inspector
  {
    id: 'nav-traces',
    route: '/app/traces',
    targetSelector: '[data-tour="traces-header"]',
    title: 'ATIF v1.8 Execution Traces',
    content: 'Inspect step-by-step observable evidence conforming to Harbor’s Agent Trajectory Interchange Format (ATIF), including tool parameters and observations.',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 11: Benchmark Certification Reports
  {
    id: 'nav-reports',
    route: '/app/reports',
    targetSelector: '[data-tour="reports-header"]',
    title: 'Reports & Audit Exports',
    content: 'Generate verifiable benchmark certification summaries with complete execution provenance. Export structured findings directly in JSON and CSV formats.',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 12: Integrations & Health Diagnostics
  {
    id: 'nav-settings',
    route: '/app/integrations',
    targetSelector: '[data-tour="settings-header"]',
    title: 'System Diagnostics & Integrations',
    content: 'Verify operational status across execution planes: Harbor container sandboxes, Maxim Bifrost model gateways, and Tavily web research tools.',
    placement: 'bottom',
    highlightPadding: 8,
  },
  // Step 13: Tavily Web Search Diagnostic
  {
    id: 'settings-tavily',
    route: '/app/integrations',
    targetSelector: '[data-tour="settings-tavily-card"]',
    title: 'Tavily Web Research Tool',
    content: 'Powers grounded external research benchmark tasks. Uses server-side TAVILY_API_KEY to execute authoritative web searches with full domain and latency telemetry.',
    placement: 'top',
    highlightPadding: 8,
  },
  // Step 14: Bifrost Model Gateway Diagnostic
  {
    id: 'settings-bifrost',
    route: '/app/integrations',
    targetSelector: '[data-tour="settings-bifrost-card"]',
    title: 'Maxim Bifrost Model Gateway',
    content: 'Routes model requests through Bifrost with x-bf-lh-* correlation headers to attribute exact token usage, costs, and provider failovers per trial.',
    placement: 'top',
    highlightPadding: 8,
  },
];
