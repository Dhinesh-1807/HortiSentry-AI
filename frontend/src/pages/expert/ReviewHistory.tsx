import React, { useEffect, useState } from 'react';
import { History, CheckCircle2, Search, Loader2, ShieldAlert, ChevronRight } from 'lucide-react';
import { getExpertReviews, getExpertReviewDetail } from '../../services/api';
import { ExpertReviewQueueItem, ExpertReviewDetail } from '../../types';
import { Badge } from '../../components/Badge';

interface ReviewHistoryProps {
  onNavigate: (route: string) => void;
}

export const ReviewHistory: React.FC<ReviewHistoryProps> = ({ onNavigate }) => {
  const [completedItems, setCompletedItems] = useState<ExpertReviewQueueItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    const loadHistory = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getExpertReviews('COMPLETED');
        setCompletedItems(data);
      } catch (err: any) {
        console.error('Failed to load review history:', err);
        setError(err.message || 'Could not load completed expert review history.');
      } finally {
        setLoading(false);
      }
    };
    loadHistory();
  }, []);

  const filteredItems = completedItems.filter((item) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.observation_id.toLowerCase().includes(q) ||
      item.crop_display_name.toLowerCase().includes(q) ||
      item.predicted_class.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Completed Review Audit Log</h1>
          <p className="text-xs text-slate-500">Historical record of ground-truth expert diagnoses</p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm max-w-md">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search Case ID, Crop, AI Prediction..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      {loading ? (
        <div className="py-16 text-center space-y-3 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-600">Loading Completed Reviews...</p>
        </div>
      ) : error ? (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center space-y-3">
          <ShieldAlert className="w-8 h-8 text-rose-500 mx-auto" />
          <p className="text-sm font-bold text-slate-800">{error}</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="py-12 text-center bg-white rounded-2xl border border-slate-200 space-y-2 p-6">
          <History className="w-10 h-10 text-slate-400 mx-auto mb-2" />
          <p className="font-bold text-slate-800">No Completed Reviews Yet</p>
          <p className="text-xs text-slate-500 max-w-xs mx-auto">
            Completed expert diagnoses will be logged here for evaluation and auditability.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <th className="py-3.5 px-4">Case ID</th>
                <th className="py-3.5 px-4">Crop</th>
                <th className="py-3.5 px-4">AI Prediction</th>
                <th className="py-3.5 px-4">AI Confidence</th>
                <th className="py-3.5 px-4">Expert Ground-Truth</th>
                <th className="py-3.5 px-4">Review Status</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredItems.map((item) => {
                const confPct = Math.round(item.confidence * 100);
                return (
                  <tr
                    key={item.review_id}
                    onClick={() => onNavigate(`/expert/reviews/${item.review_id}`)}
                    className="hover:bg-slate-50 transition-colors cursor-pointer"
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-800">
                      {item.observation_id.substring(0, 8)}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-slate-900">{item.crop_display_name}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-700">{item.predicted_class}</td>
                    <td className="py-3.5 px-4 font-bold font-mono text-slate-600">{confPct}%</td>
                    <td className="py-3.5 px-4">
                      <span className="font-extrabold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">
                        Verified Diagnostic Case
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge status={item.review_status} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <span className="text-emerald-700 font-bold hover:underline inline-flex items-center gap-1">
                        Inspect <ChevronRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
