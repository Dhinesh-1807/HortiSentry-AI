import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  PlusCircle,
  History,
  Leaf,
  ArrowRight,
  Clock,
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  FileText
} from 'lucide-react';
import { fetchObservations } from '../../services/api';
import { ObservationListItem, CropConfig } from '../../types';
import { Badge } from '../../components/Badge';

interface FarmerHomeProps {
  crops: CropConfig[];
  onNavigate: (route: string) => void;
}

export const FarmerHome: React.FC<FarmerHomeProps> = ({ crops, onNavigate }) => {
  const [observations, setObservations] = useState<ObservationListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const list = await fetchObservations();
        setObservations(list);
      } catch (err) {
        console.error('Failed to load farmer observations:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const totalObs = observations.length;
  const pendingReviews = observations.filter(
    (o) => o.status === 'PENDING' || o.status === 'ESCALATED' || o.status === 'SUBMITTED'
  ).length;
  const reviewedCount = observations.filter((o) => o.status === 'COMPLETED').length;
  const highRiskCount = observations.filter(
    (o) => o.risk_level === 'HIGH' || (o.predicted_class && o.predicted_class.toLowerCase().includes('late blight'))
  ).length;

  const recentObservations = observations.slice(0, 4);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Brand Hero Banner */}
      <div className="bg-gradient-to-br from-[#1B5E20] via-[#2E7D32] to-[#144A18] text-white rounded-2xl p-6 sm:p-8 shadow-lg relative overflow-hidden">
        <div className="absolute top-0 right-0 transform translate-x-6 -translate-y-6 opacity-10 pointer-events-none">
          <ShieldCheck className="w-56 h-56" />
        </div>
        <div className="relative z-10 space-y-3 max-w-xl">
          <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold text-emerald-100 border border-white/20">
            <Leaf className="w-3.5 h-3.5 text-emerald-300" />
            <span>Cooperative Field Surveillance</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">Farmer Portal</h1>
          <p className="text-emerald-100 text-xs sm:text-sm font-medium leading-relaxed">
            Record leaf symptoms early, obtain immediate AI preliminary screening, and escalate high-risk cases to cooperative agricultural specialists.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('/farmer/observation/new')}
              className="inline-flex items-center gap-2 bg-white text-[#1B5E20] hover:bg-[#E8F5E9] font-bold px-5 py-3 rounded-xl shadow-md transition-all active:scale-[0.98] text-sm"
            >
              <PlusCircle className="w-5 h-5 text-[#2E7D32]" />
              <span>Report Crop Disease</span>
            </button>
            <button
              onClick={() => onNavigate('/farmer/observations')}
              className="inline-flex items-center gap-2 bg-[#1B5E20]/40 hover:bg-[#1B5E20]/70 text-white font-semibold px-4 py-3 rounded-xl border border-white/20 transition-all text-sm"
            >
              <History className="w-4 h-4" />
              <span>Observation History</span>
            </button>
          </div>
        </div>
      </div>

      {/* 4 KPI CARDS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Total Reports</span>
            <FileText className="w-4 h-4 text-[#2E7D32]" />
          </div>
          <div className="text-2xl font-extrabold text-[#1F2937]">{loading ? '—' : totalObs}</div>
          <p className="text-[11px] text-slate-500">Recorded crop cases</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Pending Expert</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-extrabold text-amber-700">{loading ? '—' : pendingReviews}</div>
          <p className="text-[11px] text-slate-500">In review triage</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Expert Reviewed</span>
            <CheckCircle2 className="w-4 h-4 text-[#2E7D32]" />
          </div>
          <div className="text-2xl font-extrabold text-[#1B5E20]">{loading ? '—' : reviewedCount}</div>
          <p className="text-[11px] text-slate-500">Verified recommendations</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">High Risk</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-extrabold text-rose-700">{loading ? '—' : highRiskCount}</div>
          <p className="text-[11px] text-slate-500">Urgent action required</p>
        </div>
      </div>

      {/* Advisory Guidance Box */}
      <div className="bg-[#E8F5E9] border border-[#C8E6C9] rounded-xl p-4 flex items-start gap-3 text-[#1B5E20]">
        <AlertCircle className="w-5 h-5 text-[#2E7D32] flex-shrink-0 mt-0.5" />
        <div className="text-xs sm:text-sm leading-relaxed">
          <span className="font-bold">Horticultural Guidance: </span>
          Upload clear, in-focus photos of affected leaves in good daylight. AI observations with low confidence or aggressive diseases (e.g., Late Blight) are automatically escalated to cooperative plant specialists with a target SLA under 6 hours.
        </div>
      </div>

      {/* Recent Observations Section */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-slate-800 font-bold">
            <History className="w-5 h-5 text-[#2E7D32]" />
            <span>Recent Observations</span>
          </div>
          {observations.length > 0 && (
            <button
              onClick={() => onNavigate('/farmer/observations')}
              className="text-xs font-bold text-[#2E7D32] hover:text-[#1B5E20] inline-flex items-center gap-1"
            >
              View All ({observations.length}) <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {loading ? (
          <div className="py-8 text-center text-slate-400 text-sm">Loading recent observations...</div>
        ) : recentObservations.length === 0 ? (
          <div className="py-8 text-center bg-[#F8FAF8] rounded-xl border border-dashed border-slate-200 space-y-3">
            <div className="w-12 h-12 bg-[#E8F5E9] text-[#1B5E20] rounded-full flex items-center justify-center mx-auto">
              <Leaf className="w-6 h-6 text-[#2E7D32]" />
            </div>
            <div>
              <p className="font-semibold text-slate-700">No observations yet</p>
              <p className="text-xs text-slate-500 max-w-xs mx-auto mt-1">
                Start by reporting your first crop observation to monitor plant health.
              </p>
            </div>
            <button
              onClick={() => onNavigate('/farmer/observation/new')}
              className="inline-flex items-center gap-1.5 bg-[#2E7D32] text-white font-semibold text-xs px-4 py-2 rounded-lg hover:bg-[#1B5E20] transition-colors"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Create Your First Observation</span>
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {recentObservations.map((obs) => (
              <div
                key={obs.id}
                onClick={() => onNavigate(`/farmer/observations/${obs.id}`)}
                className="p-3.5 rounded-xl border border-slate-200 hover:border-[#2E7D32] hover:shadow-xs transition-all cursor-pointer bg-[#F8FAF8]/50 flex items-center justify-between gap-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-800 text-sm">{obs.crop_display_name}</span>
                    <span className="text-xs text-slate-500">• {obs.crop_stage}</span>
                    {obs.risk_level === 'HIGH' && (
                      <span className="bg-rose-100 text-rose-800 text-[10px] font-extrabold px-2 py-0.5 rounded-full border border-rose-200">
                        High Risk
                      </span>
                    )}
                  </div>
                  <p className="text-xs font-semibold text-[#1B5E20]">
                    {obs.predicted_class ? `AI: ${obs.predicted_class}` : 'AI Screening Pending'}
                  </p>
                  <div className="flex items-center gap-2 text-[11px] text-slate-400">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(obs.submitted_at).toLocaleDateString()}</span>
                    <span>({obs.location_village})</span>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <Badge status={obs.status} />
                  {obs.confidence !== undefined && obs.confidence > 0 && (
                    <span className="text-xs font-bold text-slate-600">
                      {Math.round(obs.confidence * 100)}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
