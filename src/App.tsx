import { HashRouter, Routes, Route } from 'react-router-dom';
import { TooltipProvider } from '@/components/ui/tooltip';
import Layout from '@/components/layout/Layout';
import SimulatorPage from '@/pages/SimulatorPage';
import AuditPage from '@/pages/AuditPage';
import MetricsPage from '@/pages/MetricsPage';
import ExperimentsPage from '@/pages/ExperimentsPage';
import DocsPage from '@/pages/DocsPage';

export default function App() {
  return (
    <TooltipProvider delayDuration={300}>
      <HashRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<SimulatorPage />} />
            <Route path="/audit" element={<AuditPage />} />
            <Route path="/metrics" element={<MetricsPage />} />
            <Route path="/experiments" element={<ExperimentsPage />} />
            <Route path="/docs" element={<DocsPage />} />
          </Route>
        </Routes>
      </HashRouter>
    </TooltipProvider>
  );
}
