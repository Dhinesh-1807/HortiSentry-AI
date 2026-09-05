import React from 'react';
import { ShieldCheck, Target, HeartHandshake, Eye, AlertCircle, Cpu, Award } from 'lucide-react';

interface AboutPageProps {
  onNavigate: (route: string) => void;
}

export const AboutPage: React.FC<AboutPageProps> = ({ onNavigate }) => {
  return (
    <div className="max-w-4xl mx-auto space-y-12 py-6">
      {/* Header Banner */}
      <div className="bg-white rounded-3xl border border-[#C8E6C9] p-8 sm:p-12 shadow-sm relative overflow-hidden">
        <div className="max-w-2xl space-y-4">
          <span className="inline-flex items-center gap-2 bg-[#E8F5E9] text-[#1B5E20] px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
            <Target className="w-4 h-4 text-[#2E7D32]" />
            About HortiSentry
          </span>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-[#1F2937] tracking-tight">
            Bridging Smallholders and Agronomic Science
          </h1>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
            HortiSentry is a software-only, AI-assisted observation and escalation platform engineered for horticulture cooperatives. We empower farmers to capture visual records early and bridge uncertain cases directly to agricultural experts.
          </p>
        </div>
      </div>

      {/* The Cooperative Problem & Mission */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 space-y-4 shadow-sm">
          <div className="w-12 h-12 bg-amber-50 text-amber-700 rounded-xl flex items-center justify-center font-bold">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-[#1F2937]">The Cooperative Challenge</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            Horticultural crops—such as tomatoes, chilies, eggplants, and peppers—are highly vulnerable to fast-spreading fungal, bacterial, and viral pathogens. In rural cooperative networks, farmers often report symptoms days late via fragmented phone calls or verbal messages, lacking visual records.
          </p>
          <p className="text-sm text-slate-600 leading-relaxed">
            Cooperative agricultural extension officers typically face overwhelming backlogs, resulting in a baseline time-to-expert review of 48+ hours. During this delay, crop damage escalates and pesticide misuse risks increase.
          </p>
        </div>

        <div className="bg-white rounded-2xl border border-[#C8E6C9] p-6 sm:p-8 space-y-4 shadow-sm">
          <div className="w-12 h-12 bg-[#E8F5E9] text-[#1B5E20] rounded-xl flex items-center justify-center font-bold">
            <HeartHandshake className="w-6 h-6 text-[#2E7D32]" />
          </div>
          <h2 className="text-xl font-bold text-[#1F2937]">Our Mission & Approach</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            HortiSentry equips farmers with an easy-to-use mobile-first progressive web workflow to document leaf symptoms, select crop stages, and receive immediate AI preliminary screening powered by lightweight computer vision (MobileNetV3).
          </p>
          <p className="text-sm text-slate-600 leading-relaxed">
            Crucially, HortiSentry never isolates the human expert. An intelligent rule-based escalation engine automatically flags ambiguous observations, low-quality photos, or high-risk diseases, routing them to the expert queue and slashing turnaround from 48 hours to under 6 hours.
          </p>
        </div>
      </div>

      {/* Responsible AI & Dataset Ethics */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-[#E8F5E9] text-[#1B5E20]">
            <ShieldCheck className="w-6 h-6 text-[#2E7D32]" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-[#1F2937]">Responsible AI & Dataset Ethics</h2>
            <p className="text-xs text-slate-500">Adhering to strict agricultural ethics and privacy standards</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
          <div className="bg-[#F8FAF8] rounded-xl p-4 border border-slate-200/80 space-y-2">
            <h3 className="text-sm font-bold text-[#1F2937]">Non-Identifiable Metadata</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Observation and training metadata contain zero personally identifiable farmer records. Only administrative regions, crop varieties, and anonymous identifiers are retained in accordance with cooperative governance.
            </p>
          </div>

          <div className="bg-[#F8FAF8] rounded-xl p-4 border border-slate-200/80 space-y-2">
            <h3 className="text-sm font-bold text-[#1F2937]">Transparent Uncertainty</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              The model communicates confidence bounds and image quality ratings. Low-confidence outputs (&lt;60%) or blurred images are marked for triage rather than producing misleading diagnoses.
            </p>
          </div>

          <div className="bg-[#F8FAF8] rounded-xl p-4 border border-slate-200/80 space-y-2">
            <h3 className="text-sm font-bold text-[#1F2937]">Strict Decision Support</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              HortiSentry acts purely as an assistive observation filter. High-risk actions and treatment protocols remain under cooperative agricultural extension officer oversight.
            </p>
          </div>
        </div>
      </div>

      {/* Software Architecture Highlights */}
      <div className="bg-[#E8F5E9] border border-[#C8E6C9] rounded-2xl p-6 sm:p-8 space-y-4">
        <div className="flex items-center gap-3">
          <Cpu className="w-6 h-6 text-[#1B5E20]" />
          <h2 className="text-lg font-bold text-[#1B5E20]">Software-Only Architecture</h2>
        </div>
        <p className="text-xs sm:text-sm text-[#1F2937] leading-relaxed">
          HortiSentry is strictly a software solution running in modern web browsers and Python FastAPI backend. It requires no physical sensors, IoT devices, microcontrollers, drones, or proprietary hardware. Farmers access the platform using existing smartphones.
        </p>
        <div className="pt-2 flex flex-wrap gap-4">
          <button
            onClick={() => onNavigate('/how-it-works')}
            className="bg-[#2E7D32] hover:bg-[#1B5E20] text-white font-bold text-xs sm:text-sm px-5 py-2.5 rounded-xl transition-all shadow-sm"
          >
            See How the Workflow Operates
          </button>
          <button
            onClick={() => onNavigate('/farmer/observation/new')}
            className="bg-white hover:bg-slate-50 text-[#1B5E20] font-bold text-xs sm:text-sm px-5 py-2.5 rounded-xl border border-[#C8E6C9] transition-all"
          >
            Try Leaf Observation
          </button>
        </div>
      </div>
    </div>
  );
};
