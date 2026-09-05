import React from 'react';

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
  stepName: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  currentStep,
  totalSteps,
  stepName,
}) => {
  const percentage = Math.round((currentStep / totalSteps) * 100);

  return (
    <div className="w-full mb-6">
      <div className="flex justify-between items-center text-xs font-semibold text-emerald-800 mb-1.5">
        <span className="uppercase tracking-wider">
          Step {currentStep} of {totalSteps} — {stepName}
        </span>
        <span>{percentage}%</span>
      </div>
      <div className="w-full bg-emerald-100 rounded-full h-2 overflow-hidden">
        <div
          className="bg-emerald-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
