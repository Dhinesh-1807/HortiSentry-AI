import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorPageProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorPage: React.FC<ErrorPageProps> = ({
  title = 'Connection Error',
  message = 'Unable to connect to the HortiSentry backend server. Please verify backend status.',
  onRetry
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 min-h-[400px]">
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 max-w-md text-center shadow-sm">
        <div className="bg-red-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4 text-red-600">
          <AlertTriangle className="h-6 w-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 mb-2">{title}</h3>
        <p className="text-sm text-slate-600 mb-6">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-colors shadow-sm"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Retry Connection</span>
          </button>
        )}
      </div>
    </div>
  );
};
