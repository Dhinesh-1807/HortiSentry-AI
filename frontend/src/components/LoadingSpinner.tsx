import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingProps {
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingProps> = ({ message = 'Loading HortiSentry...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-slate-500 min-h-[300px]">
      <Loader2 className="h-8 w-8 text-emerald-600 animate-spin mb-3" />
      <p className="text-sm font-medium text-slate-600">{message}</p>
    </div>
  );
};
