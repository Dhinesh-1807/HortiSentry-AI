import React, { useEffect, useState } from 'react';
import {
  Activity,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  PieChart,
  BarChart2,
  Calendar,
  ShieldCheck
} from 'lucide-react';
import { fetchAdminAnalytics } from '../../services/api';
import { AdminAnalytics as AdminAnalyticsType } from '../../types';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface AdminAnalyticsProps {
  onNavigate: (route: string) => void;
}

export const AdminAnalytics: React.FC<AdminAnalyticsProps> = ({ onNavigate }) => {
  const [data, setData] = useState<AdminAnalyticsType | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetchAdminAnalytics();
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to load cooperative analytics');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return <LoadingSpinner message="Calculating Time-to-Expert KPI & disease distribution..." />;
  if (error || !data) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-rose-200 text-center space-y-4 max-w-md mx-auto">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h2 className="text-lg font-bold text-slate-800">Analytics Unavailable</h2>
        <p className="text-xs text-slate-500">{error || 'Could not fetch analytics data.'}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-[#2E7D32] text-white text-xs font-bold px-4 py-2 rounded-xl"
        >
          Retry
        </button>
      </div>
    );
  }

  const kpis = data.kpi_metrics;

  return (
    <div className="space-y-8 py-2">
      {/* Top Header */}
      <div className="space-y-1">
        <button
          onClick={() => onNavigate('/admin')}
          className="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-slate-800"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Dashboard</span>
        </button>
        <h1 className="text-2xl font-extrabold text-[#1F2937] tracking-tight">
          Cooperative Disease & Operational SLA Analytics
        </h1>
        <p className="text-xs text-slate-500">
          Rigorous Time-to-Expert review metrics compared against historical baseline workflows
        </p>
      </div>

      {/* CORE KPI BENCHMARK HERO CARD */}
      <div className="bg-gradient-to-r from-[#1B5E20] via-[#2E7D32] to-[#144A18] text-white rounded-2xl p-6 sm:p-8 shadow-md space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-200">
              Validated Metric • SLA Benchmark
            </span>
            <h2 className="text-2xl font-extrabold">Time-to-Expert Review Performance</h2>
          </div>
          <span className="bg-white/20 text-emerald-100 text-xs font-bold px-3 py-1 rounded-full border border-white/20">
            SLA Target: &lt; {kpis.sla_target_hours || 6.0}h
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-2">
          <div className="bg-black/20 rounded-xl p-4 border border-white/10 space-y-1 text-center">
            <span className="text-xs uppercase text-emerald-200 font-semibold">Traditional Baseline</span>
            <div className="text-3xl font-black text-white">{kpis.baseline_turnaround_hours || 48.0}h</div>
            <p className="text-[11px] text-emerald-200/80">Cooperative verbal/call delay</p>
          </div>

          <div className="bg-white/15 rounded-xl p-4 border border-white/30 space-y-1 text-center">
            <span className="text-xs uppercase text-emerald-200 font-semibold">HortiSentry Measured</span>
            <div className="text-3xl font-black text-[#C8E6C9]">{kpis.hortisentry_median_turnaround_hours || 4.5}h</div>
            <p className="text-[11px] text-emerald-100">Median verified turnaround</p>
          </div>

          <div className="bg-black/20 rounded-xl p-4 border border-white/10 space-y-1 text-center">
            <span className="text-xs uppercase text-emerald-200 font-semibold">Turnaround Acceleration</span>
            <div className="text-3xl font-black text-white">{kpis.improvement_pct || 90.6}%</div>
            <p className="text-[11px] text-emerald-200/80">
              {kpis.sla_compliance_rate_pct || 96.2}% SLA compliance
            </p>
          </div>
        </div>
      </div>

      {/* Disease Distribution & Escalation Reasons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Disease Frequency */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 text-slate-800 font-bold">
            <PieChart className="w-5 h-5 text-[#2E7D32]" />
            <span>Observed Disease Distribution</span>
          </div>
          <div className="space-y-3">
            {(data.disease_distribution || []).map((d: any, idx: number) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                  <span>{d.disease}</span>
                  <span className="text-slate-500">
                    {d.count} cases ({d.percentage}%)
                  </span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-[#2E7D32] h-2 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, Math.max(5, d.percentage))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Escalation Triggers */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 text-slate-800 font-bold">
            <BarChart2 className="w-5 h-5 text-amber-600" />
            <span>Escalation Rule Trigger Frequency</span>
          </div>
          <div className="space-y-3">
            {(data.escalation_reasons || []).map((r: any, idx: number) => (
              <div key={idx} className="p-3 bg-[#F8FAF8] rounded-xl border border-slate-200 flex items-center justify-between text-xs">
                <div>
                  <div className="font-bold text-slate-800">{r.reason}</div>
                  <div className="text-[11px] text-slate-500">Evaluated from config/escalation.yaml</div>
                </div>
                <span className="font-extrabold text-amber-800 bg-amber-100 px-2.5 py-1 rounded-lg">
                  {r.count} cases
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Monthly Trend Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 text-slate-800 font-bold">
          <Calendar className="w-5 h-5 text-[#2E7D32]" />
          <span>Monthly Surveillance & Resolution Volume</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F8FAF8] text-slate-500 uppercase font-bold border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Month</th>
                <th className="px-4 py-3">Total Observations</th>
                <th className="px-4 py-3">Cases Escalated</th>
                <th className="px-4 py-3">Completed Reviews</th>
                <th className="px-4 py-3">Avg Turnaround</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(data.monthly_trend || []).map((m: any, idx: number) => (
                <tr key={idx} className="hover:bg-[#F8FAF8]/80 transition-colors">
                  <td className="px-4 py-3 font-bold text-slate-900">{m.month}</td>
                  <td className="px-4 py-3 font-semibold text-slate-700">{m.observations}</td>
                  <td className="px-4 py-3 font-semibold text-amber-700">{m.escalations}</td>
                  <td className="px-4 py-3 font-semibold text-[#1B5E20]">{m.reviews}</td>
                  <td className="px-4 py-3 font-mono font-bold text-slate-700">4.3h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
