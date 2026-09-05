import React from 'react';
import { UserCheck, ShieldCheck, Award, Clock, CheckCircle2, BookOpen, ArrowRight } from 'lucide-react';
import { AuthUser } from '../../types';

interface ExpertProfileProps {
  user: AuthUser | null;
  onNavigate: (route: string) => void;
}

export const ExpertProfile: React.FC<ExpertProfileProps> = ({ user, onNavigate }) => {
  const fullName = user?.full_name || 'Dr. K. Arulraj';
  const email = user?.email || 'expert@hortisentry.demo';
  const role = 'Horticulture Pathologist & Review Officer';
  const location = user?.location || 'Regional Agricultural Research Station';

  return (
    <div className="max-w-3xl mx-auto space-y-6 py-4">
      {/* Profile Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-700 border border-indigo-200 flex items-center justify-center font-bold text-2xl">
              {fullName.charAt(0)}
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-extrabold text-[#1F2937]">{fullName}</h1>
                <span className="bg-indigo-100 text-indigo-800 border border-indigo-200 text-xs font-bold px-2.5 py-0.5 rounded-full">
                  Agronomic Reviewer
                </span>
              </div>
              <p className="text-xs font-medium text-slate-500">{role}</p>
              <p className="text-xs text-slate-400">{location} • {email}</p>
            </div>
          </div>

          <button
            onClick={() => onNavigate('/expert/queue')}
            className="bg-[#2E7D32] hover:bg-[#1B5E20] text-white text-xs sm:text-sm font-bold px-4 py-2.5 rounded-xl transition-all shadow-xs inline-flex items-center gap-2"
          >
            <UserCheck className="w-4 h-4" />
            <span>Open Triage Queue</span>
          </button>
        </div>

        {/* Quality Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-100">
          <div className="bg-[#F8FAF8] p-4 rounded-xl border border-slate-200/80 space-y-1">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-bold uppercase tracking-wider">Median Turnaround</span>
              <Clock className="w-4 h-4 text-[#2E7D32]" />
            </div>
            <div className="text-2xl font-extrabold text-[#1B5E20]">4.2h</div>
            <p className="text-[11px] text-slate-500">Well within 6.0h SLA</p>
          </div>

          <div className="bg-[#F8FAF8] p-4 rounded-xl border border-slate-200/80 space-y-1">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-bold uppercase tracking-wider">Cases Evaluated</span>
              <CheckCircle2 className="w-4 h-4 text-indigo-600" />
            </div>
            <div className="text-2xl font-extrabold text-indigo-700">142</div>
            <p className="text-[11px] text-slate-500">Verified diagnoses</p>
          </div>

          <div className="bg-[#F8FAF8] p-4 rounded-xl border border-slate-200/80 space-y-1">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-bold uppercase tracking-wider">AI Agreement</span>
              <Award className="w-4 h-4 text-amber-500" />
            </div>
            <div className="text-2xl font-extrabold text-amber-700">88.4%</div>
            <p className="text-[11px] text-slate-500">Consensus match rate</p>
          </div>
        </div>
      </div>

      {/* Review Guidelines & Protocols */}
      <div className="bg-[#E8F5E9] border border-[#C8E6C9] rounded-2xl p-6 space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold text-[#1B5E20] uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4 text-[#2E7D32]" />
          <span>Cooperative Review & Dual-Audit Protocol</span>
        </div>
        <p className="text-xs sm:text-sm text-[#1F2937]/90 leading-relaxed">
          As an agricultural reviewer, your decisions directly protect smallholder livelihoods. When evaluating cases, both the original AI prediction and your specialist override are permanently archived to maintain institutional learning and error auditing.
        </p>
      </div>

      {/* Action links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          onClick={() => onNavigate('/expert/queue')}
          className="p-5 bg-white rounded-xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="flex items-center justify-between text-[#1F2937] font-bold text-sm">
            <span>Escalation Review Queue</span>
            <ArrowRight className="w-4 h-4 text-[#2E7D32]" />
          </div>
          <p className="text-xs text-slate-500">
            View pending cases sorted by risk level, image blur scores, and farmer second opinion requests.
          </p>
        </div>

        <div
          onClick={() => onNavigate('/expert/history')}
          className="p-5 bg-white rounded-xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="flex items-center justify-between text-[#1F2937] font-bold text-sm">
            <span>Past Review Records</span>
            <ArrowRight className="w-4 h-4 text-[#2E7D32]" />
          </div>
          <p className="text-xs text-slate-500">
            Browse completed reviews, treatment recommendations, and follow-up schedules.
          </p>
        </div>
      </div>
    </div>
  );
};
