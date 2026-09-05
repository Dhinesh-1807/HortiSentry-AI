import React, { useEffect, useState } from 'react';
import {
  Cpu,
  Database,
  CheckCircle2,
  ArrowLeft,
  AlertTriangle,
  Award,
  Layers,
  FileSpreadsheet,
  HelpCircle
} from 'lucide-react';
import { fetchAdminModelMetrics, fetchAdminDatasetMetrics } from '../../services/api';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface ModelDatasetInfoProps {
  onNavigate: (route: string) => void;
}

export const ModelDatasetInfo: React.FC<ModelDatasetInfoProps> = ({ onNavigate }) => {
  const [modelMetrics, setModelMetrics] = useState<any | null>(null);
  const [datasetMetrics, setDatasetMetrics] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadInfo = async () => {
      try {
        const [modelRes, datasetRes] = await Promise.all([
          fetchAdminModelMetrics(),
          fetchAdminDatasetMetrics()
        ]);
        setModelMetrics(modelRes);
        setDatasetMetrics(datasetRes);
      } catch (err: any) {
        setError(err.message || 'Failed to load model and dataset metrics');
      } finally {
        setLoading(false);
      }
    };
    loadInfo();
  }, []);

  if (loading) return <LoadingSpinner message="Loading MobileNetV3 evaluation metrics and dataset split reports..." />;
  if (error || !modelMetrics || !datasetMetrics) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-rose-200 text-center space-y-4 max-w-md mx-auto">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h2 className="text-lg font-bold text-slate-800">Metrics Unavailable</h2>
        <p className="text-xs text-slate-500">{error || 'Could not fetch metrics data.'}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-[#2E7D32] text-white text-xs font-bold px-4 py-2 rounded-xl"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 py-2">
      {/* Header */}
      <div className="space-y-1">
        <button
          onClick={() => onNavigate('/admin')}
          className="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-slate-800"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Dashboard</span>
        </button>
        <h1 className="text-2xl font-extrabold text-[#1F2937] tracking-tight">
          AI Model Evaluation & Dataset Metadata
        </h1>
        <p className="text-xs text-slate-500">
          MobileNetV3 test set benchmark results, confusion analysis, and balanced dataset distributions
        </p>
      </div>

      {/* MODEL PERFORMANCE SUMMARY */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-[#E8F5E9] text-[#1B5E20]">
              <Cpu className="w-6 h-6 text-[#2E7D32]" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-[#1F2937]">MobileNetV3-Small Classifier Metrics</h2>
              <p className="text-xs text-slate-500">Evaluated on independent 942-sample holdout test partition</p>
            </div>
          </div>
          <span className="bg-[#E8F5E9] text-[#1B5E20] border border-[#C8E6C9] text-xs font-bold px-3 py-1 rounded-full">
            Inference: &lt; 300ms / image
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-[#F8FAF8] p-4 rounded-xl border border-slate-200/80 text-center space-y-1">
            <span className="text-xs font-bold text-slate-500 uppercase">Test Accuracy</span>
            <div className="text-2xl sm:text-3xl font-black text-[#1B5E20]">
              {(modelMetrics.accuracy * 100).toFixed(2)}%
            </div>
            <p className="text-[10px] text-slate-400">942 test instances</p>
          </div>

          <div className="bg-[#F8FAF8] p-4 rounded-xl border border-slate-200/80 text-center space-y-1">
            <span className="text-xs font-bold text-slate-500 uppercase">Macro Precision</span>
            <div className="text-2xl sm:text-3xl font-black text-indigo-700">
              {(modelMetrics.macro_precision * 100).toFixed(2)}%
            </div>
            <p className="text-[10px] text-slate-400">Balanced class weighting</p>
          </div>

          <div className="bg-[#F8FAF8] p-4 rounded-xl border border-slate-200/80 text-center space-y-1">
            <span className="text-xs font-bold text-slate-500 uppercase">Macro Recall</span>
            <div className="text-2xl sm:text-3xl font-black text-amber-700">
              {(modelMetrics.macro_recall * 100).toFixed(2)}%
            </div>
            <p className="text-[10px] text-slate-400">Sensitivity detection</p>
          </div>

          <div className="bg-[#F8FAF8] p-4 rounded-xl border border-slate-200/80 text-center space-y-1">
            <span className="text-xs font-bold text-slate-500 uppercase">Macro F1 Score</span>
            <div className="text-2xl sm:text-3xl font-black text-[#2E7D32]">
              {(modelMetrics.macro_f1 * 100).toFixed(2)}%
            </div>
            <p className="text-[10px] text-slate-400">Harmonic mean balance</p>
          </div>
        </div>
      </div>

      {/* PER-CLASS PERFORMANCE TABLE */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden space-y-2 p-6">
        <h3 className="text-sm font-bold text-slate-800">Per-Condition Classification Breakdown</h3>
        <p className="text-xs text-slate-500">Full breakdown across 10 tomato leaf condition classes</p>

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F8FAF8] text-slate-500 uppercase font-bold border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Condition / Class</th>
                <th className="px-4 py-3">Precision</th>
                <th className="px-4 py-3">Recall</th>
                <th className="px-4 py-3">F1 Score</th>
                <th className="px-4 py-3 text-right">Support (Test)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(modelMetrics.per_class_metrics || []).map((c: any, idx: number) => (
                <tr key={idx} className="hover:bg-[#F8FAF8]/80 transition-colors">
                  <td className="px-4 py-3 font-bold text-slate-900">{c.class_name || c.name}</td>
                  <td className="px-4 py-3 font-mono text-slate-700">
                    {(c.precision * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 font-mono text-slate-700">
                    {(c.recall * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 font-mono font-bold text-[#1B5E20]">
                    {(c.f1_score * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 font-mono text-slate-500 text-right">
                    {c.support}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* DATASET SPLIT & METADATA SECTION */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-[#E8F5E9] text-[#1B5E20]">
            <Database className="w-6 h-6 text-[#2E7D32]" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-[#1F2937]">Dataset Partition & Ethics Pipeline</h2>
            <p className="text-xs text-slate-500">6,271 balanced records with zero farmer PII</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="p-4 bg-[#F8FAF8] rounded-xl border border-slate-200 text-center space-y-1">
            <span className="text-xs font-bold text-slate-500">Total Samples</span>
            <div className="text-2xl font-black text-slate-900">{datasetMetrics.total_samples || 6271}</div>
            <p className="text-[10px] text-slate-400">dataset_metadata.csv</p>
          </div>

          <div className="p-4 bg-[#F8FAF8] rounded-xl border border-slate-200 text-center space-y-1">
            <span className="text-xs font-bold text-slate-500">Training Set (70%)</span>
            <div className="text-2xl font-black text-[#1B5E20]">{datasetMetrics.train_samples || 4389}</div>
            <p className="text-[10px] text-slate-400">Class-stratified split</p>
          </div>

          <div className="p-4 bg-[#F8FAF8] rounded-xl border border-slate-200 text-center space-y-1">
            <span className="text-xs font-bold text-slate-500">Validation Set (15%)</span>
            <div className="text-2xl font-black text-indigo-700">{datasetMetrics.val_samples || 940}</div>
            <p className="text-[10px] text-slate-400">Hyperparameter tuning</p>
          </div>

          <div className="p-4 bg-[#F8FAF8] rounded-xl border border-slate-200 text-center space-y-1">
            <span className="text-xs font-bold text-slate-500">Test Set (15%)</span>
            <div className="text-2xl font-black text-amber-700">{datasetMetrics.test_samples || 942}</div>
            <p className="text-[10px] text-slate-400">Holdout benchmark</p>
          </div>
        </div>

        {/* Error Analysis Box */}
        <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-xl space-y-2 text-xs text-amber-950">
          <div className="font-bold flex items-center gap-1.5 text-amber-900">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>Systematic Error Analysis & Triage Policy:</span>
          </div>
          <p className="leading-relaxed">
            Confusion matrix analysis identifies occasional boundary confusion between <em>Septoria Leaf Spot</em> and <em>Early Blight</em> in early necrotic stages. In HortiSentry, when probability margins between top-2 classes are under 15%, the case is automatically escalated with the tag <code>LOW_CONFIDENCE</code> for human agronomist review.
          </p>
        </div>
      </div>
    </div>
  );
};
