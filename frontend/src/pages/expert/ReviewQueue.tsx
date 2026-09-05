import React, { useEffect, useState } from 'react';
import {
  Search,
  Filter,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Loader2,
  ShieldAlert,
  ArrowUpDown
} from 'lucide-react';
import { getExpertReviews } from '../../services/api';
import { ExpertReviewQueueItem } from '../../types';
import { Badge } from '../../components/Badge';

interface ReviewQueueProps {
  onNavigate: (route: string) => void;
  initialStatusFilter?: string;
}

export const ReviewQueue: React.FC<ReviewQueueProps> = ({ onNavigate, initialStatusFilter }) => {
  const [items, setItems] = useState<ExpertReviewQueueItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters State
  const [statusFilter, setStatusFilter] = useState<string>(initialStatusFilter || 'PENDING');
  const [confidenceFilter, setConfidenceFilter] = useState<string>('ALL');
  const [reasonFilter, setReasonFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadQueue = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getExpertReviews(statusFilter === 'ALL' ? undefined : statusFilter);
      setItems(data);
    } catch (err: any) {
      console.error('Failed to load review queue:', err);
      setError(err.message || 'Could not load expert review queue.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, [statusFilter]);

  // Client-side filtering for Search, Confidence, and Reason
  const filteredItems = items.filter((item) => {
    // Confidence filter
    if (confidenceFilter === 'BELOW_70' && item.confidence >= 0.70) return false;
    if (confidenceFilter === 'ABOVE_70' && item.confidence < 0.70) return false;

    // Reason filter
    if (reasonFilter !== 'ALL' && item.escalation_reason !== reasonFilter) return false;

    // Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchId = item.observation_id.toLowerCase().includes(q) || item.review_id.toLowerCase().includes(q);
      const matchCrop = item.crop_display_name.toLowerCase().includes(q);
      const matchPred = item.predicted_class.toLowerCase().includes(q);
      return matchId || matchCrop || matchPred;
    }

    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Expert Review Queue</h1>
          <p className="text-xs text-slate-500">Triage and evaluate escalated crop observation cases</p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search Case ID, Crop, Prediction..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full p-2 rounded-xl border border-slate-300 text-xs font-semibold bg-white text-slate-800 focus:ring-2 focus:ring-emerald-500"
            >
              <option value="PENDING">Status: Pending Review</option>
              <option value="UNDER_REVIEW">Status: Under Review</option>
              <option value="NEEDS_INFO">Status: Needs Info</option>
              <option value="ALL">Status: All Statuses</option>
            </select>
          </div>

          {/* Confidence Filter */}
          <div>
            <select
              value={confidenceFilter}
              onChange={(e) => setConfidenceFilter(e.target.value)}
              className="w-full p-2 rounded-xl border border-slate-300 text-xs font-semibold bg-white text-slate-800 focus:ring-2 focus:ring-emerald-500"
            >
              <option value="ALL">Confidence: All Scores</option>
              <option value="BELOW_70">Low Confidence (&lt;70%)</option>
              <option value="ABOVE_70">High Confidence (&ge;70%)</option>
            </select>
          </div>

          {/* Reason Filter */}
          <div>
            <select
              value={reasonFilter}
              onChange={(e) => setReasonFilter(e.target.value)}
              className="w-full p-2 rounded-xl border border-slate-300 text-xs font-semibold bg-white text-slate-800 focus:ring-2 focus:ring-emerald-500"
            >
              <option value="ALL">Reason: All Escalations</option>
              <option value="LOW_CONFIDENCE">Low Confidence</option>
              <option value="POOR_IMAGE_QUALITY">Poor Image Quality</option>
              <option value="MANUAL_FARMER_REQUEST">Manual Farmer Request</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Queue Content */}
      {loading ? (
        <div className="py-16 text-center space-y-3 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-600">Loading Review Queue...</p>
        </div>
      ) : error ? (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center space-y-3">
          <ShieldAlert className="w-8 h-8 text-rose-500 mx-auto" />
          <p className="text-sm font-bold text-slate-800">{error}</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="py-12 text-center bg-white rounded-2xl border border-slate-200 space-y-2 p-6">
          <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
          <p className="font-bold text-slate-800">No Cases Found</p>
          <p className="text-xs text-slate-500">No cases match the selected filters or search parameters.</p>
        </div>
      ) : (
        <>
          {/* Desktop Table View */}
          <div className="hidden md:block bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                  <th className="py-3.5 px-4">Case ID</th>
                  <th className="py-3.5 px-4">Crop</th>
                  <th className="py-3.5 px-4">AI Prediction</th>
                  <th className="py-3.5 px-4">Confidence</th>
                  <th className="py-3.5 px-4">Escalation Reason</th>
                  <th className="py-3.5 px-4">Quality</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredItems.map((item) => {
                  const confPct = Math.round(item.confidence * 100);
                  const isLowConf = item.confidence < 0.70;
                  return (
                    <tr
                      key={item.review_id}
                      onClick={() => onNavigate(`/expert/reviews/${item.review_id}`)}
                      className="hover:bg-emerald-50/40 transition-colors cursor-pointer"
                    >
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-800">
                        {item.observation_id.substring(0, 8)}
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">{item.crop_display_name}</td>
                      <td className="py-3.5 px-4 font-semibold text-emerald-900">{item.predicted_class}</td>
                      <td className="py-3.5 px-4">
                        <span className={`font-black ${isLowConf ? 'text-rose-600' : 'text-emerald-700'}`}>
                          {confPct}%
                        </span>
                        {isLowConf && (
                          <span className="ml-1 text-[10px] bg-rose-100 text-rose-800 px-1.5 py-0.5 rounded font-bold">
                            Low
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 font-medium text-slate-700">{item.escalation_reason}</td>
                      <td className="py-3.5 px-4">
                        {item.is_blur_detected ? (
                          <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded text-[11px] font-bold">
                            Blur Warning
                          </span>
                        ) : (
                          <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded text-[11px] font-bold">
                            Good
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <Badge status={item.review_status} />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button className="bg-emerald-700 hover:bg-emerald-800 text-white font-bold px-3 py-1.5 rounded-lg text-[11px]">
                          Inspect & Review
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Mobile/Tablet Stacked Cards */}
          <div className="md:hidden space-y-3">
            {filteredItems.map((item) => {
              const confPct = Math.round(item.confidence * 100);
              const isLowConf = item.confidence < 0.70;
              return (
                <div
                  key={item.review_id}
                  onClick={() => onNavigate(`/expert/reviews/${item.review_id}`)}
                  className="bg-white p-4 rounded-2xl border border-slate-200 hover:border-emerald-400 space-y-3 cursor-pointer"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-mono text-xs font-bold text-slate-400">
                        ID: {item.observation_id.substring(0, 8)}
                      </span>
                      <h3 className="font-bold text-slate-900 text-base">{item.crop_display_name}</h3>
                    </div>
                    <Badge status={item.review_status} />
                  </div>

                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-500 font-medium">AI Prediction:</span>
                      <span className="font-bold text-emerald-900">{item.predicted_class}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500 font-medium">Confidence Score:</span>
                      <span className={`font-extrabold ${isLowConf ? 'text-rose-600' : 'text-emerald-700'}`}>
                        {confPct}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500 font-medium">Reason:</span>
                      <span className="font-semibold text-slate-800">{item.escalation_reason}</span>
                    </div>
                  </div>

                  <div className="flex justify-end pt-1">
                    <span className="text-xs font-bold text-emerald-700 inline-flex items-center gap-1">
                      Start Case Inspection <ChevronRight className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};
