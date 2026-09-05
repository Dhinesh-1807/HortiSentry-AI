import React from 'react';
import { ShieldCheck, Info, Sprout } from 'lucide-react';

interface FooterProps {
  onNavigate?: (route: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer className="bg-[#E8F5E9] text-[#1F2937] border-t border-[#C8E6C9] text-xs py-8 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <div className="w-7 h-7 bg-[#2E7D32] rounded-lg text-white flex items-center justify-center">
                <Sprout className="h-4 w-4" />
              </div>
              <span className="font-extrabold text-base text-[#1B5E20] tracking-tight">HortiSentry</span>
              <span className="text-[#2E7D32] font-semibold">|</span>
              <span className="text-slate-600 font-medium">Horticulture Disease Surveillance Platform</span>
            </div>
            <p className="text-slate-500 text-[11px]">
              "See Early. Act Smart. Protect Crops." • Engineered for Smallholder Horticulture Cooperatives
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs font-semibold text-[#1B5E20]">
            {onNavigate && (
              <>
                <button onClick={() => onNavigate('/')} className="hover:underline">Home</button>
                <button onClick={() => onNavigate('/about')} className="hover:underline">About</button>
                <button onClick={() => onNavigate('/how-it-works')} className="hover:underline">How It Works</button>
                <button onClick={() => onNavigate('/farmer/observation/new')} className="hover:underline">Report Symptom</button>
              </>
            )}
          </div>
        </div>

        {/* Responsible AI Disclaimer */}
        <div className="pt-4 border-t border-[#C8E6C9]/60 flex items-start gap-2.5 text-[11px] text-slate-600 leading-relaxed">
          <Info className="h-4 w-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
          <p>
            <strong className="text-[#1B5E20]">Agronomic Decision Support Notice: </strong>
            HortiSentry provides AI-assisted preliminary observation screening and automated escalation to human agricultural specialists. Outputs are informational and do not replace certified agronomist recommendations. Treatment protocols should be verified by cooperative extension personnel.
          </p>
        </div>
      </div>
    </footer>
  );
};
