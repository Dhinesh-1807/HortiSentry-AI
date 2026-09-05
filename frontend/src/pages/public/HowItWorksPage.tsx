import React, { useState } from 'react';
import {
  Camera,
  Search,
  Cpu,
  AlertTriangle,
  UserCheck,
  CheckCircle2,
  ArrowRight,
  Clock,
  ShieldAlert,
  Zap,
  ChevronRight
} from 'lucide-react';

interface HowItWorksPageProps {
  onNavigate: (route: string) => void;
}

export const HowItWorksPage: React.FC<HowItWorksPageProps> = ({ onNavigate }) => {
  const [activeStep, setActiveStep] = useState<number>(1);

  const steps = [
    {
      id: 1,
      title: '1. Leaf Photo & Observation Capture',
      subtitle: 'Farmer documents symptom in field',
      icon: Camera,
      badge: 'Step 1: Input',
      color: 'text-emerald-700 bg-emerald-50 border-emerald-200',
      description:
        'The farmer selects the crop from the 32-crop horticulture catalogue, specifies growth stage, selects visual symptoms, sets subjective confidence, and uploads a clear leaf photograph from their mobile device.',
      technicalDetails: [
        'Client-side image validation (JPG, PNG, WEBP, max 10MB)',
        'Observation timestamp and location metadata logged',
        'Optional crop variety recorded for epidemiological monitoring'
      ]
    },
    {
      id: 2,
      title: '2. Image Quality & Preprocessing',
      subtitle: 'OpenCV automated quality gate',
      icon: Search,
      badge: 'Step 2: Quality Gate',
      color: 'text-blue-700 bg-blue-50 border-blue-200',
      description:
        'Before neural classification, the image is assessed for sharpness and illumination. Blurry images or extreme under/over-exposure are identified immediately.',
      technicalDetails: [
        'Laplacian variance calculates blur score (threshold: 100.0)',
        'Mean pixel luminance evaluates lighting (acceptable: 40 - 220)',
        'Flagged images prompt farmer retake or auto-escalate for manual inspection'
      ]
    },
    {
      id: 3,
      title: '3. MobileNetV3 AI Inference',
      subtitle: 'Lightweight deep learning classification',
      icon: Cpu,
      badge: 'Step 3: Neural AI',
      color: 'text-purple-700 bg-purple-50 border-purple-200',
      description:
        'The normalized leaf image is processed by a MobileNetV3-Small architecture trained on 6,271 balanced horticulture images across 10 condition classes.',
      technicalDetails: [
        'Multi-class softmax probability distribution computed',
        'Extracts top-1 predicted condition and confidence score',
        'CPU-optimized inference under 300ms on standard cloud or edge servers'
      ]
    },
    {
      id: 4,
      title: '4. Rule-Based Escalation Engine',
      subtitle: 'Policy driven via config/escalation.yaml',
      icon: AlertTriangle,
      badge: 'Step 4: Decision Policy',
      color: 'text-amber-700 bg-amber-50 border-amber-200',
      description:
        'A deterministic escalation evaluator checks predictions against configured thresholds. Observations never get lost or silently misclassified.',
      technicalDetails: [
        'High Risk diseases (e.g. Late Blight, Tomato Yellow Leaf Curl) auto-escalate',
        'Low confidence predictions (<60%) or blurred images route to triage queue',
        'Farmer-requested second opinion overrides automated status'
      ]
    },
    {
      id: 5,
      title: '5. Agricultural Expert Review',
      subtitle: 'Specialist confirms or overrides with audit trail',
      icon: UserCheck,
      badge: 'Step 5: Human in the Loop',
      color: 'text-indigo-700 bg-indigo-50 border-indigo-200',
      description:
        'Extension officers and plant pathologists review cases sorted by urgency. High-risk and low-confidence cases sit at the top of the priority queue.',
      technicalDetails: [
        'Dual records preserved: original AI prediction vs verified expert diagnosis',
        'Expert provides severity rating, treatment recommendations, and follow-up notes',
        'Review timestamp recorded to calculate strict Time-to-Expert KPI (<6h SLA)'
      ]
    },
    {
      id: 6,
      title: '6. Resolution & Farmer Advisory',
      subtitle: 'Immediate actionable guidance delivered',
      icon: CheckCircle2,
      badge: 'Step 6: Resolution',
      color: 'text-[#1B5E20] bg-[#E8F5E9] border-[#C8E6C9]',
      description:
        'The farmer receives an updated status notification. The observation record displays verified agronomic management actions and preventive cultural practices.',
      technicalDetails: [
        'Real-time in-app notification and persistent observation timeline',
        'Cooperative manager dashboard aggregates regional disease clusters',
        'Historical records feed continuous retraining and error analysis audits'
      ]
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-12 py-6">
      {/* Header */}
      <div className="text-center space-y-3">
        <span className="inline-flex items-center gap-2 bg-[#E8F5E9] text-[#1B5E20] px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
          <Zap className="w-4 h-4 text-[#2E7D32]" />
          Platform Architecture & Workflow
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#1F2937] tracking-tight">
          How HortiSentry Works
        </h1>
        <p className="text-slate-600 max-w-2xl mx-auto text-sm sm:text-base">
          From leaf symptom photo in the field to verified agronomic advisory: explore the 6-stage AI and human-in-the-loop pipeline.
        </p>
      </div>

      {/* KPI Comparison Highlights */}
      <div className="bg-gradient-to-r from-[#1B5E20] to-[#2E7D32] text-white rounded-2xl p-6 sm:p-8 shadow-md">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
          <div className="space-y-1">
            <span className="text-xs uppercase tracking-wider text-emerald-200 font-semibold">Traditional Baseline</span>
            <div className="text-3xl font-extrabold text-white">48.0 Hours</div>
            <p className="text-xs text-emerald-200/80">Average cooperative response</p>
          </div>

          <div className="space-y-1 sm:border-x sm:border-emerald-600/60 px-4">
            <span className="text-xs uppercase tracking-wider text-emerald-200 font-semibold">HortiSentry Measured</span>
            <div className="text-3xl font-extrabold text-[#C8E6C9]">4.5 Hours</div>
            <p className="text-xs text-emerald-200/80">Median Time-to-Expert review</p>
          </div>

          <div className="space-y-1">
            <span className="text-xs uppercase tracking-wider text-emerald-200 font-semibold">Speed Improvement</span>
            <div className="text-3xl font-extrabold text-white">90.6% Faster</div>
            <p className="text-xs text-emerald-200/80">Target &lt;6.0h SLA met</p>
          </div>
        </div>
      </div>

      {/* Interactive Step Navigator */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
        {steps.map((s) => (
          <button
            key={s.id}
            onClick={() => setActiveStep(s.id)}
            className={`p-3 rounded-xl border text-left transition-all ${
              activeStep === s.id
                ? 'bg-[#E8F5E9] border-[#2E7D32] shadow-sm ring-2 ring-[#2E7D32]/20'
                : 'bg-white border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className={`text-xs font-extrabold ${activeStep === s.id ? 'text-[#1B5E20]' : 'text-slate-400'}`}>
                #{s.id}
              </span>
              <s.icon className={`w-4 h-4 ${activeStep === s.id ? 'text-[#2E7D32]' : 'text-slate-400'}`} />
            </div>
            <div className="text-xs font-bold text-slate-800 line-clamp-1">
              {s.title.split('. ')[1]}
            </div>
          </button>
        ))}
      </div>

      {/* Active Step Detailed Card */}
      {steps.filter((s) => s.id === activeStep).map((s) => (
        <div key={s.id} className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className={`p-4 rounded-2xl border ${s.color}`}>
                <s.icon className="w-8 h-8" />
              </div>
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{s.badge}</span>
                <h2 className="text-2xl font-bold text-[#1F2937]">{s.title}</h2>
                <p className="text-sm text-slate-500">{s.subtitle}</p>
              </div>
            </div>
          </div>

          <p className="text-sm sm:text-base text-slate-700 leading-relaxed">
            {s.description}
          </p>

          <div className="bg-[#F8FAF8] rounded-xl p-5 border border-slate-200/80 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Technical Implementation Details:
            </h3>
            <ul className="space-y-2">
              {s.technicalDetails.map((td, idx) => (
                <li key={idx} className="flex items-center gap-2.5 text-xs sm:text-sm text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0" />
                  <span>{td}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex justify-between items-center pt-2">
            <button
              disabled={activeStep === 1}
              onClick={() => setActiveStep((prev) => Math.max(1, prev - 1))}
              className="text-xs font-bold text-slate-600 hover:text-slate-900 disabled:opacity-30 disabled:pointer-events-none px-3 py-1.5"
            >
              Previous Step
            </button>
            <button
              disabled={activeStep === steps.length}
              onClick={() => setActiveStep((prev) => Math.min(steps.length, prev + 1))}
              className="bg-[#2E7D32] hover:bg-[#1B5E20] text-white font-bold text-xs px-4 py-2 rounded-lg transition-all disabled:opacity-30 disabled:pointer-events-none inline-flex items-center gap-1.5"
            >
              <span>Next Step</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      ))}

      {/* Call to action */}
      <div className="text-center pt-4">
        <button
          onClick={() => onNavigate('/farmer/observation/new')}
          className="bg-[#2E7D32] hover:bg-[#1B5E20] text-white font-bold px-8 py-3.5 rounded-xl shadow-md transition-all inline-flex items-center gap-2 text-sm sm:text-base"
        >
          <Camera className="w-5 h-5" />
          <span>Report a Crop Symptom Now</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
