import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  FileText,
  ExternalLink,
  BookOpen,
  CheckCircle2,
  HelpCircle,
  ChevronLeft,
  Loader2,
  UserCheck
} from 'lucide-react';
import { getAIReview, requestExpertReview } from '../../services/api';
import { Alert } from '../../components/Alert';

interface AIReviewDetailProps {
  observationId: string;
  onNavigate: (route: string) => void;
}

export const AIReviewDetail: React.FC<AIReviewDetailProps> = ({ observationId, onNavigate }) => {
  const [review, setReview] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [escalating, setEscalating] = useState<boolean>(false);
  const [escalated, setEscalated] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    const fetchReview = async () => {
      setLoading(true);
      try {
        const data = await getAIReview(observationId);
        if (isMounted) setReview(data);
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load AI Evidence Review.');
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    fetchReview();
    return () => { isMounted = false; };
  }, [observationId]);

  const handleRequestExpert = async () => {
    setEscalating(true);
    try {
      await requestExpertReview(observationId, 'Farmer requested manual expert verification.');
      setEscalated(true);
    } catch (err: any) {
      alert('Could not submit expert escalation request: ' + err.message);
    } finally {
      setEscalating(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto py-16 text-center space-y-4">
        <Loader2 className="w-10 h-10 text-emerald-700 animate-spin mx-auto" />
        <h2 className="text-lg font-bold text-slate-800">Generating AI Evidence Review...</h2>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          Retrieving authoritative agricultural guidance from ICAR, TNAU, and FAO databases.
        </p>
      </div>
    );
  }

  if (error || !review) {
    return (
      <div className="max-w-2xl mx-auto space-y-4 py-8">
        <Alert type="danger" title="Review Error">
          {error || 'Unable to retrieve AI review.'}
        </Alert>
        <button
          onClick={() => onNavigate('/farmer/history')}
          className="text-xs font-bold text-slate-700 hover:text-slate-900 inline-flex items-center gap-1"
        >
          <ChevronLeft className="w-4 h-4" /> Back to History
        </button>
      </div>
    );
  }

  const isLowConf = review.overall_confidence < 0.70;

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-12">
      {/* Header Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => onNavigate('/farmer/history')}
          className="text-xs font-semibold text-slate-600 hover:text-slate-900 inline-flex items-center gap-1"
        >
          <ChevronLeft className="w-4 h-4" /> Back to Observations
        </button>
        <span className="text-[11px] font-mono bg-slate-100 text-slate-600 px-2.5 py-1 rounded-md border border-slate-200">
          ID: {observationId.substring(0, 8)}...
        </span>
      </div>

      {/* Responsible AI Notice Banner */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 flex items-start gap-3 text-xs text-amber-900">
        <ShieldCheck className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">AI Decision Support Notice: </span>
          This AI review evaluates visual symptoms against verified agricultural literature for farmer decision support. It is not an official diagnostic certificate.
        </div>
      </div>

      {/* Primary Candidate Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-5">
          <div>
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              {review.crop_key ? review.crop_key.toUpperCase() : 'CROP'} OBSERVATION RESULT
            </div>
            <h1 className="text-2xl font-extrabold text-slate-900 mt-1">
              {review.primary_candidate}
            </h1>
            <p className="text-xs text-emerald-800 font-semibold mt-1">
              Visually consistent with observed foliage symptoms
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1.5 border border-emerald-200">
              <span>Overall Conf:</span>
              <span className="text-sm font-extrabold">{Math.round(review.overall_confidence * 100)}%</span>
            </span>
          </div>
        </div>

        {/* Confidence Breakdown Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50/80 p-3.5 rounded-xl border border-slate-200 text-xs">
          <div>
            <span className="text-slate-500 block text-[11px]">Vision Confidence</span>
            <span className="font-bold text-slate-900 text-sm">{Math.round(review.vision_confidence * 100)}%</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">Evidence Match</span>
            <span className="font-bold text-slate-900 text-sm">{Math.round(review.evidence_confidence * 100)}%</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">Severity Estimate</span>
            <span className={`font-bold uppercase text-xs ${review.severity_estimate === 'high' ? 'text-red-700' : 'text-amber-700'}`}>
              {review.severity_estimate}
            </span>
          </div>
        </div>

        {/* Evidence Mixed Warning Banner */}
        {review.evidence_is_mixed && (
          <div className="bg-amber-50 border border-amber-300 rounded-xl p-4 space-y-1">
            <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
              <AlertTriangle className="w-4 h-4 text-amber-700" />
              Evidence is Mixed
            </div>
            <p className="text-xs text-amber-800 leading-relaxed">
              {review.conflict_notes || 'Multiple trusted sources indicate overlapping symptom characteristics. Human expert review is recommended.'}
            </p>
          </div>
        )}

        {/* Summary Description */}
        <div>
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Observation Summary</h3>
          <p className="text-sm text-slate-800 leading-relaxed">{review.observation_summary}</p>
        </div>
      </div>

      {/* Recommended Immediate Actions (IPM-Focused) */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-700" />
          Recommended Field Actions (IPM Guidance)
        </h2>
        <div className="space-y-2.5">
          {review.recommended_immediate_actions?.map((act: string, idx: number) => (
            <div key={idx} className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs text-slate-800 flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[11px] flex items-center justify-center flex-shrink-0">
                {idx + 1}
              </span>
              <span className="leading-relaxed">{act}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Prevention & Monitoring */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-emerald-700" />
          Prevention & Seasonal Monitoring
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
            <h3 className="text-xs font-bold text-slate-800">Long-term Prevention</h3>
            <ul className="text-xs text-slate-600 space-y-1.5 list-disc pl-4">
              {review.prevention_monitoring?.map((item: string, idx: number) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
            <h3 className="text-xs font-bold text-slate-800">What to Watch Next</h3>
            <ul className="text-xs text-slate-600 space-y-1.5 list-disc pl-4">
              {review.what_to_watch_next?.map((item: string, idx: number) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Cited Agricultural Sources (Source Cards) */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-emerald-700" />
            Verified Agricultural Sources Used ({review.sources?.length || 0})
          </h2>
        </div>

        <div className="space-y-3">
          {review.sources?.map((src: any) => (
            <div key={src.id || src.url} className="border border-slate-200 rounded-xl p-3.5 bg-slate-50/50 hover:bg-slate-50 transition-colors space-y-2">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-xs sm:text-sm">{src.source_name}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${src.authority_tier === 1 ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'}`}>
                      Tier {src.authority_tier}
                    </span>
                  </div>
                  <h4 className="text-xs font-semibold text-slate-700 mt-1">{src.title}</h4>
                </div>
                <a
                  href={src.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-bold text-emerald-700 hover:text-emerald-900 inline-flex items-center gap-1 bg-white border border-slate-200 px-2.5 py-1 rounded-lg flex-shrink-0 shadow-2xs"
                >
                  View Source <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <p className="text-xs text-slate-600 italic line-clamp-2 leading-relaxed bg-white p-2.5 rounded-lg border border-slate-100">
                "{src.evidence_text}"
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Expert Verification Escalation Footer */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 space-y-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-md">
        <div>
          <h3 className="font-bold text-base flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-emerald-400" />
            Human Expert Verification Available
          </h3>
          <p className="text-xs text-slate-300 mt-1 max-w-lg">
            If you need second-opinion confirmation from an agricultural extension officer, submit this case to the Expert Review Queue.
          </p>
        </div>

        {escalated ? (
          <span className="bg-emerald-600 text-white text-xs font-bold px-4 py-2.5 rounded-xl inline-flex items-center gap-1.5 flex-shrink-0">
            <CheckCircle2 className="w-4 h-4" /> Requested Expert Review
          </span>
        ) : (
          <button
            onClick={handleRequestExpert}
            disabled={escalating}
            className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-xs px-5 py-2.5 rounded-xl transition-all shadow-sm flex-shrink-0"
          >
            {escalating ? 'Submitting Request...' : 'Request Expert Review'}
          </button>
        )}
      </div>
    </div>
  );
};
