import React, { useState } from 'react';
import { X, MessageSquare, Loader2 } from 'lucide-react';

interface RequestInfoDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (note: string) => Promise<void>;
}

export const RequestInfoDialog: React.FC<RequestInfoDialogProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [note, setNote] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!note.trim()) return;

    setSubmitting(true);
    try {
      await onSubmit(note);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-purple-900 font-bold">
            <MessageSquare className="w-5 h-5 text-purple-600" />
            <span>Request Additional Information</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-slate-500">
          Specify what additional crop photo, symptom details, or notes are required from the farmer to resolve this case.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Information Requested *
            </label>
            <textarea
              rows={4}
              required
              placeholder="e.g. Please upload a clearer photo of the underside of the affected leaf showing vein patterns..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="flex-1 py-2.5 rounded-xl border border-slate-300 font-bold text-xs text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !note.trim()}
              className="flex-1 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-800 disabled:opacity-50 text-white font-bold text-xs inline-flex items-center justify-center gap-1.5"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Send Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
