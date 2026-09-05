import React, { useState } from 'react';
import {
  LayoutDashboard,
  ClipboardList,
  History,
  Shield,
  Search,
  UserCheck,
  Menu,
  X,
  ArrowRightLeft,
  Bell
} from 'lucide-react';
import { UserRole, HealthStatus } from '../types';

interface ExpertLayoutProps {
  children: React.ReactNode;
  activeTab: 'dashboard' | 'queue' | 'history' | 'case';
  onNavigate: (route: string) => void;
  onSwitchRole: (role: UserRole) => void;
  health: HealthStatus | null;
}

export const ExpertLayout: React.FC<ExpertLayoutProps> = ({
  children,
  activeTab,
  onNavigate,
  onSwitchRole,
  health,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard Overview', icon: LayoutDashboard, route: '/expert' },
    { id: 'queue', label: 'Review Queue', icon: ClipboardList, route: '/expert/reviews' },
    { id: 'history', label: 'Reviewed History', icon: History, route: '/expert/history' },
  ];

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden text-slate-300 hover:text-white p-1"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => onNavigate('/expert')}>
              <div className="w-9 h-9 rounded-xl bg-emerald-600 flex items-center justify-center font-bold text-white shadow-md">
                <Shield className="w-5 h-5 text-emerald-100" />
              </div>
              <div>
                <span className="font-extrabold text-lg tracking-tight text-white block leading-none">HortiSentry</span>
                <span className="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider block mt-0.5">
                  Expert Review Workspace
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* DEMO MODE Badge */}
            {health?.ml_mode === 'DEMO' && (
              <span className="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-[11px] font-bold px-2.5 py-1 rounded-full hidden sm:inline-flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                DEMO MODE ACTIVE
              </span>
            )}

            {/* Role Switcher */}
            <button
              onClick={() => onSwitchRole('farmer')}
              className="inline-flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors"
              title="Switch to Farmer Portal"
            >
              <ArrowRightLeft className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden sm:inline">Farmer Portal</span>
            </button>

            {/* Expert Profile Indicator */}
            <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
              <div className="w-8 h-8 rounded-full bg-emerald-700 text-white font-bold text-xs flex items-center justify-center border border-emerald-500">
                EX
              </div>
              <div className="hidden md:block text-left text-xs">
                <p className="font-bold text-slate-200">Dr. Horti Reviewer</p>
                <p className="text-[10px] text-slate-400">Cooperative Pathologist</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Layout with Sidebar */}
      <div className="flex-1 max-w-7xl w-full mx-auto flex flex-col lg:flex-row">
        {/* Desktop Sidebar / Mobile Drawer Navigation */}
        <aside
          className={`lg:w-64 bg-slate-900 text-slate-300 border-r border-slate-800 lg:block flex-shrink-0 ${
            mobileMenuOpen ? 'block' : 'hidden'
          }`}
        >
          <div className="p-4 space-y-6">
            <div className="space-y-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3">
                Expert Navigation
              </span>
              <nav className="space-y-1 pt-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        onNavigate(item.route);
                        setMobileMenuOpen(false);
                      }}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-xs transition-all ${
                        isActive
                          ? 'bg-emerald-600 text-white shadow-md'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Development Guard Disclaimer Notice */}
            <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 text-[11px] text-slate-400 space-y-1">
              <p className="font-semibold text-slate-300">Development Role Mode</p>
              <p className="text-slate-400 leading-tight">
                Simulated expert session enabled for Phase 5 prototype validation.
              </p>
            </div>
          </div>
        </aside>

        {/* Main Content Workspace */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6">{children}</main>
      </div>
    </div>
  );
};
