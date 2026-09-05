import React from 'react';
import {
  ShieldCheck,
  Sprout,
  ArrowRight,
  Clock,
  CheckCircle2,
  Users,
  Search,
  Activity,
  AlertTriangle,
  Lock,
  ChevronRight,
  BookOpen
} from 'lucide-react';
import { HealthStatus, CropConfig } from '../../types';

interface LandingPageProps {
  health: HealthStatus | null;
  crops: CropConfig[];
  onNavigate: (route: string) => void;
  onQuickLogin?: (role: 'farmer' | 'expert' | 'admin') => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  health,
  crops,
  onNavigate
}) => {
  return (
    <div className="space-y-16 py-4">
      {/* 1. HERO SECTION (Section 32) */}
      <section className="bg-gradient-to-br from-[#1B5E20] via-[#2E7D32] to-[#144A18] text-white rounded-3xl p-8 sm:p-14 shadow-xl relative overflow-hidden">
        <div className="max-w-3xl space-y-6 relative z-10">
          <div className="inline-flex items-center gap-2 bg-[#E8F5E9]/20 text-[#E8F5E9] border border-[#E8F5E9]/30 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase">
            <ShieldCheck className="w-4 h-4" />
            <span>AI-Assisted Crop Disease Observation & Escalation Platform</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            HortiSentry
          </h1>

          <p className="text-xl sm:text-2xl font-medium text-emerald-100">
            Early crop disease observation. Faster expert support.
          </p>

          <p className="text-emerald-100/90 text-sm sm:text-base leading-relaxed max-w-2xl">
            An AI-assisted platform helping horticulture farmers record symptoms early, analyze crop images, and connect uncertain cases with agricultural experts.
          </p>

          <div className="flex flex-wrap gap-4 pt-2">
            <button
              onClick={() => onNavigate('/farmer/observation/new')}
              className="bg-white text-[#1B5E20] hover:bg-[#E8F5E9] font-bold px-6 py-3.5 rounded-xl shadow-lg transition-all flex items-center gap-2 text-sm sm:text-base"
            >
              <Sprout className="w-5 h-5 text-[#2E7D32]" />
              <span>Report a Crop Symptom</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>

            <button
              onClick={() => onNavigate('/how-it-works')}
              className="bg-[#1B5E20]/50 hover:bg-[#1B5E20]/80 text-white border border-emerald-300/40 font-semibold px-5 py-3.5 rounded-xl transition-all flex items-center gap-2 text-sm sm:text-base"
            >
              <BookOpen className="w-4 h-4" />
              <span>Explore How It Works</span>
            </button>
          </div>
        </div>
      </section>

      {/* 2. PROBLEM & SOLUTION SECTION (Section 1, 2, 32) */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm space-y-4">
          <div className="inline-flex items-center gap-2 text-rose-700 bg-rose-50 px-3 py-1 rounded-full text-xs font-bold uppercase">
            <AlertTriangle className="w-4 h-4" />
            <span>The Agricultural Problem</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900">
            Delayed Disease Detection & Inconsistent Records
          </h2>
          <p className="text-slate-600 text-sm leading-relaxed">
            Horticulture cooperative farmers often report crop symptoms late and through informal verbal channels without consistent visual records. Middlemen delays mean expert reviews take days (average 48+ hours), allowing pathogens to spread and destroying crop yield.
          </p>
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs font-mono text-slate-700 space-y-1">
            <p className="text-rose-600 font-semibold">Traditional Delayed Workflow:</p>
            <p>Farmer notices symptom &rarr; Waits / manual call &rarr; Delayed cooperative report &rarr; Expert arrives days later &rarr; Crop loss</p>
          </div>
        </div>

        <div className="bg-white border border-emerald-200 rounded-2xl p-6 sm:p-8 shadow-sm space-y-4 bg-gradient-to-br from-white to-[#E8F5E9]/30">
          <div className="inline-flex items-center gap-2 text-[#2E7D32] bg-[#E8F5E9] px-3 py-1 rounded-full text-xs font-bold uppercase">
            <CheckCircle2 className="w-4 h-4" />
            <span>The HortiSentry Solution</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900">
            Early Digital Screening & Intelligent Escalation
          </h2>
          <p className="text-slate-600 text-sm leading-relaxed">
            HortiSentry empowers farmers to take crop photos, record observed symptoms and growth stages, and receive instant AI decision support. Low-confidence, high-risk, or poor-quality cases are automatically queued for authoritative human expert review, reducing turnaround time by over 90%.
          </p>
          <div className="bg-[#E8F5E9]/60 border border-emerald-200 rounded-xl p-4 text-xs font-mono text-slate-800 space-y-1">
            <p className="text-[#2E7D32] font-semibold">HortiSentry Streamlined Workflow:</p>
            <p>Farmer symptom photo &rarr; AI screening &rarr; Auto-escalation &rarr; Expert priority queue &rarr; Turnaround &lt; 6 hours</p>
          </div>
        </div>
      </section>

      {/* 3. HOW HORTISENTRY WORKS SECTION */}
      <section className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl font-bold text-slate-900">How HortiSentry Works</h2>
          <p className="text-sm text-slate-600">
            A seamless 4-step closed loop connecting farmers, computer vision models, and agricultural extension specialists.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-4">
          <div className="bg-[#F8FAF8] border border-slate-200 p-5 rounded-xl space-y-3">
            <div className="w-10 h-10 rounded-lg bg-[#E8F5E9] text-[#2E7D32] flex items-center justify-center font-bold text-base">
              1
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Capture & Observe</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Farmer photographs crop leaf, selects crop type (Tomato, Chilli, Potato, etc.), growth stage, and checks visible symptoms.
            </p>
          </div>

          <div className="bg-[#F8FAF8] border border-slate-200 p-5 rounded-xl space-y-3">
            <div className="w-10 h-10 rounded-lg bg-[#E8F5E9] text-[#2E7D32] flex items-center justify-center font-bold text-base">
              2
            </div>
            <h3 className="font-bold text-slate-900 text-sm">AI Screening & Risk</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              MobileNetV3 model checks image clarity, predicts possible conditions ("Possible Tomato Early Blight"), and calculates risk score.
            </p>
          </div>

          <div className="bg-[#F8FAF8] border border-slate-200 p-5 rounded-xl space-y-3">
            <div className="w-10 h-10 rounded-lg bg-[#E8F5E9] text-[#2E7D32] flex items-center justify-center font-bold text-base">
              3
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Rule-Based Escalation</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Cases with confidence &lt; 0.85, severe disease traits, or blurry images automatically route to the Expert Priority Queue.
            </p>
          </div>

          <div className="bg-[#F8FAF8] border border-slate-200 p-5 rounded-xl space-y-3">
            <div className="w-10 h-10 rounded-lg bg-[#E8F5E9] text-[#2E7D32] flex items-center justify-center font-bold text-base">
              4
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Authoritative Review</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Agricultural expert reviews photos, confirms/overrides diagnosis, issues actionable guidance, and notifies farmer in &lt; 6 hours.
            </p>
          </div>
        </div>
      </section>

      {/* 4. KEY FEATURES & STAKEHOLDER BENEFITS */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 space-y-4">
          <div className="flex items-center gap-3">
            <div className="bg-[#E8F5E9] p-2.5 rounded-xl text-[#2E7D32]">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">Farmer Benefits</h3>
              <p className="text-xs text-slate-500">Fast, farmer-friendly, minimal friction</p>
            </div>
          </div>
          <ul className="space-y-2.5 text-sm text-slate-600">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
              <span>Instant AI screening without technical terminology</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
              <span>Direct escalation to university/cooperative experts</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
              <span>Live status tracking: Submitted &rarr; Review &rarr; Resolved</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
              <span>Non-identifiable farmer ID protecting personal data</span>
            </li>
          </ul>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 space-y-4">
          <div className="flex items-center gap-3">
            <div className="bg-[#E8F5E9] p-2.5 rounded-xl text-[#2E7D32]">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">Cooperative & Expert Benefits</h3>
              <p className="text-xs text-slate-500">Quality assurance, triage, and actionable data</p>
            </div>
          </div>
          <ul className="space-y-2.5 text-sm text-slate-600">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
              <span>AI triage filters out normal cases, saving expert workload</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
              <span>Priority queue highlights high-risk outbreaks immediately</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
              <span>Objective measurement of Time-to-Expert turnaround KPI</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
              <span>Regional disease hotspot analytics and audit trails</span>
            </li>
          </ul>
        </div>
      </section>

      {/* 5. PRIVACY & RESPONSIBLE AI DISCLAIMER (Sections 3, 35) */}
      <section className="bg-emerald-50/70 border border-emerald-200 rounded-2xl p-6 sm:p-8 space-y-4 text-slate-800">
        <div className="flex items-center gap-2 text-[#1B5E20] font-bold text-base">
          <ShieldCheck className="w-5 h-5 text-[#2E7D32]" />
          <span>Privacy Protection & Responsible AI Commitment</span>
        </div>
        <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
          HortiSentry is designed strictly as an **AI-assisted decision support system**, not a certified diagnosis replacement. Crop disease observations provided by deep learning models are advisory suggestions.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 text-xs text-slate-600">
          <div className="flex items-start gap-2 bg-white/80 p-3 rounded-xl border border-emerald-100">
            <Lock className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-slate-900">Privacy Consciousness</p>
              <p>We do not collect Aadhaar, bank details, or personal photos. Farmers are assigned non-identifiable identifiers (e.g. HS-FARMER-0001).</p>
            </div>
          </div>
          <div className="flex items-start gap-2 bg-white/80 p-3 rounded-xl border border-emerald-100">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-slate-900">Expert Supervision</p>
              <p>AI predictions never prescribe direct chemical dosages. High-impact crop decisions are escalated to human agricultural experts.</p>
            </div>
          </div>
        </div>
        <div className="text-center pt-2 text-xs font-semibold text-[#1B5E20]">
          "AI results are decision-support information and should not replace professional agricultural assessment."
        </div>
      </section>
    </div>
  );
};
