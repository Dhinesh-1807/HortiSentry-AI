import React, { useState, useEffect } from 'react';
import { ZoomIn, ZoomOut, AlertTriangle, CheckCircle2, Leaf, RotateCw } from 'lucide-react';

interface CaseImageViewerProps {
  imageUrl: string;
  qualityAnalysis?: {
    is_blur_detected?: boolean;
    is_exposure_issue?: boolean;
    blur_score?: number;
    width?: number;
    height?: number;
  };
}

export const CaseImageViewer: React.FC<CaseImageViewerProps> = ({
  imageUrl,
  qualityAnalysis,
}) => {
  const [zoom, setZoom] = useState<number>(1);
  const [imgError, setImgError] = useState<boolean>(false);

  useEffect(() => {
    setImgError(false);
  }, [imageUrl]);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.3, 2.5));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.3, 0.8));

  const hasQualityWarning = qualityAnalysis?.is_blur_detected || qualityAnalysis?.is_exposure_issue;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-4 space-y-3 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Crop Photo Inspection
        </h3>
        {!imgError && imageUrl && (
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg">
            <button
              onClick={handleZoomOut}
              className="p-1 text-slate-600 hover:text-slate-900 hover:bg-slate-200 rounded"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-[11px] font-mono font-bold text-slate-700 px-1">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={handleZoomIn}
              className="p-1 text-slate-600 hover:text-slate-900 hover:bg-slate-200 rounded"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Main Image Container */}
      {!imageUrl || imgError ? (
        <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-50 border border-dashed border-slate-200 rounded-xl min-h-[300px]">
          <div className="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600 mb-3 shadow-2xs">
            <Leaf className="w-7 h-7" />
          </div>
          <h4 className="text-sm font-bold text-slate-800">Crop Leaf Photo Unavailable</h4>
          <p className="text-xs text-slate-500 max-w-xs mt-1 leading-relaxed">
            The escalated crop leaf image could not be loaded or is not present in storage.
          </p>
          {imageUrl && (
            <button
              onClick={() => setImgError(false)}
              className="mt-4 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors border border-emerald-200 shadow-2xs"
            >
              <RotateCw className="w-3.5 h-3.5" /> Retry Loading
            </button>
          )}
        </div>
      ) : (
        <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-950 flex items-center justify-center min-h-[300px] max-h-[420px]">
          <img
            src={imageUrl}
            alt="Escalated Leaf Inspection"
            style={{ transform: `scale(${zoom})` }}
            className="transition-transform duration-200 ease-out max-h-[400px] w-auto object-contain select-none"
            onError={() => setImgError(true)}
          />
        </div>
      )}

      {/* Quality Overlay Metrics */}
      <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-2 text-xs">
        <div className="flex items-center justify-between">
          <span className="font-bold text-slate-800">Quality Diagnostic Status:</span>
          {hasQualityWarning ? (
            <span className="inline-flex items-center gap-1 font-bold text-amber-900 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded">
              <AlertTriangle className="w-3.5 h-3.5" /> Needs Attention
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 font-bold text-emerald-900 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded">
              <CheckCircle2 className="w-3.5 h-3.5" /> Sharp & Clear
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-1 border-t border-slate-200/80 text-[11px]">
          <div>
            <span className="text-slate-500">Blur Detected: </span>
            <span className={qualityAnalysis?.is_blur_detected ? 'font-bold text-rose-600' : 'font-semibold text-slate-800'}>
              {qualityAnalysis?.is_blur_detected ? 'Yes (Blurry)' : 'No'}
            </span>
          </div>
          <div>
            <span className="text-slate-500">Exposure: </span>
            <span className={qualityAnalysis?.is_exposure_issue ? 'font-bold text-amber-600' : 'font-semibold text-slate-800'}>
              {qualityAnalysis?.is_exposure_issue ? 'Issue Detected' : 'Normal'}
            </span>
          </div>
          {qualityAnalysis?.blur_score !== undefined && (
            <div>
              <span className="text-slate-500">Blur Score: </span>
              <span className="font-mono font-semibold text-slate-800">
                {qualityAnalysis.blur_score.toFixed(1)}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
