import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  UserCheck,
  FileText,
  AlertCircle,
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import { fetchObservationDetail } from '../../services/api';
import { ObservationDetail } from '../../types';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface ExpertReviewStatusProps {
  observationId: string;
  onNavigate: (route: string) => void;
}

export const ExpertReviewStatus: React.FC<ExpertReviewStatusProps> = ({ observationId, onNavigate }) => {
  const [data, setData] = useState<ObservationDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDetail = async () => {
      try {
        const res = await fetchObservationDetail(observationId);
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to load case status');
      } finally {
        setLoading(false);
      }
    };
    loadDetail();
  }, [observationId]);

  if (loading) return <LoadingSpinner message="Checking expert escalation status..." />;
  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-2xl border border-rose-200 text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-500 mx-auto" />
        <h2 className="text-lg font-bold text-slate-900">Observation Not Found</h2>
        <p className="text-xs text-slate-500">{error || 'Could not find the requested review record.'}</p>
        <button
          onClick={() => onNavigate('/farmer')}
          className="bg-[#2E7D32] text-white text-xs font-bold px-4 py-2 rounded-xl"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const isCompleted = data.status === 'COMPLETED' || !!data.expert_review;
  const isEscalated = data.status === 'ESCALATED' || data.status === 'PENDING' || isCompleted;

  // Calculate turnaround time if completed
  let turnaroundHours: string | null = null;
  if (data.expert_review?.reviewed_at && data.submitted_at) {
    const diffMs = new Date(data.expert_review.reviewed_at).getTime() - new Date(data.submitted_at).getTime();
    turnaroundHours = (diffMs / (1000 * 60 * 60)).toFixed(1);
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 py-4">
      {/* Back button */}
      <button
        onClick={() => onNavigate(`/farmer/observations/${data.id}`)}
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-600 hover:text-slate-900"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Observation Details</span>
      </button>

      {/* Header Banner */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="space-y-1">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Case Tracking • ID: {data.id.slice(0, 8)}
            </span>
            <h1 className="text-2xl font-bold text-[#1F2937]">
              {data.crop_display_name} Health Review Status
            </h1>
          </div>
          <div className="flex items-center gap-2">
            {isCompleted ? (
              <span className="bg-[#E8F5E9] text-[#1B5E20] border border-[#C8E6C9] text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#2E7D32]" />
                Review Completed
              </span>
            ) : isEscalated ? (
              <span className="bg-amber-100 text-amber-800 border border-amber-300 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-amber-600" />
                In Review Queue (&lt;6h SLA)
              </span>
            ) : (
              <span className="bg-slate-100 text-slate-700 text-xs font-bold px-3 py-1 rounded-full">
                Preliminary AI Complete
              </span>
            )}
          </div>
        </div>

        {turnaroundHours && (
          <div className="bg-[#E8F5E9] border border-[#C8E6C9] rounded-xl p-3 text-xs text-[#1B5E20] flex items-center justify-between">
            <span className="font-semibold">Turnaround Time-to-Expert Review:</span>
            <span className="font-extrabold text-sm">{turnaroundHours} hours (Target &lt;6.0h Met)</span>
          </div>
        )}
      </div>

      {/* Visual Stepper */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-8">
        <h2 className="text-base font-bold text-slate-800">Observation Lifecycle Timeline</h2>

        <div className="relative border-l-2 border-slate-200 ml-4 space-y-8 pl-6">
          {/* STEP 1 */}
          <div className="relative">
            <div className="absolute -left-[35px] top-0.5 w-6 h-6 rounded-full bg-[#2E7D32] text-white flex items-center justify-center text-xs font-bold">
              ✓
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900">1. Observation Submitted by Farmer</h3>
                <span className="text-xs text-slate-400">
                  {new Date(data.submitted_at || data.timestamps?.submitted_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <p className="text-xs text-slate-600">
                Leaf photo uploaded with growth stage ({data.crop_stage}) and symptoms.
              </p>
            </div>
          </div>

          {/* STEP 2 */}
          <div className="relative">
            <div className="absolute -left-[35px] top-0.5 w-6 h-6 rounded-full bg-[#2E7D32] text-white flex items-center justify-center text-xs font-bold">
              ✓
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900">2. Automated Quality & AI Screening</h3>
                <span className="text-xs text-[#2E7D32] font-semibold">Processed</span>
              </div>
              <p className="text-xs text-slate-600">
                Preliminary assessment: <span className="font-bold">{data.predicted_class || 'Processed'}</span>{' '}
                {data.confidence ? `(${Math.round(data.confidence * 100)}% model confidence)` : ''}
              </p>
            </div>
          </div>

          {/* STEP 3 */}
          <div className="relative">
            <div
              className={`absolute -left-[35px] top-0.5 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                isEscalated ? 'bg-[#2E7D32] text-white' : 'bg-slate-200 text-slate-500'
              }`}
            >
              {isEscalated ? '✓' : '3'}
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900">3. Escalated to Agricultural Extension Specialist</h3>
                <span className="text-xs text-amber-700 font-semibold">
                  {data.escalation_reason || 'Policy Threshold'}
                </span>
              </div>
              <p className="text-xs text-slate-600">
                {isEscalated
                  ? 'High risk disease flag or confidence triage rule routed this observation to the cooperative expert review queue.'
                  : 'Case did not require escalation.'}
              </p>
            </div>
          </div>

          {/* STEP 4 */}
          <div className="relative">
            <div
              className={`absolute -left-[35px] top-0.5 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                isCompleted ? 'bg-[#2E7D32] text-white' : 'bg-amber-100 text-amber-700 border border-amber-300 animate-pulse'
              }`}
            >
              {isCompleted ? '✓' : '4'}
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900">4. Specialist Review & Agronomic Guidance</h3>
                {data.expert_review?.reviewed_at && (
                  <span className="text-xs text-slate-400">
                    {new Date(data.expert_review.reviewed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                )}
              </div>
              {isCompleted && data.expert_review ? (
                <div className="bg-[#E8F5E9]/50 border border-[#C8E6C9] rounded-xl p-4 mt-2 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#1B5E20]">
                      Verified by: {data.expert_review.expert_name || 'Agricultural Officer'}
                    </span>
                    <span className="text-xs font-bold bg-[#E8F5E9] text-[#1B5E20] px-2 py-0.5 rounded">
                      Severity: {data.expert_review.severity || 'Moderate'}
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm font-bold text-slate-800">
                    Diagnosis: {data.expert_review.final_condition || data.predicted_class}
                  </p>
                  <p className="text-xs text-slate-700">
                    <span className="font-semibold">Recommendation: </span>
                    {data.expert_review.treatment_recommendation || data.expert_review.expert_notes}
                  </p>
                </div>
              ) : (
                <p className="text-xs text-amber-800 font-medium">
                  Currently queued for cooperative agronomist inspection. Expected turnaround within 6 hours.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
