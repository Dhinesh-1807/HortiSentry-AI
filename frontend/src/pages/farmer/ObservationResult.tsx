import React, { useEffect, useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  UserCheck,
  ArrowLeft,
  ShieldAlert,
  Loader2,
  Activity,
  Award
} from 'lucide-react';
import { fetchObservationDetail, escalateObservation } from '../../services/api';
import { ObservationDetail } from '../../types';
import { Badge } from '../../components/Badge';
import { Alert } from '../../components/Alert';

interface ObservationResultProps {
  observationId: string;
  onNavigate: (route: string) => void;
}

export const ObservationResult: React.FC<ObservationResultProps> = ({ observationId, onNavigate }) => {
  const [data, setData] = useState<ObservationDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Manual Escalation State
  const [escalating, setEscalating] = useState<boolean>(false);
  const [escalationMsg, setEscalationMsg] = useState<string | null>(null);

  const loadDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const obs = await fetchObservationDetail(observationId);
      setData(obs);
    } catch (err: any) {
      console.error('Error fetching observation result:', err);
      setError(err.message || 'Failed to load observation result.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (observationId) {
      loadDetail();
    }
  }, [observationId]);

  const handleManualEscalate = async () => {
    if (!observationId) return;
    setEscalating(true);
    try {
      await escalateObservation(observationId, 'Farmer requested expert review from result screen');
      setEscalationMsg('Your observation has been submitted for expert review.');
      await loadDetail();
    } catch (err: any) {
      console.error('Escalation error:', err);
      alert(err.message || 'Failed to request expert review.');
    } finally {
      setEscalating(false);
    }
  };

  if (loading) {
    return (
      <div className="py-16 text-center space-y-3">
        <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-600">Retrieving AI Observation Result...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-md mx-auto bg-white p-6 rounded-2xl border border-slate-200 text-center space-y-4">
        <ShieldAlert className="w-10 h-10 text-rose-500 mx-auto" />
        <p className="font-bold text-slate-800">{error || 'Observation not found.'}</p>
        <button
          onClick={() => onNavigate('/farmer/observations')}
          className="bg-emerald-700 text-white font-semibold text-xs px-4 py-2 rounded-lg"
        >
          Return to History
        </button>
      </div>
    );
  }

  const confidencePct = data.prediction?.confidence != null
    ? Math.round(data.prediction.confidence * 100)
    : (data.confidence != null ? Math.round(data.confidence * 100) : 0);
  const isHighConfidence = (data.prediction?.confidence ?? data.confidence ?? 0) >= 0.70;

  const topPredictionsList = Array.isArray(data.prediction?.top_predictions)
    ? data.prediction.top_predictions
    : typeof data.prediction?.top_predictions === 'string'
      ? (() => {
          try {
            const p = JSON.parse(data.prediction.top_predictions);
            return Array.isArray(p) ? p : [];
          } catch {
            return [];
          }
        })()
      : [];

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      {/* Header Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => onNavigate('/farmer/observations')}
          className="inline-flex items-center gap-1 text-xs font-bold text-slate-600 hover:text-slate-900 bg-white border border-slate-200 px-3 py-1.5 rounded-lg"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to History
        </button>
        <span className="text-xs font-semibold text-slate-400">ID: {data.id.substring(0, 8)}</span>
      </div>

      {/* DEMO MODE Banner */}
      {data.prediction?.is_demo_mode && (
        <Alert type="demo" title="DEMO MODE ACTIVE">
          This prediction is provided for demonstration purposes and is not a validated agricultural diagnosis. Real ML training will take place in Phase 7.
        </Alert>
      )}

      {/* Main AI Result Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 sm:p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-black text-slate-900">
                {data.prediction?.predicted_class || data.predicted_class || 'Screening Complete'}
              </h1>
              <Badge status={data.status} />
            </div>
            <p className="text-xs text-slate-500 mt-0.5">Target Crop: <span className="font-bold text-slate-700">{data.crop_display_name}</span> ({data.crop_stage})</p>
          </div>
          <div className="text-left sm:text-right bg-emerald-50 px-4 py-2 rounded-xl border border-emerald-200">
            <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">AI Confidence Score</span>
            <span className="text-2xl font-black text-emerald-700">{confidencePct}%</span>
          </div>
        </div>

        {/* Confidence Interpretation Indicator */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-semibold text-slate-700">
            <span>Confidence Indicator</span>
            <span>{isHighConfidence ? 'Above Review Threshold' : 'Low Confidence / Uncertain'}</span>
          </div>
          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
            <div
              className={`h-2.5 rounded-full ${isHighConfidence ? 'bg-emerald-600' : 'bg-amber-500'}`}
              style={{ width: `${confidencePct}%` }}
            />
          </div>
          <p className="text-xs text-slate-500 pt-0.5">
            {isHighConfidence
              ? 'AI confidence is above the prototype review threshold.'
              : 'The AI is uncertain about this observation. Expert review recommended.'}
          </p>
        </div>

        {/* Image Quality Summary */}
        <div className="p-3.5 rounded-xl border bg-slate-50 border-slate-200 text-xs space-y-1">
          <div className="flex justify-between items-center">
            <span className="font-bold text-slate-800">Image Quality Rating:</span>
            {data.image?.is_blur_detected || (data.image as any)?.is_exposure_issue ? (
              <span className="text-amber-800 font-bold bg-amber-100 px-2 py-0.5 rounded">Needs Attention</span>
            ) : (
              <span className="text-emerald-800 font-bold bg-emerald-100 px-2 py-0.5 rounded">Good Quality</span>
            )}
          </div>
          {(data.image?.is_blur_detected || (data.image as any)?.is_exposure_issue) && (
            <p className="text-amber-800 text-[11px] mt-1">
              Image blur or lighting exposure may affect AI reliability. Try taking photos in good lighting with clear leaf visibility.
            </p>
          )}
        </div>

        {/* Top Predictions Breakdown */}
        {topPredictionsList.length > 0 && (
          <div className="space-y-2 pt-1">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Top Alternative Class Probabilities</h3>
            <div className="space-y-1.5">
              {topPredictionsList.map((top, idx) => (
                <div key={idx} className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-50/70 border border-slate-100">
                  <span className="font-semibold text-slate-800">{top.class}</span>
                  <span className="font-mono font-bold text-slate-600">{Math.round(top.confidence * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Responsible AI Disclaimer */}
        <Alert type="info" title="Responsible AI Field Notice">
          This is an AI-assisted observation, not a guaranteed diagnosis. For uncertain cases, please seek expert review.
        </Alert>

        {/* Expert Escalation UI */}
        <div className="pt-3 border-t border-slate-100 space-y-3">
          {escalationMsg && (
            <Alert type="success" title="Escalation Request Sent">
              {escalationMsg}
            </Alert>
          )}

          {data.escalation.is_escalated ? (
            <div className="bg-amber-50/80 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
              <UserCheck className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
              <div className="text-xs space-y-1">
                <h4 className="font-bold text-amber-950">Expert Review Status: {data.escalation.status}</h4>
                <p className="text-amber-900">
                  Reason: <span className="font-semibold">{data.escalation.reason}</span>. An agricultural expert will review this case.
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div className="text-xs text-slate-600">
                <p className="font-bold text-slate-900">Want expert confirmation?</p>
                <p>Request human agricultural expert review at any time.</p>
              </div>
              <button
                onClick={handleManualEscalate}
                disabled={escalating}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs px-4 py-2.5 rounded-xl transition-all shadow-sm flex-shrink-0"
              >
                {escalating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <UserCheck className="w-4 h-4" />}
                Request Expert Review
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
