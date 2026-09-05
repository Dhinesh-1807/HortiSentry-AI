import React, { useEffect, useState } from 'react';
import {
  Users,
  ShieldCheck,
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  Activity,
  ArrowRight,
  Database,
  Cpu,
  Layers,
  History
} from 'lucide-react';
import { fetchAdminDashboard } from '../../services/api';
import { AdminDashboardStats } from '../../types';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface AdminDashboardProps {
  onNavigate: (route: string) => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await fetchAdminDashboard();
        setStats(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load cooperative administration metrics');
      } finally {
        setLoading(false);
      }
    };
    loadStats();
  }, []);

  if (loading) return <LoadingSpinner message="Loading cooperative administration dashboard..." />;
  if (error || !stats) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-rose-200 text-center space-y-4 max-w-md mx-auto">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h2 className="text-lg font-bold text-slate-800">Admin Service Unavailable</h2>
        <p className="text-xs text-slate-500">{error || 'Could not fetch admin statistics.'}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-[#2E7D32] text-white text-xs font-bold px-4 py-2 rounded-xl"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 py-2">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 bg-[#E8F5E9] text-[#1B5E20] border border-[#C8E6C9] px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <ShieldCheck className="w-4 h-4 text-[#2E7D32]" />
            <span>Cooperative Management Portal</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1F2937] tracking-tight">
            Administrative Control Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            System overview, user role management, and operational Time-to-Expert KPI tracking
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 bg-[#E8F5E9] text-[#1B5E20] border border-[#C8E6C9] text-xs font-bold px-3 py-1.5 rounded-xl">
            <span className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse" />
            Backend Active: {stats.system_health || 'OPERATIONAL'}
          </span>
        </div>
      </div>

      {/* Primary KPI Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Registered Users</span>
            <Users className="w-4 h-4 text-[#2E7D32]" />
          </div>
          <div className="text-3xl font-black text-[#1F2937]">{stats.total_users}</div>
          <p className="text-[11px] text-slate-500">Farmers, Reviewers, Admins</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Total Observations</span>
            <FileText className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-3xl font-black text-emerald-800">{stats.total_observations}</div>
          <p className="text-[11px] text-slate-500">Captured crop cases</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Pending Escalations</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-black text-amber-700">{stats.pending_escalations}</div>
          <p className="text-[11px] text-slate-500">Awaiting agronomist</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Completed Reviews</span>
            <CheckCircle2 className="w-4 h-4 text-[#2E7D32]" />
          </div>
          <div className="text-3xl font-black text-[#1B5E20]">{stats.completed_reviews}</div>
          <p className="text-[11px] text-slate-500">Dual-audit verified</p>
        </div>
      </div>

      {/* KPI Benchmark Highlight Box */}
      <div className="bg-gradient-to-r from-[#1B5E20] to-[#2E7D32] text-white rounded-2xl p-6 sm:p-8 shadow-md">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <div className="inline-flex items-center gap-1.5 bg-white/20 text-emerald-100 text-xs font-bold px-3 py-0.5 rounded-full">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-300" />
              <span>Core Operational Milestone</span>
            </div>
            <h2 className="text-2xl font-black">Time-to-Expert Review: 90.6% Faster</h2>
            <p className="text-xs sm:text-sm text-emerald-100/90 leading-relaxed">
              Cooperative baseline turnaround without HortiSentry: <span className="font-bold underline">48.0 hours</span>.
              HortiSentry verified turnaround: <span className="font-bold underline">4.5 hours</span>. Exceeds the target &lt;6.0h SLA with 96.2% compliance.
            </p>
          </div>
          <button
            onClick={() => onNavigate('/admin/analytics')}
            className="bg-white text-[#1B5E20] hover:bg-[#E8F5E9] font-bold text-xs sm:text-sm px-5 py-3 rounded-xl shadow-sm transition-all whitespace-nowrap inline-flex items-center gap-2"
          >
            <span>View Detailed Analytics</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Admin Quick Link Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          onClick={() => onNavigate('/admin/users')}
          className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-[#E8F5E9] text-[#1B5E20] flex items-center justify-center font-bold">
            <Users className="w-5 h-5 text-[#2E7D32]" />
          </div>
          <h3 className="font-bold text-slate-800 text-sm">User & Role Management</h3>
          <p className="text-xs text-slate-500">
            View cooperative membership, assign roles (Farmer, Expert, Admin), and toggle account active status.
          </p>
        </div>

        <div
          onClick={() => onNavigate('/admin/crops')}
          className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-[#E8F5E9] text-[#1B5E20] flex items-center justify-center font-bold">
            <Layers className="w-5 h-5 text-[#2E7D32]" />
          </div>
          <h3 className="font-bold text-slate-800 text-sm">Crop Catalogue Management</h3>
          <p className="text-xs text-slate-500">
            Configure 32 horticultural crops across vegetables, fruits, and spices, vision support, and taxonomy.
          </p>
        </div>

        <div
          onClick={() => onNavigate('/admin/analytics')}
          className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-[#E8F5E9] text-[#1B5E20] flex items-center justify-center font-bold">
            <Activity className="w-5 h-5 text-[#2E7D32]" />
          </div>
          <h3 className="font-bold text-slate-800 text-sm">Disease Analytics & SLA</h3>
          <p className="text-xs text-slate-500">
            Track regional disease frequency, monthly submission trends, and Time-to-Expert compliance curves.
          </p>
        </div>

        <div
          onClick={() => onNavigate('/admin/model')}
          className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-[#E8F5E9] text-[#1B5E20] flex items-center justify-center font-bold">
            <Cpu className="w-5 h-5 text-[#2E7D32]" />
          </div>
          <h3 className="font-bold text-slate-800 text-sm">Model Metrics & Dataset Splits</h3>
          <p className="text-xs text-slate-500">
            MobileNetV3 test set performance (94.16% accuracy), per-class F1 scores, and balanced dataset reports.
          </p>
        </div>

        <div
          onClick={() => onNavigate('/admin/audit-logs')}
          className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-[#E8F5E9] text-[#1B5E20] flex items-center justify-center font-bold">
            <History className="w-5 h-5 text-[#2E7D32]" />
          </div>
          <h3 className="font-bold text-slate-800 text-sm">Cooperative Audit Logs</h3>
          <p className="text-xs text-slate-500">
            Full compliance traceability log of all observation submissions, AI predictions, and expert overrides.
          </p>
        </div>

        <div
          onClick={() => onNavigate('/expert/queue')}
          className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-[#E8F5E9] text-[#1B5E20] flex items-center justify-center font-bold">
            <ShieldCheck className="w-5 h-5 text-[#2E7D32]" />
          </div>
          <h3 className="font-bold text-slate-800 text-sm">Expert Triage Queue</h3>
          <p className="text-xs text-slate-500">
            Direct access to inspect high-priority escalated cases currently awaiting agricultural extension review.
          </p>
        </div>
      </div>
    </div>
  );
};
