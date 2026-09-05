import React from 'react';
import { Sprout, CheckCircle2, Clock, Image as ImageIcon } from 'lucide-react';
import { CropConfig } from '../../types';

interface FarmerPlaceholderProps {
  crops: CropConfig[];
}

export const FarmerPlaceholder: React.FC<FarmerPlaceholderProps> = ({ crops }) => {
  const targetCrop = crops.find(c => c.key === 'tomato') || crops[0];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Portal Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="bg-emerald-100 p-3 rounded-2xl text-emerald-700">
            <Sprout className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-slate-900">Farmer Observation Portal</h1>
            <p className="text-xs text-slate-500">Report crop symptoms, run AI image checks, and track expert reviews</p>
          </div>
        </div>
        <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-3 py-1 rounded-full font-medium">
          Phase 2 Foundation Ready
        </span>
      </div>

      {/* Target Crop Preview Shell */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
          <span>Target Crop Selection (Dynamic YAML Config)</span>
        </h2>

        {targetCrop ? (
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
            <div className="flex justify-between items-center">
              <span className="font-bold text-slate-800 text-lg">{targetCrop.display_name}</span>
              <span className="text-xs bg-emerald-600 text-white px-2 py-0.5 rounded font-semibold">
                Active
              </span>
            </div>
            <p className="text-xs text-slate-600">{targetCrop.description}</p>
            
            <div className="pt-2 border-t border-slate-200">
              <span className="text-xs font-semibold text-slate-700 block mb-2">Supported Growth Stages:</span>
              <div className="flex flex-wrap gap-1.5">
                {targetCrop.stages.map((stage) => (
                  <span key={stage.key} className="bg-white text-slate-700 text-xs px-2.5 py-1 rounded border border-slate-300">
                    {stage.display_name}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-slate-500">Loading crop configuration...</p>
        )}
      </div>

      {/* Workflow Steps Preview Shell */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h3 className="font-bold text-slate-900 text-sm mb-4">Farmer Workflow Pipeline (Phase 3+ Implementation)</h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1">
            <div className="font-bold text-slate-800 flex items-center space-x-1">
              <span className="bg-emerald-700 text-white rounded-full w-4 h-4 text-[10px] flex items-center justify-center">1</span>
              <span>Select Crop</span>
            </div>
            <p className="text-slate-500">Choose horticultural crop (Tomato active)</p>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1">
            <div className="font-bold text-slate-800 flex items-center space-x-1">
              <span className="bg-emerald-700 text-white rounded-full w-4 h-4 text-[10px] flex items-center justify-center">2</span>
              <span>Upload Photo</span>
            </div>
            <p className="text-slate-500">Client quality & blur inspection</p>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1">
            <div className="font-bold text-slate-800 flex items-center space-x-1">
              <span className="bg-emerald-700 text-white rounded-full w-4 h-4 text-[10px] flex items-center justify-center">3</span>
              <span>Symptoms & Stage</span>
            </div>
            <p className="text-slate-500">Select observed symptoms & location</p>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1">
            <div className="font-bold text-slate-800 flex items-center space-x-1">
              <span className="bg-emerald-700 text-white rounded-full w-4 h-4 text-[10px] flex items-center justify-center">4</span>
              <span>AI Evaluation</span>
            </div>
            <p className="text-slate-500">Confidence scoring & Expert escalation</p>
          </div>
        </div>
      </div>
    </div>
  );
};
