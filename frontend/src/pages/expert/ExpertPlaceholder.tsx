import React from 'react';
import { UserCheck, ShieldAlert, FileText, CheckCircle } from 'lucide-react';

export const ExpertPlaceholder: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="bg-slate-800 p-3 rounded-2xl text-emerald-400">
            <UserCheck className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-slate-900">Expert / Cooperative Reviewer Portal</h1>
            <p className="text-xs text-slate-500">Review low-confidence AI observations and validate ground-truth diagnoses</p>
          </div>
        </div>
        <span className="bg-slate-800 text-slate-200 border border-slate-700 text-xs px-3 py-1 rounded-full font-medium">
          Phase 2 Shell Initialized
        </span>
      </div>

      {/* KPI Card Placeholders */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-medium block">Total Submissions</span>
          <span className="text-2xl font-black text-slate-800 mt-1 block">0</span>
          <span className="text-[10px] text-slate-400">Database connected</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-medium block">Pending Reviews</span>
          <span className="text-2xl font-black text-amber-600 mt-1 block">0</span>
          <span className="text-[10px] text-amber-600/80">Queue ready</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-medium block">Low Confidence</span>
          <span className="text-2xl font-black text-red-600 mt-1 block">0</span>
          <span className="text-[10px] text-slate-400">Confidence &lt; 0.70</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-medium block">Completed Reviews</span>
          <span className="text-2xl font-black text-emerald-600 mt-1 block">0</span>
          <span className="text-[10px] text-slate-400">Ground truth logged</span>
        </div>
      </div>

      {/* Queue Shell Notice */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm text-center py-10 space-y-3">
        <FileText className="h-10 w-10 text-slate-400 mx-auto" />
        <h3 className="text-base font-bold text-slate-800">Expert Review Queue Engine Ready</h3>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          The expert decision portal will list pending cases requiring ground-truth validation, symptom inspection, and advisory guidance. Full queue and review workflows will be activated in Phase 5.
        </p>
      </div>
    </div>
  );
};
