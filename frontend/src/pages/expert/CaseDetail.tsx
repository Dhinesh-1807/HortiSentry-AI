import React, { useEffect, useState } from 'react';
import {
  ArrowLeft,
  Calendar,
  MapPin,
  FileText,
  Clock,
  ShieldAlert,
  Loader2,
  AlertTriangle,
  UserCheck,
  CheckCircle2
} from 'lucide-react';
import { getExpertReviewDetail, completeExpertReview, requestExpertInfo } from '../../services/api';
import { ExpertReviewDetail } from '../../types';
import { Badge } from '../../components/Badge';
import { Alert } from '../../components/Alert';
import { CaseImageViewer } from '../../components/expert/CaseImageViewer';
import { ExpertDecisionPanel } from '../../components/expert/ExpertDecisionPanel';
import { RequestInfoDialog } from '../../components/expert/RequestInfoDialog';

interface CaseDetailProps {
  reviewId: string;
  onNavigate: (route: string) => void;
}

export const CaseDetail: React.FC<CaseDetailProps> = ({ reviewId, onNavigate }) => {
  const [data, setData] = useState<ExpertReviewDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showRequestInfoModal, setShowRequestInfoModal] = useState<boolean>(false);

  const loadCase = async () => {
    setLoading(true);
    setError(null);
    try {
      const caseData = await getExpertReviewDetail(reviewId);
      setData(caseData);
    } catch (err: any) {
      console.error('Failed to load review case:', err);
      setError(err.message || 'Could not load review case detail.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (reviewId) loadCase();
  }, [reviewId]);

  const handleCompleteReview = async (payload: { expert_prediction: string; expert_notes?: string }) => {
    if (!reviewId) return;
    try {
      await completeExpertReview(reviewId, payload);
      await loadCase();
    } catch (err: any) {
      console.error('Error completing review:', err);
      alert(err.message || 'Failed to complete review.');
    }
  };

  const handleRequestInfoSubmit = async (note: string) => {
    if (!reviewId) return;
    try {
      await requestExpertInfo(reviewId, { info_note: note });
      await loadCase();
    } catch (err: any) {
      console.error('Error requesting info:', err);
      alert(err.message || 'Failed to submit request for info.');
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-3">
        <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-600">Loading Case Diagnostic Data...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center space-y-4 max-w-md mx-auto">
        <ShieldAlert className="w-10 h-10 text-rose-500 mx-auto" />
        <p className="font-bold text-slate-800">{error || 'Review case not found.'}</p>
        <button
          onClick={() => onNavigate('/expert/reviews')}
          className="bg-emerald-700 text-white font-semibold text-xs px-4 py-2 rounded-lg"
        >
          Return to Queue
        </button>
      </div>
    );
  }

  const confPct = data.ai_prediction?.confidence != null ? Math.round(data.ai_prediction.confidence * 100) : 0;
  const isLowConf = (data.ai_prediction?.confidence ?? 0) < 0.70;

  const symptomsList = Array.isArray(data.symptoms)
    ? data.symptoms
    : typeof data.symptoms === 'string'
      ? (() => {
          try {
            const p = JSON.parse(data.symptoms);
            return Array.isArray(p) ? p : [data.symptoms];
          } catch {
            return [data.symptoms];
          }
        })()
      : [];

  return (
    <div className="space-y-6">
      {/* Top Action Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => onNavigate('/expert/reviews')}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-slate-900 bg-white border border-slate-200 px-3.5 py-2 rounded-xl shadow-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Queue
        </button>
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-bold text-slate-500">Case ID: {data.observation_id?.substring(0, 8) || 'N/A'}</span>
          <Badge status={data.review_status} />
        </div>
      </div>

      {/* DEMO MODE Notice */}
      {data.ai_prediction?.is_demo_mode && (
        <Alert type="demo" title="DEMO MODE — OBSERVATION SYSTEM DEMONSTRATION">
          Prediction shown for demonstration purposes. Not a validated agricultural diagnosis. Real ML training will occur in Phase 7.
        </Alert>
      )}

      {/* Main Split Grid Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Image Viewer & Quality Diagnostics */}
        <div className="lg:col-span-6 space-y-4">
          <CaseImageViewer imageUrl={data.image_url} qualityAnalysis={data.quality_analysis} />

          {/* Turnaround Metric Box */}
          {data.turnaround_metrics && (
            <div className="bg-slate-900 text-slate-200 p-4 rounded-2xl border border-slate-800 text-xs space-y-1">
              <span className="font-bold text-emerald-400 uppercase tracking-wider block text-[10px]">
                Turnaround Metric (Completed Time - Symptom Observed)
              </span>
              <p className="font-mono font-bold text-white text-sm">
                Elapsed: {data.turnaround_metrics.formatted} ({data.turnaround_metrics.hours} Hours)
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Case Information & AI Breakdown */}
        <div className="lg:col-span-6 space-y-4">
          {/* Case Meta Box */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 space-y-4 shadow-sm">
            <div className="flex justify-between items-start border-b border-slate-100 pb-3">
              <div>
                <h2 className="text-xl font-black text-slate-900">{data.crop_display_name}</h2>
                <p className="text-xs text-slate-500 font-semibold">Growth Stage: {data.crop_stage}</p>
              </div>
              <div className="text-right">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Escalation Reason</span>
                <span className="text-xs font-bold text-amber-800 bg-amber-100 px-2.5 py-0.5 rounded-full inline-block mt-0.5">
                  {data.escalation_reason}
                </span>
              </div>
            </div>

            {/* Reported Symptoms */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">Farmer Symptoms</span>
              <div className="flex flex-wrap gap-1.5">
                {symptomsList.map((sym, idx) => (
                  <span key={idx} className="bg-slate-100 text-slate-800 px-2.5 py-1 rounded-lg text-xs font-semibold">
                    {sym}
                  </span>
                ))}
              </div>
            </div>

            {/* Regional Location & Notes */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-slate-100 text-xs">
              <div className="flex items-center gap-1.5 text-slate-600">
                <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                <span>Location: <strong className="text-slate-800">{data.location}</strong></span>
              </div>
              <div className="flex items-center gap-1.5 text-slate-600">
                <Clock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                <span>Submitted: {new Date(data.submitted_at).toLocaleString()}</span>
              </div>
            </div>

            {data.farmer_notes && (
              <div className="pt-2 border-t border-slate-100">
                <span className="text-[11px] font-semibold text-slate-400 block">Farmer Notes:</span>
                <p className="text-xs text-slate-700 italic bg-slate-50 p-2.5 rounded-xl border border-slate-200 mt-1">
                  "{data.farmer_notes}"
                </p>
              </div>
            )}
          </div>

          {/* AI Prediction Breakdown Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 space-y-4 shadow-sm">
            <div className="flex justify-between items-center pb-2 border-b border-slate-100">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-500">
                AI Inference Analysis
              </h3>
              <span className="text-xs font-mono font-bold text-slate-600">Model: tomato-v1</span>
            </div>

            <div className="flex items-center justify-between bg-emerald-50/70 p-3.5 rounded-xl border border-emerald-200">
              <div>
                <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">AI Top Prediction</span>
                <h4 className="text-lg font-black text-emerald-950">{data.ai_prediction.predicted_class}</h4>
              </div>
              <div className="text-right">
                <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">Confidence</span>
                <span className={`text-xl font-black ${isLowConf ? 'text-rose-600' : 'text-emerald-700'}`}>
                  {confPct}%
                </span>
              </div>
            </div>

            {/* Top Predictions List */}
            {data.ai_prediction.top_predictions && (
              <div className="space-y-1.5">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Probability Distribution</span>
                <div className="space-y-1 text-xs">
                  {data.ai_prediction.top_predictions.map((top, idx) => (
                    <div key={idx} className="flex justify-between items-center p-2 rounded-lg bg-slate-50 border border-slate-100">
                      <span className="font-semibold text-slate-800">{top.class}</span>
                      <span className="font-mono font-bold text-slate-600">{Math.round(top.confidence * 100)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Decision Section at Bottom */}
      <ExpertDecisionPanel
        aiPredictedClass={data.ai_prediction.predicted_class}
        availableClasses={[]}
        onCompleteReview={handleCompleteReview}
        onRequestInfoClick={() => setShowRequestInfoModal(true)}
        reviewStatus={data.review_status}
      />

      {/* Request Info Modal */}
      <RequestInfoDialog
        isOpen={showRequestInfoModal}
        onClose={() => setShowRequestInfoModal(false)}
        onSubmit={handleRequestInfoSubmit}
      />
    </div>
  );
};
