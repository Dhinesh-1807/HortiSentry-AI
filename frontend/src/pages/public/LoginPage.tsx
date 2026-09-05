import React, { useState, useEffect } from 'react';
import { ShieldCheck, LogIn, Lock, Mail, AlertCircle, CheckCircle2 } from 'lucide-react';
import { authLogin } from '../../services/api';

interface LoginPageProps {
  onNavigate: (route: string) => void;
  onLoginSuccess: (user: any) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onNavigate, onLoginSuccess }) => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [flashSuccess, setFlashSuccess] = useState<string | null>(null);

  useEffect(() => {
    const savedMsg = sessionStorage.getItem('hortisentry_reg_msg');
    if (savedMsg) {
      setFlashSuccess(savedMsg);
      sessionStorage.removeItem('hortisentry_reg_msg');
    }
  }, []);

  const redirectAfterLogin = (user: any) => {
    onLoginSuccess(user);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await authLogin({ email, password });
      redirectAfterLogin(res.user);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-8 space-y-6">
      {/* Brand Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 rounded-2xl bg-[#E8F5E9] text-[#1B5E20] border border-[#C8E6C9] mb-1">
          <ShieldCheck className="w-8 h-8 text-[#2E7D32]" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1F2937]">Sign In to HortiSentry</h1>
        <p className="text-xs sm:text-sm text-slate-500">
          Access the horticulture disease observation & escalation network
        </p>
      </div>

      {/* Form Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm space-y-5">
        {flashSuccess && (
          <div className="bg-[#E8F5E9] border border-[#C8E6C9] rounded-xl p-3.5 flex items-start gap-2.5 text-xs text-[#1B5E20]">
            <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">{flashSuccess}</p>
              <p className="text-[11px] text-slate-600 mt-0.5">Please sign in with your credentials to continue.</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-3 flex items-start gap-2.5 text-xs text-rose-800">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email address"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#2E7D32] focus:border-[#2E7D32]"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#2E7D32] focus:border-[#2E7D32]"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#2E7D32] hover:bg-[#1B5E20] text-white font-bold py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 text-sm disabled:opacity-50"
          >
            <LogIn className="w-4 h-4" />
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
          </button>
        </form>

        <div className="pt-2 border-t border-slate-100 text-center text-xs text-slate-500">
          <span>New to HortiSentry cooperative? </span>
          <button
            type="button"
            onClick={() => onNavigate('/register')}
            className="font-bold text-[#2E7D32] hover:underline"
          >
            Register as a Farmer
          </button>
        </div>
      </div>
    </div>
  );
};
