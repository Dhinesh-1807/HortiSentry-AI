import React from 'react';
import { Sprout, ShieldCheck, Cpu, ArrowRight } from 'lucide-react';
import { HealthStatus, CropConfig } from '../types';

interface HomePageProps {
  health: HealthStatus | null;
  crops: CropConfig[];
  onSelectRole: (role: 'farmer') => void;
}

export const HomePage: React.FC<HomePageProps> = ({ health, crops, onSelectRole }) => {
  return (
    <div className="max-w-5xl mx-auto space-y-8 py-4">
      
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-emerald-900 via-emerald-800 to-slate-900 text-white rounded-3xl p-8 sm:p-12 shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center space-x-2 bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-4">
            <ShieldCheck className="h-4 w-4" />
            <span>AI Evidence Engine & Visual Observation</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-3">
            HortiSentry — See Early. Act Smart. Protect Crops.
          </h1>
          <p className="text-emerald-100 text-base sm:text-lg mb-8 leading-relaxed">
            Empowering horticultural farmers across 32 crops with instant AI visual symptom analysis and evidence-backed guidance from trusted agricultural research institutions.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={() => onSelectRole('farmer')}
              className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-6 py-3.5 rounded-xl shadow-lg hover:shadow-emerald-500/30 transition-all flex items-center justify-center space-x-2 text-base"
            >
              <Sprout className="h-5 w-5" />
              <span>Launch Farmer Portal</span>
              <ArrowRight className="h-5 w-5 ml-1" />
            </button>
          </div>
        </div>
      </div>

      {/* System Status & Dynamic Crop Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* API Status Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-emerald-100 p-2.5 rounded-xl text-emerald-700">
              <Cpu className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">System Engine Status</h3>
              <span className="text-xs text-slate-500">FastAPI & SQLite Backend</span>
            </div>
          </div>
          <div className="space-y-2 text-xs text-slate-600 mt-4 border-t border-slate-100 pt-3">
            <div className="flex justify-between">
              <span>API Status:</span>
              <span className="font-semibold text-emerald-600 uppercase">{health?.status || 'Connecting...'}</span>
            </div>
            <div className="flex justify-between">
              <span>Database Connection:</span>
              <span className="font-semibold text-emerald-600 capitalize">{health?.database || 'Pending'}</span>
            </div>
            <div className="flex justify-between">
              <span>ML Engine Mode:</span>
              <span className={`font-bold px-2 py-0.5 rounded text-[11px] ${
                health?.ml_mode === 'DEMO' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
              }`}>
                {health?.ml_mode || 'DEMO'} MODE
              </span>
            </div>
          </div>
        </div>

        {/* Dynamic Target Crop Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm md:col-span-2">
          <h3 className="font-bold text-slate-900 text-sm mb-3">Supported Horticultural Crops</h3>
          {crops.length > 0 ? (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-emerald-800 text-base">32 Horticultural Crops Active</span>
                <span className="bg-emerald-100 text-emerald-800 text-xs px-2.5 py-0.5 rounded-full font-semibold">
                  Multi-Crop Platform
                </span>
              </div>
              <p className="text-xs text-slate-600 mb-3">Integrated visual symptom analysis & ICAR/TNAU/FAO automated evidence review engine.</p>
              <div className="flex flex-wrap gap-2 text-xs">
                <span className="bg-white text-slate-700 px-2.5 py-1 rounded border border-slate-200 font-medium">
                  10 Vegetables
                </span>
                <span className="bg-white text-slate-700 px-2.5 py-1 rounded border border-slate-200 font-medium">
                  12 Fruits
                </span>
                <span className="bg-white text-slate-700 px-2.5 py-1 rounded border border-slate-200 font-medium">
                  10 Spices & Plantation
                </span>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500">Loading dynamic crop configurations...</p>
          )}
        </div>
      </div>
    </div>
  );
};
