import React, { useEffect, useState } from 'react';
import {
  ClipboardList,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
  Loader2,
  Clock
} from 'lucide-react';
import { getExpertDashboardStats, getExpertReviews } from '../../services/api';
import { ExpertDashboardStats, ExpertReviewQueueItem } from '../../types';
import { DashboardStatCard } from '../../components/expert/DashboardStatCard';
import { Badge } from '../../components/Badge';

interface ExpertHomeProps {
  onNavigate: (route: string) => void;
}

export const ExpertHome: React.FC<ExpertHomeProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<ExpertDashboardStats | null>(null);
  const [pendingQueue, setPendingQueue] = useState<ExpertReviewQueueItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      setError(null);
      try {
        const [statsData, queueData] = await Promise.all([
          getExpertDashboardStats(),
          getExpertReviews('PENDING')
        ]);
        setStats(statsData);
        setPendingQueue(queueData.slice(0, 5));
      } catch (err: any) {
        console.error('Failed to load expert dashboard data:', err);
        setError(err.message || 'Could not load expert dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="py-20 text-center space-y-3">
        <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-600">Loading Expert Dashboard Metrics...</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center space-y-4 max-w-md mx-auto">
        <ShieldAlert className="w-10 h-10 text-rose-500 mx-auto" />
        <p className="font-bold text-slate-800">{error || 'Dashboard unavailable.'}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-emerald-700 text-white font-semibold text-xs px-4 py-2 rounded-lg"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-7">
      {/* Workspace Title */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Expert Review Dashboard</h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
          Real-time observation metrics and triage queue operations
        </p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <DashboardStatCard
          title="Total Observations"
          value={stats.total_observations}
          icon={TrendingUp}
          colorScheme="slate"
          description="Total reported farmer cases"
        />
        <DashboardStatCard
          title="Pending Reviews"
          value={stats.pending_reviews}
          icon={ClipboardList}
          colorScheme="amber"
          description="Awaiting expert decision"
          onClick={() => onNavigate('/expert/reviews')}
        />
        <DashboardStatCard
          title="Low Confidence"
          value={stats.low_confidence_cases}
          icon={AlertTriangle}
          colorScheme="rose"
          description="Uncertain AI predictions (<70%)"
          onClick={() => onNavigate('/expert/reviews?status=PENDING')}
        />
        <DashboardStatCard
          title="Completed Reviews"
          value={stats.completed_reviews}
          icon={CheckCircle2}
          colorScheme="emerald"
          description="Ground-truth verified cases"
          onClick={() => onNavigate('/expert/history')}
        />
        <DashboardStatCard
          title="Total Escalations"
          value={stats.total_escalations}
          icon={ShieldAlert}
          colorScheme="blue"
          description="Quality or confidence escalations"
        />
      </div>

      {/* Recent Pending Queue Preview Section */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Priority Pending Queue</h2>
            <p className="text-xs text-slate-500">Unresolved cases requiring expert review</p>
          </div>
          <button
            onClick={() => onNavigate('/expert/reviews')}
            className="inline-flex items-center gap-1.5 text-xs font-extrabold text-emerald-700 hover:text-emerald-900"
          >
            View Full Queue ({stats.pending_reviews})
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {pendingQueue.length === 0 ? (
          <div className="py-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
            <p className="font-bold text-slate-800 text-sm">No Pending Reviews</p>
            <p className="text-xs text-slate-500">All escalated crop observations have been resolved.</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {pendingQueue.map((item) => {
              const confPct = Math.round(item.confidence * 100);
              const isLowConf = item.confidence < 0.70;
              return (
                <div
                  key={item.review_id}
                  onClick={() => onNavigate(`/expert/reviews/${item.review_id}`)}
                  className="p-3.5 rounded-xl border border-slate-200 hover:border-emerald-400 hover:shadow-md transition-all cursor-pointer bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900 text-sm">{item.crop_display_name}</span>
                      <span className="text-xs font-semibold text-emerald-800">AI: {item.predicted_class}</span>
                      {isLowConf && (
                        <span className="text-[10px] bg-rose-100 text-rose-800 px-2 py-0.5 rounded font-bold">
                          Low Conf
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span>Reason: <strong className="text-slate-700">{item.escalation_reason}</strong></span>
                      <span>•</span>
                      <span className="inline-flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {new Date(item.submitted_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-3 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-200">
                    <div className="text-right">
                      <span className="text-[10px] text-slate-400 font-semibold block">Confidence</span>
                      <span className={`text-sm font-extrabold ${isLowConf ? 'text-rose-600' : 'text-emerald-700'}`}>
                        {confPct}%
                      </span>
                    </div>
                    <Badge status={item.review_status} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
