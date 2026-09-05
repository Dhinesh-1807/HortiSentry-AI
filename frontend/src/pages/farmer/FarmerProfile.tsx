import React from 'react';
import { User, ShieldCheck, MapPin, Phone, Mail, Award, Clock, ArrowRight, PlusCircle } from 'lucide-react';
import { AuthUser } from '../../types';

interface FarmerProfileProps {
  user: AuthUser | null;
  onNavigate: (route: string) => void;
}

export const FarmerProfile: React.FC<FarmerProfileProps> = ({ user, onNavigate }) => {
  const farmerCode = user?.farmer_code || 'HS-FARMER-0001';
  const fullName = user?.full_name || user?.name || 'Horticulture Farmer';
  const email = user?.email || 'farmer@hortisentry.demo';
  const phone = user?.phone || '+91 98401 23456';
  const location = user?.location || 'Horticulture Cooperative Member';

  return (
    <div className="max-w-3xl mx-auto space-y-6 py-4">
      {/* Header Profile Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-[#E8F5E9] text-[#1B5E20] border border-[#C8E6C9] flex items-center justify-center font-bold text-2xl">
              {fullName.charAt(0)}
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-extrabold text-[#1F2937]">{fullName}</h1>
                <span className="bg-[#E8F5E9] text-[#1B5E20] border border-[#C8E6C9] text-xs font-bold px-2.5 py-0.5 rounded-full">
                  Verified Farmer
                </span>
              </div>
              <p className="text-xs font-mono font-bold text-[#2E7D32]">
                Cooperative ID: {farmerCode}
              </p>
            </div>
          </div>

          <button
            onClick={() => onNavigate('/farmer/observation/new')}
            className="bg-[#2E7D32] hover:bg-[#1B5E20] text-white text-xs sm:text-sm font-bold px-4 py-2.5 rounded-xl transition-all inline-flex items-center gap-2"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Observation</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-100">
          <div className="flex items-center gap-3 text-xs text-slate-600">
            <Mail className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <span className="truncate">{email}</span>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-600">
            <Phone className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <span>{phone}</span>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-600">
            <MapPin className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <span className="truncate">{location}</span>
          </div>
        </div>
      </div>

      {/* Privacy Guarantee */}
      <div className="bg-[#E8F5E9] border border-[#C8E6C9] rounded-xl p-5 space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold text-[#1B5E20] uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4 text-[#2E7D32]" />
          <span>Ethical & Non-Identifiable Cooperative Record</span>
        </div>
        <p className="text-xs text-[#1F2937]/80 leading-relaxed">
          Your farmer identifier ({farmerCode}) is strictly separated from agricultural diagnostic training datasets. Extension officers only receive anonymized crop condition telemetry, growth stage, and regional epidemiological signals.
        </p>
      </div>

      {/* Action links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          onClick={() => onNavigate('/farmer/observations')}
          className="p-5 bg-white rounded-xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="flex items-center justify-between text-[#1F2937] font-bold text-sm">
            <span>View All My Observations</span>
            <ArrowRight className="w-4 h-4 text-[#2E7D32]" />
          </div>
          <p className="text-xs text-slate-500">
            Check the history of your submitted crop observations, AI preliminary scores, and specialist review results.
          </p>
        </div>

        <div
          onClick={() => onNavigate('/how-it-works')}
          className="p-5 bg-white rounded-xl border border-slate-200 hover:border-[#2E7D32] transition-all cursor-pointer space-y-2 shadow-xs"
        >
          <div className="flex items-center justify-between text-[#1F2937] font-bold text-sm">
            <span>How HortiSentry Works</span>
            <ArrowRight className="w-4 h-4 text-[#2E7D32]" />
          </div>
          <p className="text-xs text-slate-500">
            Understand how our AI screening and agricultural expert escalation process protects your harvest.
          </p>
        </div>
      </div>
    </div>
  );
};
