import React, { useState } from 'react';
import { CheckCircle2, Edit3, MessageSquare, Send, Loader2 } from 'lucide-react';
import { DiseaseClass } from '../../types';

interface ExpertDecisionPanelProps {
  aiPredictedClass: string;
  availableClasses: DiseaseClass[];
  onCompleteReview: (payload: { expert_prediction: string; expert_notes?: string }) => Promise<void>;
  onRequestInfoClick: () => void;
  reviewStatus: string;
}

export const ExpertDecisionPanel: React.FC<ExpertDecisionPanelProps> = ({
  aiPredictedClass,
  availableClasses,
  onCompleteReview,
  onRequestInfoClick,
  reviewStatus,
}) => {
  const [decisionMode, setDecisionMode] = useState<'validate' | 'correct'>('validate');
  const [selectedClass, setSelectedClass] = useState<string>(aiPredictedClass || 'Early Blight');
  const [notes, setNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);

  const defaultClasses = [
    { key: 'Healthy', display_name: 'Healthy' },
    { key: 'Early Blight', display_name: 'Early Blight' },
    { key: 'Late Blight', display_name: 'Late Blight' },
    { key: 'Leaf Spot', display_name: 'Leaf Spot' },
  ];

  const classOptions = availableClasses && availableClasses.length > 0
    ? availableClasses
    : defaultClasses;

  const handleValidateClick = () => {
    setDecisionMode('validate');
    setSelectedClass(aiPredictedClass);
  };

  const handleCorrectClick = () => {
    setDecisionMode('correct');
    // Default to first non-AI class if available, or Healthy
    const firstOther = classOptions.find((c) => c.display_name !== aiPredictedClass) || classOptions[0];
    setSelectedClass(firstOther.display_name);
  };

  const handleFormSubmit = async () => {
    setSubmitting(true);
    try {
      const finalPrediction = decisionMode === 'validate' ? aiPredictedClass : selectedClass;
      await onCompleteReview({
        expert_prediction: finalPrediction,
        expert_notes: notes,
      });
      setShowConfirmModal(false);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (reviewStatus === 'COMPLETED') {
    return (
      <div className="bg-emerald-50 border border-emerald-300 rounded-2xl p-5 text-center space-y-2">
        <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
        <h3 className="font-extrabold text-emerald-950 text-base">Expert Review Completed</h3>
        <p className="text-xs text-emerald-800">
          Ground-truth diagnosis recorded and preserved in database.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 space-y-5 shadow-sm">
      <div>
        <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-900">
          Expert Diagnostic Decision
        </h3>
        <p className="text-xs text-slate-500 mt-0.5">
          Select expert assessment to confirm or correct AI observation.
        </p>
      </div>

      {/* Mode Switcher */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        <button
          type="button"
          onClick={handleValidateClick}
          className={`p-3 rounded-xl border text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            decisionMode === 'validate'
              ? 'border-emerald-600 bg-emerald-50 text-emerald-900 ring-2 ring-emerald-600/20'
              : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-emerald-300'
          }`}
        >
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          Validate AI ({aiPredictedClass})
        </button>

        <button
          type="button"
          onClick={handleCorrectClick}
          className={`p-3 rounded-xl border text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            decisionMode === 'correct'
              ? 'border-amber-600 bg-amber-50 text-amber-900 ring-2 ring-amber-600/20'
              : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-amber-300'
          }`}
        >
          <Edit3 className="w-4 h-4 text-amber-600" />
          Correct AI Prediction
        </button>

        <button
          type="button"
          onClick={onRequestInfoClick}
          className="p-3 rounded-xl border border-slate-200 bg-slate-50 text-purple-800 hover:border-purple-300 text-xs font-bold transition-all flex items-center justify-center gap-2"
        >
          <MessageSquare className="w-4 h-4 text-purple-600" />
          Request Info
        </button>
      </div>

      {/* Correction Selection Dropdown */}
      {decisionMode === 'correct' && (
        <div className="bg-amber-50/70 p-4 rounded-xl border border-amber-200 space-y-2">
          <label className="block text-xs font-bold text-amber-950">
            Select Expert Ground-Truth Classification *
          </label>
          <select
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-amber-300 text-sm font-semibold bg-white text-slate-900 focus:ring-2 focus:ring-amber-500"
          >
            {classOptions.map((cls) => (
              <option key={cls.display_name} value={cls.display_name}>
                {cls.display_name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Expert Advisory Notes */}
      <div className="space-y-1">
        <label className="block text-xs font-semibold text-slate-700">
          Expert Advisory Notes & Reasoning (Optional)
        </label>
        <textarea
          rows={3}
          placeholder="Add clinical observations, pathological reasoning, or protective guidance..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500"
        />
      </div>

      {/* Submit Action */}
      <div className="pt-2">
        <button
          type="button"
          onClick={() => setShowConfirmModal(true)}
          className="w-full inline-flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold text-sm px-6 py-3 rounded-xl transition-all shadow-md active:scale-[0.98]"
        >
          <Send className="w-4 h-4" />
          Review & Complete Diagnosis
        </button>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-200">
            <h4 className="text-lg font-black text-slate-900">Confirm Expert Review</h4>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs space-y-2">
              <div>
                <span className="text-slate-500 font-semibold">AI Original Prediction: </span>
                <span className="font-bold text-slate-800">{aiPredictedClass}</span>
              </div>
              <div>
                <span className="text-slate-500 font-semibold">Expert Classification: </span>
                <span className="font-extrabold text-emerald-800">
                  {decisionMode === 'validate' ? aiPredictedClass : selectedClass}
                </span>
              </div>
              {notes && (
                <div>
                  <span className="text-slate-500 font-semibold">Notes: </span>
                  <span className="text-slate-700 italic">"{notes}"</span>
                </div>
              )}
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowConfirmModal(false)}
                disabled={submitting}
                className="flex-1 py-2.5 rounded-xl border border-slate-300 font-bold text-xs text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleFormSubmit}
                disabled={submitting}
                className="flex-1 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs inline-flex items-center justify-center gap-1.5"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Confirm & Complete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
