import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { GuidedTourProvider, GuidedTourOverlay } from './components/tour';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { AgentsPage } from './pages/AgentsPage';
import { BenchmarksPage } from './pages/BenchmarksPage';
import { ExperimentsPage } from './pages/ExperimentsPage';
import { ComparisonsPage } from './pages/ComparisonsPage';
import { RegressionsPage } from './pages/RegressionsPage';
import { TracesPage } from './pages/TracesPage';

import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <GuidedTourProvider>
        <GuidedTourOverlay />
        <Routes>
        {/* PUBLIC DEDICATED EDITORIAL LANDING PAGE */}
        <Route path="/" element={<LandingPage />} />

        {/* WORKSPACE & APPLICATION DASHBOARD SHELL */}
        <Route path="/app" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="agents" element={<AgentsPage />} />
          <Route path="benchmarks" element={<BenchmarksPage />} />
          <Route path="experiments" element={<ExperimentsPage />} />
          <Route path="regressions" element={<RegressionsPage />} />
          <Route path="comparison" element={<ComparisonsPage />} />

          <Route path="traces" element={<TracesPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="integrations" element={<SettingsPage />} />
        </Route>

        {/* Legacy Fallbacks */}
        <Route path="/agents" element={<Navigate to="/app/agents" replace />} />
        <Route path="/benchmarks" element={<Navigate to="/app/benchmarks" replace />} />
        <Route path="/experiments" element={<Navigate to="/app/experiments" replace />} />
        <Route path="/comparisons" element={<Navigate to="/app/comparison" replace />} />
        <Route path="/traces" element={<Navigate to="/app/traces" replace />} />
        <Route path="/reports" element={<Navigate to="/app/reports" replace />} />
        <Route path="/settings" element={<Navigate to="/app/integrations" replace />} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </GuidedTourProvider>
    </BrowserRouter>
  );
};

export default App;
