import React from 'react';
import { LucideIcon } from 'lucide-react';

interface DashboardStatCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  colorScheme?: 'emerald' | 'amber' | 'blue' | 'rose' | 'slate';
  description?: string;
  onClick?: () => void;
}

export const DashboardStatCard: React.FC<DashboardStatCardProps> = ({
  title,
  value,
  icon: Icon,
  colorScheme = 'emerald',
  description,
  onClick,
}) => {
  let colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  let iconBg = 'bg-emerald-100 text-emerald-800';

  switch (colorScheme) {
    case 'amber':
      colorClasses = 'bg-amber-50/80 text-amber-900 border-amber-200';
      iconBg = 'bg-amber-100 text-amber-800';
      break;
    case 'blue':
      colorClasses = 'bg-blue-50/80 text-blue-900 border-blue-200';
      iconBg = 'bg-blue-100 text-blue-800';
      break;
    case 'rose':
      colorClasses = 'bg-rose-50/80 text-rose-900 border-rose-200';
      iconBg = 'bg-rose-100 text-rose-800';
      break;
    case 'slate':
      colorClasses = 'bg-slate-50 text-slate-800 border-slate-200';
      iconBg = 'bg-slate-200 text-slate-700';
      break;
  }

  return (
    <div
      onClick={onClick}
      className={`p-5 rounded-2xl border ${colorClasses} transition-all shadow-sm ${
        onClick ? 'cursor-pointer hover:shadow-md hover:scale-[1.01]' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-1">
            {title}
          </span>
          <span className="text-3xl font-black text-slate-900 tracking-tight">{value}</span>
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${iconBg}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      {description && <p className="text-xs text-slate-500 mt-2 font-medium">{description}</p>}
    </div>
  );
};
