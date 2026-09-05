import React, { useEffect, useState } from 'react';
import {
  ArrowLeft,
  Calendar,
  MapPin,
  FileText,
  UserCheck,
  ShieldAlert,
  Loader2,
  AlertTriangle,
  ExternalLink,
  Leaf,
  Clock,
  Sparkles,
  Info
} from 'lucide-react';
import { fetchObservationDetail, escalateObservation } from '../../services/api';
import { ObservationDetail as ObservationDetailType } from '../../types';
import { Badge } from '../../components/Badge';
import { Alert } from '../../components/Alert';
import { ErrorBoundary } from '../../components/ErrorBoundary';

interface ObservationDetailProps {
  observationId: string;
  onNavigate: (route: string) => void;
}

export const ObservationDetail: React.FC<ObservationDetailProps> = ({ observationId, onNavigate }) => {
  const [data, setData] = useState<ObservationDetailType | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [escalating, setEscalating] = useState<boolean>(false);
  const [imgError, setImgError] = useState<boolean>(false);

  const loadDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const obs = await fetchObservationDetail(observationId);
      setData(obs);
    } catch (err: any) {
      console.error('Error loading observation detail:', err);
      setError(err.message || 'Failed to load observation detail.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (observationId) loadDetail();
  }, [observationId]);

  const handleEscalate = async () => {
    setEscalating(true);
    try {
      await escalateObservation(observationId, 'Manual farmer request from detail screen');
      await loadDetail();
    } catch (err: any) {
      alert(err.message || 'Escalation failed');
    } finally {
      setEscalating(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-4">
        <Loader2 className="w-10 h-10 text-[#2E7D32] animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-700">Loading Observation Records...</p>
        <p className="text-xs text-slate-400">Retrieving disease observation telemetry and expert notes</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-md mx-auto bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 text-center space-y-4 shadow-sm my-8">
        <div className="w-12 h-12 bg-rose-50 text-rose-600 rounded-full flex items-center justify-center mx-auto">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h3 className="font-bold text-slate-900 text-base">Observation Not Found</h3>
          <p className="text-xs text-slate-500">{error || 'Case details could not be retrieved from the database.'}</p>
        </div>
        <button
          onClick={() => onNavigate('/farmer/observations')}
          className="bg-[#2E7D32] hover:bg-[#1B5E20] text-white font-bold text-xs px-5 py-2.5 rounded-xl transition-all shadow-sm"
        >
          Return to History
        </button>
      </div>
    );
  }

  // Safe Symptoms Parsing
  const symptomsList: string[] = Array.isArray(data.symptoms)
    ? data.symptoms
    : typeof data.symptoms === 'string'
      ? (() => {
          try {
            const parsed = JSON.parse(data.symptoms);
            return Array.isArray(parsed) ? parsed : [data.symptoms];
          } catch {
            return [data.symptoms];
          }
        })()
      : [];

  // Safe Timestamp Resolution
  const submittedAtRaw = data.submitted_at || data.timestamps?.submitted_at;
  const submittedFormatted = submittedAtRaw
    ? new Date(submittedAtRaw).toLocaleString()
    : 'Recently submitted';

  // Safe Confidence
  const confidencePct = data.prediction?.confidence != null
    ? Math.round(data.prediction.confidence * 100)
    : (data.confidence != null ? Math.round(data.confidence * 100) : 0);

  // Safe Image URL
  const imageSrc = data.image?.image_url
    ? data.image.image_url
    : data.image?.file_name
      ? `/uploads/${data.image.file_name}`
      : null;

  // Safe Location
  const locationString = data.location
    ? [data.location.village, data.location.district, data.location.state].filter(Boolean).join(', ')
    : 'Location not recorded';

  const isEscalated = data.escalation?.is_escalated || data.status === 'ESCALATED' || data.status === 'EXPERT_REVIEW_REQUIRED';
  const isExpertReviewed = data.expert_review?.status === 'COMPLETED' || data.status === 'COMPLETED' || data.status === 'EXPERT_REVIEWED';

  return (
    <ErrorBoundary fallbackTitle="Observation Detail View Error" onReset={() => onNavigate('/farmer/observations')}>
      <div className="max-w-3xl mx-auto space-y-5 pb-10">
        {/* Top Navigation & Status Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => onNavigate('/farmer/observations')}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-slate-900 bg-white border border-slate-200 px-3.5 py-2 rounded-xl transition-all hover:border-slate-300 shadow-2xs"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to History
          </button>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-bold text-slate-400">ID: {data.id.slice(0, 8)}</span>
            <Badge status={data.status} />
          </div>
        </div>

        {/* Primary Case Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 sm:p-7 shadow-xs space-y-6">
          {/* Leaf Image & Basic Meta Header */}
          <div className="flex flex-col sm:flex-row gap-5 items-start">
            <div className="w-full sm:w-52 h-52 rounded-2xl overflow-hidden bg-slate-100 border border-slate-200 shrink-0 flex items-center justify-center relative">
              {imageSrc && !imgError ? (
                <img
                  src={imageSrc}
                  alt={data.crop_display_name || 'Crop Leaf'}
                  className="w-full h-full object-cover"
                  onError={() => setImgError(true)}
                />
              ) : (
                <div className="text-center p-4 space-y-2 text-slate-400">
                  <Leaf className="w-12 h-12 mx-auto text-emerald-600/40" />
                  <span className="text-[11px] font-semibold block text-slate-500">Leaf Image Record</span>
                </div>
              )}
            </div>

            <div className="space-y-3 grow">
              <div>
                <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                  {data.crop_display_name || 'Horticulture Crop'}
                </h1>
                <p className="text-xs text-slate-500 font-semibold mt-0.5">
                  Growth Stage: <span className="text-slate-800 font-bold">{data.crop_stage || 'Not specified'}</span>
                  {data.variety && <span> • Variety: <strong className="text-slate-800">{data.variety}</strong></span>}
                </p>
              </div>

              {/* AI Diagnostic Screening Summary */}
              <div className="bg-[#E8F5E9]/60 p-4 rounded-xl border border-[#C8E6C9] space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-extrabold text-[#1B5E20] uppercase tracking-wider inline-flex items-center gap-1">
                    <Sparkles className="w-3 h-3" /> AI Screening Observation
                  </span>
                  <span className="text-[10px] font-mono bg-white/80 border border-[#C8E6C9] text-[#1B5E20] px-2 py-0.5 rounded-md font-bold">
                    {data.prediction?.is_demo_mode ? 'DEMO MODE' : 'REAL ML MODEL'}
                  </span>
                </div>
                <p className="text-lg font-black text-[#1B5E20]">
                  {data.prediction?.predicted_class || data.predicted_class || 'Screening Completed'}
                </p>
                <div className="flex items-center justify-between text-xs text-[#2E7D32] pt-0.5">
                  <span>Confidence: <strong className="font-extrabold">{confidencePct}%</strong></span>
                  <button
                    onClick={() => onNavigate(`/ai-review/${data.id}`)}
                    className="text-[11px] font-bold text-[#1B5E20] hover:underline inline-flex items-center gap-1"
                  >
                    View AI Sources <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>

              {/* Metadata details */}
              <div className="text-xs text-slate-500 space-y-1.5 pt-1">
                <div className="flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span className="text-slate-700 font-medium">{locationString}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span>Submitted: <strong className="text-slate-700">{submittedFormatted}</strong></span>
                </div>
              </div>
            </div>
          </div>

          {/* Reported Visual Symptoms */}
          <div className="pt-4 border-t border-slate-100 space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Reported Visual Symptoms
            </h3>
            {symptomsList.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {symptomsList.map((sym, idx) => (
                  <span
                    key={idx}
                    className="bg-slate-100 text-slate-800 px-3 py-1.5 rounded-lg text-xs font-semibold border border-slate-200/60"
                  >
                    {sym}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">No specific symptoms recorded</p>
            )}
          </div>

          {/* Field Notes if provided */}
          {data.notes && (
            <div className="pt-3 border-t border-slate-100 space-y-1.5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Farmer Field Notes
              </h3>
              <p className="text-xs text-slate-700 bg-slate-50 p-3.5 rounded-xl border border-slate-200 italic">
                "{data.notes}"
              </p>
            </div>
          )}

          {/* Expert Review & Escalation Status */}
          <div className="pt-4 border-t border-slate-100 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Agronomic Specialist Review
              </h3>
              {isEscalated && (
                <button
                  onClick={() => onNavigate(`/farmer/reviews/${data.id}`)}
                  className="text-xs font-bold text-[#2E7D32] hover:text-[#1B5E20] inline-flex items-center gap-1"
                >
                  View Review Stepper <ExternalLink className="w-3 h-3" />
                </button>
              )}
            </div>

            {isExpertReviewed ? (
              <div className="bg-[#E8F5E9] border border-[#A5D6A7] rounded-xl p-4 sm:p-5 space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-[#1B5E20] font-bold text-sm">
                    <UserCheck className="w-5 h-5 text-[#2E7D32]" />
                    <span>Specialist Ground-Truth Assessment</span>
                  </div>
                  {data.expert_review?.severity && (
                    <span className="text-[11px] font-extrabold bg-[#C8E6C9] text-[#1B5E20] px-2.5 py-0.5 rounded-md uppercase">
                      Severity: {data.expert_review.severity}
                    </span>
                  )}
                </div>
                <p className="text-base font-black text-slate-900">
                  Confirmed Diagnosis: {data.expert_review?.final_condition || data.expert_review?.expert_prediction || data.prediction?.predicted_class}
                </p>
                {(data.expert_review?.expert_notes || data.expert_review?.treatment_recommendation) && (
                  <div className="text-xs text-[#1B5E20] bg-white/80 p-3 rounded-lg border border-[#C8E6C9] space-y-1">
                    <span className="font-bold block">Agronomic Recommendation:</span>
                    <p className="text-slate-800">
                      {data.expert_review.treatment_recommendation || data.expert_review.expert_notes}
                    </p>
                  </div>
                )}
              </div>
            ) : isEscalated ? (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 sm:p-5 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
                    <Clock className="w-5 h-5 text-amber-600" />
                    <span>Queued for Cooperative Expert Inspection</span>
                  </div>
                  <span className="text-xs font-bold text-amber-800 bg-amber-100 px-2.5 py-0.5 rounded-full">
                    SLA &lt;6.0 Hours
                  </span>
                </div>
                <p className="text-xs text-amber-800">
                  This case has been routed to the priority specialist queue. An agronomist is inspecting leaf symptoms and will provide actionable management recommendations.
                </p>
                <div className="pt-2">
                  <button
                    onClick={() => onNavigate(`/farmer/reviews/${data.id}`)}
                    className="inline-flex items-center gap-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs px-4 py-2 rounded-xl transition-all shadow-xs"
                  >
                    Track Review Timeline
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
                <div className="space-y-0.5 text-center sm:text-left">
                  <span className="font-bold text-slate-800 block">Want human agronomist verification?</span>
                  <span className="text-slate-500">Request formal inspection from cooperative extension experts.</span>
                </div>
                <button
                  onClick={handleEscalate}
                  disabled={escalating}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold px-4 py-2.5 rounded-xl transition-all shadow-xs disabled:opacity-50"
                >
                  {escalating ? <Loader2 className="w-4 h-4 animate-spin" /> : <UserCheck className="w-4 h-4" />}
                  Request Expert Review
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

