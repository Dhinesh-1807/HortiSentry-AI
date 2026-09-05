import React, { useEffect, useState } from 'react';
import { PlusCircle, Clock, MapPin, ChevronRight, Loader2, Leaf, ShieldAlert } from 'lucide-react';
import { fetchObservations } from '../../services/api';
import { ObservationListItem } from '../../types';
import { Badge } from '../../components/Badge';

interface ObservationHistoryProps {
  onNavigate: (route: string) => void;
}

export const ObservationHistory: React.FC<ObservationHistoryProps> = ({ onNavigate }) => {
  const [observations, setObservations] = useState<ObservationListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const list = await fetchObservations();
        setObservations(list);
      } catch (err: any) {
        console.error('Failed to load observation history:', err);
        setError(err.message || 'Could not load observation history.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900">Observation History</h1>
          <p className="text-xs text-slate-500">View and track all your reported crop disease observations</p>
        </div>
        <button
          onClick={() => onNavigate('/farmer/observation/new')}
          className="inline-flex items-center gap-1.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs px-3.5 py-2 rounded-xl transition-all shadow-sm"
        >
          <PlusCircle className="w-4 h-4" />
          New Observation
        </button>
      </div>

      {loading ? (
        <div className="py-16 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-600">Loading observation history...</p>
        </div>
      ) : error ? (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center space-y-3">
          <ShieldAlert className="w-8 h-8 text-rose-500 mx-auto" />
          <p className="text-sm font-bold text-slate-800">{error}</p>
        </div>
      ) : observations.length === 0 ? (
        <div className="py-12 text-center bg-white rounded-2xl border border-slate-200 space-y-3 p-6">
          <div className="w-12 h-12 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto">
            <Leaf className="w-6 h-6" />
          </div>
          <div>
            <p className="font-bold text-slate-800">No observations yet</p>
            <p className="text-xs text-slate-500 max-w-xs mx-auto mt-1">
              Submit your first crop photo to get started with AI disease observation.
            </p>
          </div>
          <button
            onClick={() => onNavigate('/farmer/observation/new')}
            className="inline-flex items-center gap-1.5 bg-emerald-700 text-white font-semibold text-xs px-4 py-2 rounded-lg"
          >
            <PlusCircle className="w-4 h-4" />
            Create First Observation
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {observations.map((obs) => (
            <div
              key={obs.id}
              onClick={() => onNavigate(`/farmer/observations/${obs.id}`)}
              className="bg-white p-4 rounded-2xl border border-slate-200 hover:border-emerald-400 hover:shadow-md transition-all cursor-pointer flex items-center justify-between gap-3"
            >
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900 text-base">{obs.crop_display_name}</span>
                  <span className="text-xs text-slate-500 font-medium">• {obs.crop_stage}</span>
                </div>
                <p className="text-xs font-bold text-emerald-800">
                  {obs.predicted_class ? `AI: ${obs.predicted_class}` : 'Processing AI result...'}
                </p>
                <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400">
                  <span className="inline-flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    {new Date(obs.submitted_at).toLocaleDateString()}
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-slate-400" />
                    {obs.location_village}, {obs.location_district}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex flex-col items-end gap-1">
                  <Badge status={obs.status} />
                  {obs.confidence !== undefined && (
                    <span className="text-xs font-black text-slate-700">
                      {Math.round(obs.confidence * 100)}%
                    </span>
                  )}
                </div>
                <ChevronRight className="w-5 h-5 text-slate-400" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
