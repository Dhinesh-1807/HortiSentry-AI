import React, { useState, useMemo, useRef, useEffect } from 'react';
import {
  ShieldCheck,
  UserPlus,
  User,
  Mail,
  Phone,
  MapPin,
  Lock,
  AlertCircle,
  CheckCircle2,
  Award,
  ChevronDown,
  Search
} from 'lucide-react';
import { authRegister } from '../../services/api';

interface RegisterPageProps {
  onNavigate: (route: string) => void;
  onRegisterSuccess?: (user: any) => void;
}

// Comprehensive Horticultural Districts Directory (Tamil Nadu + Major States)
export const DISTRICT_LIST: { district: string; state: string }[] = [
  // Tamil Nadu (All 38 Districts)
  { district: 'Ariyalur', state: 'Tamil Nadu' },
  { district: 'Chengalpattu', state: 'Tamil Nadu' },
  { district: 'Chennai', state: 'Tamil Nadu' },
  { district: 'Coimbatore', state: 'Tamil Nadu' },
  { district: 'Cuddalore', state: 'Tamil Nadu' },
  { district: 'Dharmapuri', state: 'Tamil Nadu' },
  { district: 'Dindigul', state: 'Tamil Nadu' },
  { district: 'Erode', state: 'Tamil Nadu' },
  { district: 'Kallakurichi', state: 'Tamil Nadu' },
  { district: 'Kanchipuram', state: 'Tamil Nadu' },
  { district: 'Kanyakumari', state: 'Tamil Nadu' },
  { district: 'Karur', state: 'Tamil Nadu' },
  { district: 'Krishnagiri', state: 'Tamil Nadu' },
  { district: 'Madurai', state: 'Tamil Nadu' },
  { district: 'Mayiladuthurai', state: 'Tamil Nadu' },
  { district: 'Nagapattinam', state: 'Tamil Nadu' },
  { district: 'Namakkal', state: 'Tamil Nadu' },
  { district: 'Nilgiris', state: 'Tamil Nadu' },
  { district: 'Perambalur', state: 'Tamil Nadu' },
  { district: 'Pudukkottai', state: 'Tamil Nadu' },
  { district: 'Ramanathapuram', state: 'Tamil Nadu' },
  { district: 'Ranipet', state: 'Tamil Nadu' },
  { district: 'Salem', state: 'Tamil Nadu' },
  { district: 'Sivaganga', state: 'Tamil Nadu' },
  { district: 'Tenkasi', state: 'Tamil Nadu' },
  { district: 'Thanjavur', state: 'Tamil Nadu' },
  { district: 'Theni', state: 'Tamil Nadu' },
  { district: 'Thoothukudi', state: 'Tamil Nadu' },
  { district: 'Tiruchirappalli', state: 'Tamil Nadu' },
  { district: 'Tirunelveli', state: 'Tamil Nadu' },
  { district: 'Tirupathur', state: 'Tamil Nadu' },
  { district: 'Tiruppur', state: 'Tamil Nadu' },
  { district: 'Tiruvallur', state: 'Tamil Nadu' },
  { district: 'Tiruvannamalai', state: 'Tamil Nadu' },
  { district: 'Tiruvarur', state: 'Tamil Nadu' },
  { district: 'Vellore', state: 'Tamil Nadu' },
  { district: 'Viluppuram', state: 'Tamil Nadu' },
  { district: 'Virudhunagar', state: 'Tamil Nadu' },

  // Karnataka
  { district: 'Bengaluru Rural', state: 'Karnataka' },
  { district: 'Bengaluru Urban', state: 'Karnataka' },
  { district: 'Belagavi', state: 'Karnataka' },
  { district: 'Chikkaballapur', state: 'Karnataka' },
  { district: 'Chikkamagaluru', state: 'Karnataka' },
  { district: 'Hassan', state: 'Karnataka' },
  { district: 'Kolar', state: 'Karnataka' },
  { district: 'Mandya', state: 'Karnataka' },
  { district: 'Mysuru', state: 'Karnataka' },
  { district: 'Shimoga (Shivamogga)', state: 'Karnataka' },
  { district: 'Tumakuru', state: 'Karnataka' },

  // Maharashtra
  { district: 'Ahmednagar', state: 'Maharashtra' },
  { district: 'Jalgaon', state: 'Maharashtra' },
  { district: 'Kolhapur', state: 'Maharashtra' },
  { district: 'Nagpur', state: 'Maharashtra' },
  { district: 'Nashik', state: 'Maharashtra' },
  { district: 'Pune', state: 'Maharashtra' },
  { district: 'Sangli', state: 'Maharashtra' },
  { district: 'Satara', state: 'Maharashtra' },
  { district: 'Solapur', state: 'Maharashtra' },

  // Andhra Pradesh
  { district: 'Anantapur', state: 'Andhra Pradesh' },
  { district: 'Chittoor', state: 'Andhra Pradesh' },
  { district: 'Guntur', state: 'Andhra Pradesh' },
  { district: 'Krishna', state: 'Andhra Pradesh' },
  { district: 'Kurnool', state: 'Andhra Pradesh' },

  // Kerala
  { district: 'Idukki', state: 'Kerala' },
  { district: 'Palakkad', state: 'Kerala' },
  { district: 'Wayanad', state: 'Kerala' },

  // Himachal Pradesh
  { district: 'Kinnaur', state: 'Himachal Pradesh' },
  { district: 'Kullu', state: 'Himachal Pradesh' },
  { district: 'Shimla', state: 'Himachal Pradesh' },
  { district: 'Solan', state: 'Himachal Pradesh' }
];

export const RegisterPage: React.FC<RegisterPageProps> = ({ onNavigate }) => {
  const [selectedRole, setSelectedRole] = useState<'farmer' | 'expert'>('farmer');
  const [fullName, setFullName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [phone, setPhone] = useState<string>('');
  const [location, setLocation] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // District autocomplete suggestions state
  const [showSuggestions, setShowSuggestions] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Compute matched districts based on typed text
  const matchingDistricts = useMemo(() => {
    const q = location.trim().toLowerCase();
    if (!q) {
      return DISTRICT_LIST.slice(0, 8);
    }
    return DISTRICT_LIST.filter(
      (item) =>
        item.district.toLowerCase().includes(q) ||
        item.state.toLowerCase().includes(q)
    ).slice(0, 10);
  }, [location]);

  // Click outside listener to dismiss suggestions
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectDistrict = (district: string, state: string) => {
    setLocation(`${district}, ${state}`);
    setShowSuggestions(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await authRegister({
        name: fullName,
        email,
        phone,
        location,
        password,
        role: selectedRole.toUpperCase()
      });

      // Show message and redirect to Login without auto-login
      const message = res?.message || 'Registration successful! Please sign in with your new account.';
      setSuccessMessage(message);
      sessionStorage.setItem('hortisentry_reg_msg', message);

      setTimeout(() => {
        onNavigate('/login?registered=1');
      }, 1200);
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please check the details and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-8 space-y-6">
      {/* Brand Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 rounded-2xl bg-[#E8F5E9] text-[#1B5E20] border border-[#C8E6C9] mb-1">
          <UserPlus className="w-8 h-8 text-[#2E7D32]" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1F2937]">
          {selectedRole === 'farmer' ? 'Farmer Registration' : 'Agricultural Expert Registration'}
        </h1>
        <p className="text-xs sm:text-sm text-slate-500">
          {selectedRole === 'farmer'
            ? "Join your horticulture cooperative's rapid disease surveillance network"
            : 'Register to provide authoritative diagnosis & recommendations to cooperative farmers'}
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm space-y-5">
        {/* Role Switch Tabs */}
        <div className="flex rounded-xl bg-slate-100 p-1">
          <button
            type="button"
            onClick={() => setSelectedRole('farmer')}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              selectedRole === 'farmer'
                ? 'bg-white text-[#1B5E20] shadow-xs'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <User className="w-3.5 h-3.5" />
            <span>Farmer</span>
          </button>
          <button
            type="button"
            onClick={() => setSelectedRole('expert')}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              selectedRole === 'expert'
                ? 'bg-white text-indigo-800 shadow-xs'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <Award className="w-3.5 h-3.5" />
            <span>Agricultural Expert</span>
          </button>
        </div>

        {successMessage && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3.5 flex items-start gap-2.5 text-xs text-emerald-900 animate-fadeIn">
            <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">{successMessage}</p>
              <p className="text-[11px] text-emerald-700 mt-0.5">Redirecting to Login page...</p>
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
          {/* Full Name field with clean neutral placeholder */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Full Name</label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your full name"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#2E7D32] focus:border-[#2E7D32]"
              />
            </div>
          </div>

          {/* Email Address field with clean neutral placeholder */}
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

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Phone Number</label>
              <div className="relative">
                <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="10-digit mobile number"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#2E7D32] focus:border-[#2E7D32]"
                />
              </div>
            </div>

            {/* District with Auto-Suggest While Typing */}
            <div className="space-y-1 relative" ref={dropdownRef}>
              <label className="text-xs font-bold text-slate-700 flex items-center justify-between">
                <span>District</span>
                <span className="text-[10px] text-slate-400 font-normal">Type to suggest</span>
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  required
                  list="hortisentry-districts"
                  value={location}
                  onFocus={() => setShowSuggestions(true)}
                  onChange={(e) => {
                    setLocation(e.target.value);
                    setShowSuggestions(true);
                  }}
                  placeholder="Type district name..."
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#2E7D32] focus:border-[#2E7D32]"
                />
              </div>

              {/* Native datalist for quick browser auto-completion */}
              <datalist id="hortisentry-districts">
                {DISTRICT_LIST.map((item) => (
                  <option key={`${item.district}-${item.state}`} value={`${item.district}, ${item.state}`} />
                ))}
              </datalist>

              {/* Interactive Autocomplete Suggestions Dropdown */}
              {showSuggestions && matchingDistricts.length > 0 && (
                <div className="absolute left-0 right-0 top-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-30 max-h-52 overflow-y-auto divide-y divide-slate-100">
                  <div className="px-3 py-1.5 bg-[#F8FAF8] text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                    <span>Suggested Districts</span>
                    <span>{matchingDistricts.length} matches</span>
                  </div>
                  {matchingDistricts.map((item) => (
                    <button
                      key={`${item.district}-${item.state}`}
                      type="button"
                      onMouseDown={(e) => {
                        e.preventDefault(); // Prevent input blur before selection
                        handleSelectDistrict(item.district, item.state);
                      }}
                      className="w-full px-3.5 py-2 text-left text-xs hover:bg-[#E8F5E9] transition-colors flex items-center justify-between group"
                    >
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-[#2E7D32] opacity-70 group-hover:opacity-100" />
                        <span className="font-bold text-slate-800 group-hover:text-[#1B5E20]">
                          {item.district}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400 font-medium group-hover:text-slate-600">
                        {item.state}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 6 characters"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#2E7D32] focus:border-[#2E7D32]"
              />
            </div>
          </div>

          {selectedRole === 'farmer' ? (
            <div className="p-3 bg-[#F8FAF8] border border-slate-200/80 rounded-xl text-xs text-slate-600 flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2E7D32] flex-shrink-0 mt-0.5" />
              <span>
                A unique anonymous identifier (e.g. <code>HS-FARMER-XXXX</code>) will be generated for privacy-preserving cooperative escalations.
              </span>
            </div>
          ) : (
            <div className="p-3 bg-amber-50 border border-amber-200/80 rounded-xl text-xs text-amber-900 flex items-start gap-2">
              <ShieldCheck className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
              <span>
                Expert accounts require verification by the cooperative administrator before diagnostic queue access is activated.
              </span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !!successMessage}
            className="w-full bg-[#2E7D32] hover:bg-[#1B5E20] text-white font-bold py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 text-sm disabled:opacity-50"
          >
            <UserPlus className="w-4 h-4" />
            <span>
              {loading
                ? 'Creating Account...'
                : selectedRole === 'farmer'
                ? 'Complete Farmer Registration'
                : 'Register as Agricultural Expert'}
            </span>
          </button>
        </form>

        <div className="pt-2 border-t border-slate-100 text-center text-xs text-slate-500">
          <span>Already have an account? </span>
          <button
            type="button"
            onClick={() => onNavigate('/login')}
            className="font-bold text-[#2E7D32] hover:underline"
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
};
