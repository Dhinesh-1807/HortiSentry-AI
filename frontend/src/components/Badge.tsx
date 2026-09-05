import React from 'react';

interface BadgeProps {
  status: string;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ status, className = '' }) => {
  const normStatus = status.toUpperCase();

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';
  let label = status;

  switch (normStatus) {
    case 'SUBMITTED':
      colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      label = 'Submitted';
      break;
    case 'PENDING':
    case 'PENDING_REVIEW':
    case 'RECOMMENDED':
      colorClasses = 'bg-amber-50 text-amber-700 border-amber-200';
      label = 'Expert Review Pending';
      break;
    case 'IN_PROGRESS':
    case 'UNDER_REVIEW':
      colorClasses = 'bg-blue-50 text-blue-700 border-blue-200';
      label = 'Under Expert Review';
      break;
    case 'COMPLETED':
    case 'RESOLVED':
    case 'REVIEWED':
      colorClasses = 'bg-emerald-100 text-emerald-800 border-emerald-300 font-semibold';
      label = 'Completed';
      break;
    case 'NEEDS_INFO':
      colorClasses = 'bg-purple-50 text-purple-700 border-purple-200';
      label = 'Needs Information';
      break;
    case 'DEMO':
    case 'DEMO MODE':
      colorClasses = 'bg-amber-100 text-amber-900 border-amber-300 font-bold';
      label = 'DEMO MODE';
      break;
    default:
      label = status;
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClasses} ${className}`}
    >
      {label}
    </span>
  );
};
