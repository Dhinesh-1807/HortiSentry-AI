import React from 'react';
import { AlertTriangle, Info, CheckCircle2, ShieldAlert } from 'lucide-react';

interface AlertProps {
  type?: 'info' | 'warning' | 'danger' | 'success' | 'demo';
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  className = '',
}) => {
  let containerStyles = 'bg-blue-50 border-blue-200 text-blue-800';
  let Icon = Info;

  switch (type) {
    case 'warning':
      containerStyles = 'bg-amber-50 border-amber-200 text-amber-900';
      Icon = AlertTriangle;
      break;
    case 'danger':
      containerStyles = 'bg-rose-50 border-rose-200 text-rose-900';
      Icon = ShieldAlert;
      break;
    case 'success':
      containerStyles = 'bg-emerald-50 border-emerald-200 text-emerald-900';
      Icon = CheckCircle2;
      break;
    case 'demo':
      containerStyles = 'bg-amber-100 border-amber-300 text-amber-950 font-medium';
      Icon = AlertTriangle;
      break;
  }

  return (
    <div className={`p-4 rounded-xl border flex items-start gap-3 ${containerStyles} ${className}`}>
      <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
      <div className="text-sm leading-relaxed">
        {title && <h4 className="font-semibold mb-0.5">{title}</h4>}
        <div>{children}</div>
      </div>
    </div>
  );
};
