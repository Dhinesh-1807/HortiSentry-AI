import React from 'react';
import {
  ShieldAlert,
  Clock,
  AlertTriangle,
  LogOut,
  HelpCircle,
  CheckCircle2,
  Mail,
  Home
} from 'lucide-react';
import { AuthUser } from '../../types';

interface ExpertStatusPageProps {
  user: AuthUser | null;
  statusOverride?: string;
  onNavigate: (route: string) => void;
  onLogout: () => void;
}

export const ExpertStatusPage: React.FC<ExpertStatusPageProps> = ({
  user,
  statusOverride,
  onNavigate,
  onLogout
}) => {
  const currentStatus = (statusOverride || user?.verification_status || 'PENDING').toUpperCase();

  const isPending = currentStatus === 'PENDING';
  const isRejected = currentStatus === 'REJECTED';
  const isSuspended = currentStatus === 'SUSPENDED';

  // Exact required status messages
  const statusConfig = {
    PENDING: {
      badge: 'EXPERT • PENDING',
      badgeColor: 'bg-amber-100 text-amber-900 border-amber-300',
      icon: Clock,
      iconBg: 'bg-amber-50 text-amber-600 border-amber-200',
      title: 'Verification In Progress',
      message: 'Your expert account is awaiting verification by the administrator.',
      subtext: 'To maintain diagnostic integrity across the cooperative surveillance network, all agricultural experts are vetted by cooperative management before access to active observation queues is granted.'
    },
    REJECTED: {
      badge: 'EXPERT • REJECTED',
      badgeColor: 'bg-rose-100 text-rose-900 border-rose-300',
      icon: AlertTriangle,
      iconBg: 'bg-rose-50 text-rose-600 border-rose-200',
      title: 'Registration Not Approved',
      message: 'Your expert registration was not approved. Please contact the administrator.',
      subtext: 'The cooperative administration was unable to verify your agricultural accreditation or regional assignment. If you believe this is in error, please reach out to your cooperative coordinator.'
    },
    SUSPENDED: {
      badge: 'EXPERT • SUSPENDED',
      badgeColor: 'bg-slate-200 text-slate-800 border-slate-300',
      icon: ShieldAlert,
      iconBg: 'bg-slate-100 text-slate-700 border-slate-300',
      title: 'Expert Account Suspended',
      message: 'Your expert account has been suspended. Please contact the administrator.',
      subtext: 'Access to the Expert Diagnostic Portal and priority observation queue is temporarily suspended. Please contact cooperative headquarters for compliance review and reinstatement.'
    }
  };

  const activeConfig = statusConfig[currentStatus as keyof typeof statusConfig] || statusConfig.PENDING;
  const StatusIcon = activeConfig.icon;

  return (
    <div className="max-w-xl mx-auto py-10 px-4 space-y-6">
      {/* Status Card */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6 text-center">
        
        {/* Status Badge */}
        <div className="flex justify-center">
          <span
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-black tracking-wider uppercase border shadow-xs ${activeConfig.badgeColor}`}
          >
            <span className="w-2 h-2 rounded-full bg-current animate-pulse"></span>
            {activeConfig.badge}
          </span>
        </div>

        {/* Big Icon */}
        <div className="flex justify-center">
          <div className={`p-4 rounded-2xl border ${activeConfig.iconBg}`}>
            <StatusIcon className="w-10 h-10" />
          </div>
        </div>

        {/* Main Heading & Message */}
        <div className="space-y-2 max-w-md mx-auto">
          <h1 className="text-xl sm:text-2xl font-extrabold text-[#1F2937]">
            {activeConfig.title}
          </h1>
          <p className="text-sm font-semibold text-slate-800 bg-slate-50 border border-slate-200 rounded-xl p-3">
            "{activeConfig.message}"
          </p>
          <p className="text-xs text-slate-500 leading-relaxed pt-1">
            {activeConfig.subtext}
          </p>
        </div>

        {/* User Details Summary */}
        {user && (
          <div className="bg-[#F8FAF8] border border-slate-200 rounded-2xl p-4 text-left space-y-2 text-xs">
            <div className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">
              Registered Expert Account
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-600">
              <div>
                <span className="text-slate-400">Name: </span>
                <span className="font-semibold text-slate-900">{user.name || user.full_name || 'Expert Member'}</span>
              </div>
              <div>
                <span className="text-slate-400">Email: </span>
                <span className="font-semibold text-slate-900">{user.email}</span>
              </div>
              {user.location && (
                <div className="sm:col-span-2">
                  <span className="text-slate-400">Affiliation / Region: </span>
                  <span className="font-semibold text-slate-900">{user.location}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* What Happens Next Card */}
        <div className="bg-[#E8F5E9]/50 border border-[#C8E6C9] rounded-2xl p-4 text-left space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-[#1B5E20]">
            <HelpCircle className="w-4 h-4 text-[#2E7D32]" />
            <span>Cooperative Governance & Protocols</span>
          </div>
          <p className="text-xs text-[#1F2937]/80 leading-relaxed">
            {isPending &&
              'An authorized cooperative manager reviews expert credentials and assigns target crop domains (e.g. Solanaceae, Cucurbits). You will receive full access once approved.'}
            {isRejected &&
              'Please verify that your registered email corresponds to your accredited research or extension organisation.'}
            {isSuspended &&
              'For security and audit trails, all past diagnoses submitted under this profile remain preserved.'}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={onLogout}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
          >
            <LogOut className="w-4 h-4 text-slate-500" />
            <span>Sign Out / Switch Account</span>
          </button>
          <button
            onClick={() => onNavigate('/')}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-[#2E7D32] hover:bg-[#1B5E20] text-xs font-bold text-white transition-colors shadow-xs"
          >
            <Home className="w-4 h-4" />
            <span>Return to HortiSentry Home</span>
          </button>
        </div>
      </div>
    </div>
  );
};
