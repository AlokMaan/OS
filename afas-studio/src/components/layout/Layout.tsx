import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play, FileText, BarChart3, FlaskConical, BookOpen,
  Sun, Moon, Menu, X, Download, ChevronLeft,
} from 'lucide-react';
import { useAppStore } from '@/store/store';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent,
  DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { downloadCSV, downloadJSON } from '@/lib/utils';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { to: '/', icon: Play, label: 'Simulator' },
  { to: '/audit', icon: FileText, label: 'Audit Log' },
  { to: '/metrics', icon: BarChart3, label: 'Metrics' },
  { to: '/experiments', icon: FlaskConical, label: 'Experiments' },
  { to: '/docs', icon: BookOpen, label: 'Docs' },
];

const PAGE_TITLES: Record<string, string> = {
  '/': 'Simulator',
  '/audit': 'AFAS Decision Audit Log',
  '/metrics': 'Metrics & Comparison',
  '/experiments': 'Experiments',
  '/docs': 'Algorithm Documentation',
};

export default function Layout() {
  const { theme, toggleTheme, results, processes } = useAppStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const pageTitle = PAGE_TITLES[location.pathname] || 'AFAS Studio';

  const handleExportCSV = () => {
    if (results.size === 0) return;
    const rows: Record<string, unknown>[] = [];
    results.forEach((r, policy) => {
      r.processResults.forEach((pr) => {
        rows.push({ policy, ...pr });
      });
    });
    downloadCSV(rows, 'afas-results.csv');
  };

  const handleExportJSON = () => {
    if (results.size === 0) return;
    const data: Record<string, unknown> = {};
    results.forEach((r, policy) => { data[policy] = r; });
    downloadJSON(data, 'afas-results.json');
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Brand */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-border/50">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
          <span className="text-emerald-400 font-bold text-sm">A</span>
        </div>
        {sidebarOpen && (
          <div className="flex flex-col">
            <span className="font-bold text-sm tracking-tight">AFAS Studio</span>
            <span className="text-[10px] text-muted-foreground">CPU Scheduler</span>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50',
                !sidebarOpen && 'justify-center px-2',
              )
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {sidebarOpen && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle (desktop only) */}
      <div className="hidden md:block px-3 py-4 border-t border-border/50">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="w-full justify-center"
        >
          <ChevronLeft className={cn('h-4 w-4 transition-transform', !sidebarOpen && 'rotate-180')} />
        </Button>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Desktop Sidebar */}
      <aside
        className={cn(
          'hidden md:flex flex-col border-r border-border/50 bg-card/30 backdrop-blur-sm transition-all duration-300',
          sidebarOpen ? 'w-56' : 'w-16',
        )}
      >
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black/50 md:hidden"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: -256 }}
              animate={{ x: 0 }}
              exit={{ x: -256 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="fixed inset-y-0 left-0 z-50 w-56 border-r border-border/50 bg-card md:hidden"
            >
              <SidebarContent />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center justify-between h-14 px-4 md:px-6 border-b border-border/50 bg-card/30 backdrop-blur-sm shrink-0">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <h1 className="text-base font-semibold truncate">{pageTitle}</h1>
          </div>

          <div className="flex items-center gap-2">
            {/* Theme toggle */}
            <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            {/* Export menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                  <Download className="h-4 w-4" />
                  <span className="hidden sm:inline">Export</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Export Results</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleExportCSV} disabled={results.size === 0}>
                  Export as CSV
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleExportJSON} disabled={results.size === 0}>
                  Export as JSON
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-4 md:p-6 max-w-[1600px] mx-auto">
            <Outlet />
          </div>

          {/* Footer */}
          <footer className="border-t border-border/50 px-4 md:px-6 py-4 text-center text-xs text-muted-foreground">
            <p>Adaptive Fairness-Aware CPU Scheduling Simulator — VIT Chennai | Operating Systems Project</p>
            <p className="mt-1">
              Alok Maan · Arshdeep Singh · Ankush Hooda · Somya Sharma &nbsp;|&nbsp; Guide: Prof. V. Ezhil Arasi
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}
