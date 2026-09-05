import React, { useEffect, useState } from 'react';
import { Layers, Search, ArrowLeft, CheckCircle2, ShieldCheck, Sprout } from 'lucide-react';
import { fetchAdminCrops } from '../../services/api';
import { CropConfig } from '../../types';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface CropManagementProps {
  onNavigate: (route: string) => void;
}

export const CropManagement: React.FC<CropManagementProps> = ({ onNavigate }) => {
  const [crops, setCrops] = useState<CropConfig[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    const loadCrops = async () => {
      try {
        const data = await fetchAdminCrops();
        setCrops(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load crop taxonomy');
      } finally {
        setLoading(false);
      }
    };
    loadCrops();
  }, []);

  const handleToggleActive = (cropKey: string) => {
    setCrops((prev) =>
      prev.map((c) => (c.key === cropKey ? { ...c, is_active: c.is_active === false ? true : false } : c))
    );
  };

  const filteredCrops = crops.filter((c) => {
    if (categoryFilter !== 'ALL' && c.category?.toLowerCase() !== categoryFilter.toLowerCase()) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchKey = c.key.toLowerCase().includes(q);
      const matchCommon = c.common_name?.toLowerCase().includes(q);
      const matchScientific = c.scientific_name?.toLowerCase().includes(q);
      const matchTa = c.display_name_ta?.toLowerCase().includes(q);
      return matchKey || matchCommon || matchScientific || matchTa;
    }
    return true;
  });

  return (
    <div className="space-y-6 py-2">
      {/* Top bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <button
            onClick={() => onNavigate('/admin')}
            className="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-slate-800"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Dashboard</span>
          </button>
          <h1 className="text-2xl font-extrabold text-[#1F2937] tracking-tight">
            Horticultural Crop Catalogue ({crops.length} Crops)
          </h1>
          <p className="text-xs text-slate-500">
            Cooperative crop taxonomy covering Vegetables, Fruits, Spices, and Plantation crops
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by crop name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-[#2E7D32]"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs font-bold text-slate-500 whitespace-nowrap">Category:</span>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="w-full sm:w-auto px-3 py-2 rounded-xl border border-slate-300 text-xs font-semibold focus:ring-2 focus:ring-[#2E7D32]"
          >
            <option value="ALL">All Categories</option>
            <option value="vegetables">Vegetables</option>
            <option value="fruits">Fruits</option>
            <option value="spices_plantation">Spices & Plantation</option>
          </select>
        </div>
      </div>

      {/* Crops Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-8"><LoadingSpinner message="Loading crop catalogue..." /></div>
        ) : error ? (
          <div className="p-8 text-center text-rose-600 text-sm">{error}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-[#F8FAF8] border-b border-slate-200 text-slate-700 font-bold uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="px-5 py-3.5">Crop Name</th>
                  <th className="px-5 py-3.5">Category</th>
                  <th className="px-5 py-3.5">Vision Model Support</th>
                  <th className="px-5 py-3.5">Observable Symptoms</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredCrops.map((c) => {
                  const isTrained = c.key === 'tomato' || c.vision_support_status === 'trained_model';
                  const cropImg = `/images/crops/${c.key}.jpg`;
                  return (
                    <tr key={c.key} className="hover:bg-[#F8FAF8]/80 transition-colors">
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg overflow-hidden bg-slate-100 flex-shrink-0 border border-slate-200">
                            <img
                              src={cropImg}
                              alt={c.display_name || c.common_name || c.key}
                              className="w-full h-full object-cover"
                              loading="lazy"
                              onError={(e) => {
                                (e.target as HTMLImageElement).src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="%232E7D32" stroke-width="2"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>';
                              }}
                            />
                          </div>
                          <div>
                            <div className="font-bold text-slate-900 text-sm">
                              {c.display_name || c.common_name || c.key}
                            </div>
                            <div className="text-slate-400 text-[11px] capitalize">
                              {c.category?.replace('_', ' ') || 'Horticulture'}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        <span className="capitalize text-slate-700 font-semibold bg-slate-100 px-2 py-0.5 rounded">
                          {c.category?.replace('_', ' ') || 'General'}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        {isTrained ? (
                          <span className="inline-flex items-center gap-1 text-[#1B5E20] font-bold bg-[#E8F5E9] border border-[#C8E6C9] px-2.5 py-0.5 rounded-full">
                            <CheckCircle2 className="w-3.5 h-3.5 text-[#2E7D32]" />
                            MobileNetV3 Deep Vision
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-full">
                            Symptom Triage Gate
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {(c.symptoms || ['Spots', 'Curling', 'Wilting']).slice(0, 3).map((sym: any, idx: number) => (
                            <span key={idx} className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded text-[10px]">
                              {typeof sym === 'string' ? sym : sym.display_name || String(sym)}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        {c.is_active !== false ? (
                          <span className="text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full font-bold inline-flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            Active
                          </span>
                        ) : (
                          <span className="text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full font-semibold">
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-4 text-right">
                        <button
                          onClick={() => handleToggleActive(c.key)}
                          className="text-xs font-semibold text-slate-600 hover:text-slate-900 border border-slate-200 px-2.5 py-1 rounded-lg hover:bg-slate-50"
                        >
                          Toggle
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
