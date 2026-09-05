import React, { useState, useEffect } from 'react';
import {
  Sprout,
  ShieldCheck,
  Bell,
  UserCheck,
  Settings,
  LogOut,
  ChevronDown,
  Menu,
  X,
  FileText,
  Clock,
  Layers,
  Activity,
  History,
  Info,
  CheckCircle2,
  AlertTriangle,
  Award,
  AlertCircle
} from 'lucide-react';
import { HealthStatus, UserRole, AuthUser, NotificationItem } from '../types';
import { fetchNotifications, markNotificationRead, markAllNotificationsRead } from '../services/api';

interface NavbarProps {
  currentRole: UserRole;
  currentRoute: string;
  onNavigate: (route: string) => void;
  onSelectRole: (role: UserRole) => void;
  health: HealthStatus | null;
  user: AuthUser | null;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentRole,
  currentRoute,
  onNavigate,
  onSelectRole,
  health,
  user,
  onLogout
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [notifDropdownOpen, setNotifDropdownOpen] = useState<boolean>(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);

  const loadNotifs = async () => {
    if (!user) return;
    try {
      const res = await fetchNotifications();
      setNotifications(res.items || []);
      setUnreadCount(res.unread_count || 0);
    } catch {
      // Ignore if offline or unauthorized
    }
  };

  useEffect(() => {
    loadNotifs();
    if (user) {
      const timer = setInterval(loadNotifs, 15000); // Polling every 15s
      return () => clearInterval(timer);
    }
  }, [user]);

  const handleMarkRead = async (id: string) => {
    try {
      await markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch {
      // pass
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch {
      // pass
    }
  };

  const userRole = (user?.role || '').toLowerCase();
  const vStatus = (user?.verification_status || 'NOT_REQUIRED').toUpperCase();
  const isExpertVerified = userRole === 'expert' && vStatus === 'VERIFIED';

  const renderRoleBadge = () => {
    if (!user) return null;

    if (userRole === 'admin') {
      return (
        <button
          onClick={() => onNavigate('/admin')}
          className="bg-amber-950/60 border border-amber-500/40 text-amber-200 text-xs font-extrabold px-3 py-1.5 rounded-xl flex items-center gap-1.5 shadow-xs transition-all hover:bg-amber-900/70"
          title="Authenticated Cooperative Admin"
        >
          <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
          <span>ADMIN</span>
        </button>
      );
    }

    if (userRole === 'expert') {
      switch (vStatus) {
        case 'VERIFIED':
          return (
            <button
              onClick={() => onNavigate('/expert')}
              className="bg-emerald-950/60 border border-emerald-400/50 text-emerald-200 text-xs font-extrabold px-3 py-1.5 rounded-xl flex items-center gap-1.5 shadow-xs transition-all hover:bg-emerald-900/70"
              title="Verified Agricultural Expert"
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>EXPERT • VERIFIED</span>
            </button>
          );
        case 'PENDING':
          return (
            <button
              onClick={() => onNavigate('/expert/status')}
              className="bg-amber-950/70 border border-amber-400/50 text-amber-200 text-xs font-extrabold px-3 py-1.5 rounded-xl flex items-center gap-1.5 shadow-xs transition-all hover:bg-amber-900/80 animate-pulse"
              title="Awaiting Administrator Verification"
            >
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>EXPERT • PENDING</span>
            </button>
          );
        case 'REJECTED':
          return (
            <button
              onClick={() => onNavigate('/expert/status')}
              className="bg-rose-950/70 border border-rose-400/50 text-rose-200 text-xs font-extrabold px-3 py-1.5 rounded-xl flex items-center gap-1.5 shadow-xs transition-all hover:bg-rose-900/80"
              title="Expert Registration Rejected"
            >
              <X className="w-3.5 h-3.5 text-rose-400" />
              <span>EXPERT • REJECTED</span>
            </button>
          );
        case 'SUSPENDED':
          return (
            <button
              onClick={() => onNavigate('/expert/status')}
              className="bg-red-950/70 border border-red-400/50 text-red-200 text-xs font-extrabold px-3 py-1.5 rounded-xl flex items-center gap-1.5 shadow-xs transition-all hover:bg-red-900/80"
              title="Expert Account Suspended"
            >
              <AlertCircle className="w-3.5 h-3.5 text-red-400" />
              <span>EXPERT • SUSPENDED</span>
            </button>
          );
        default:
          return (
            <button
              onClick={() => onNavigate('/expert/status')}
              className="bg-slate-800 border border-slate-600 text-slate-200 text-xs font-extrabold px-3 py-1.5 rounded-xl flex items-center gap-1.5 shadow-xs"
            >
              <Award className="w-3.5 h-3.5" />
              <span>EXPERT</span>
            </button>
          );
      }
    }

    // Default: Farmer
    return (
      <button
        onClick={() => onNavigate('/farmer')}
        className="bg-emerald-950/60 border border-emerald-400/40 text-emerald-200 text-xs font-extrabold px-3 py-1.5 rounded-xl flex items-center gap-1.5 shadow-xs transition-all hover:bg-emerald-900/70"
        title="Authenticated Farmer Portal"
      >
        <Sprout className="w-3.5 h-3.5 text-emerald-400" />
        <span>FARMER</span>
      </button>
    );
  };

  return (
    <header className="bg-[#1B5E20] text-white shadow-md sticky top-0 z-50 border-b border-[#2E7D32]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <button
            onClick={() => onNavigate(user ? (userRole === 'admin' ? '/admin' : userRole === 'expert' ? (isExpertVerified ? '/expert' : '/expert/status') : '/farmer') : '/')}
            className="flex items-center space-x-3 text-left focus:outline-none group"
          >
            <div className="bg-[#2E7D32] p-2 rounded-xl text-white group-hover:bg-emerald-600 transition-colors shadow-xs">
              <Sprout className="h-6 w-6 text-emerald-200" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight text-white">HortiSentry</span>
                {health && health.ml_mode === 'DEMO' && (
                  <span className="bg-amber-400/20 text-amber-200 border border-amber-400/40 text-[10px] px-1.5 py-0.2 rounded font-bold uppercase tracking-wide">
                    DEMO
                  </span>
                )}
              </div>
              <p className="text-[11px] text-emerald-200 hidden sm:block">
                Horticulture Observation & Escalation
              </p>
            </div>
          </button>

          {/* Desktop Navigation Links based on active authenticated user */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2 text-xs font-semibold">
            {!user && (
              <>
                <button
                  onClick={() => onNavigate('/')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Home
                </button>
                <button
                  onClick={() => onNavigate('/about')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/about' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  About
                </button>
                <button
                  onClick={() => onNavigate('/how-it-works')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/how-it-works' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  How It Works
                </button>
              </>
            )}

            {user && userRole === 'farmer' && (
              <>
                <button
                  onClick={() => onNavigate('/farmer')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/farmer' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => onNavigate('/farmer/observation/new')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/farmer/observation/new' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Report Symptom
                </button>
                <button
                  onClick={() => onNavigate('/farmer/observations')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/farmer/observations' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  My History
                </button>
                <button
                  onClick={() => onNavigate('/farmer/profile')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/farmer/profile' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Profile
                </button>
              </>
            )}

            {user && userRole === 'expert' && (
              <>
                {isExpertVerified ? (
                  <>
                    <button
                      onClick={() => onNavigate('/expert')}
                      className={`px-3 py-1.5 rounded-lg transition-colors ${
                        currentRoute === '/expert' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                      }`}
                    >
                      Reviewer Home
                    </button>
                    <button
                      onClick={() => onNavigate('/expert/queue')}
                      className={`px-3 py-1.5 rounded-lg transition-colors ${
                        currentRoute.startsWith('/expert/queue') || currentRoute.startsWith('/expert/cases')
                          ? 'bg-[#2E7D32] text-white'
                          : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                      }`}
                    >
                      Review Queue
                    </button>
                    <button
                      onClick={() => onNavigate('/expert/history')}
                      className={`px-3 py-1.5 rounded-lg transition-colors ${
                        currentRoute === '/expert/history' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                      }`}
                    >
                      Review History
                    </button>
                    <button
                      onClick={() => onNavigate('/expert/profile')}
                      className={`px-3 py-1.5 rounded-lg transition-colors ${
                        currentRoute === '/expert/profile' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                      }`}
                    >
                      Profile
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => onNavigate('/expert/status')}
                      className={`px-3 py-1.5 rounded-lg transition-colors ${
                        currentRoute === '/expert/status' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                      }`}
                    >
                      Verification Status
                    </button>
                    <button
                      onClick={() => onNavigate('/expert/profile')}
                      className={`px-3 py-1.5 rounded-lg transition-colors ${
                        currentRoute === '/expert/profile' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                      }`}
                    >
                      Profile
                    </button>
                  </>
                )}
              </>
            )}

            {user && userRole === 'admin' && (
              <>
                <button
                  onClick={() => onNavigate('/admin')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/admin' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => onNavigate('/admin/users')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/admin/users' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Users & Verifications
                </button>
                <button
                  onClick={() => onNavigate('/admin/crops')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/admin/crops' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Crops
                </button>
                <button
                  onClick={() => onNavigate('/admin/analytics')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/admin/analytics' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Analytics & SLA
                </button>
                <button
                  onClick={() => onNavigate('/admin/model')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/admin/model' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Model & Data
                </button>
                <button
                  onClick={() => onNavigate('/admin/audit-logs')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${
                    currentRoute === '/admin/audit-logs' ? 'bg-[#2E7D32] text-white' : 'text-emerald-100 hover:bg-[#2E7D32]/60'
                  }`}
                >
                  Audit
                </button>
              </>
            )}
          </nav>

          {/* Right Tools: Notification Bell, Authenticated Status Badge, User Sign In/Out */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            
            {/* Notification Bell Dropdown (When Logged In) */}
            {user && (
              <div className="relative">
                <button
                  onClick={() => setNotifDropdownOpen(!notifDropdownOpen)}
                  className="relative p-2 rounded-xl text-emerald-100 hover:bg-[#2E7D32] transition-colors focus:outline-none"
                  title="Notifications"
                >
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-amber-400 text-amber-950 font-black text-[10px] rounded-full flex items-center justify-center shadow-xs">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>

                {/* Notification Tray Modal */}
                {notifDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-2xl shadow-xl border border-slate-200 text-slate-800 py-3 z-50 overflow-hidden">
                    <div className="px-4 py-2 border-b border-slate-100 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-slate-900">Cooperative Alerts</span>
                        {unreadCount > 0 && (
                          <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                            {unreadCount} new
                          </span>
                        )}
                      </div>
                      {unreadCount > 0 && (
                        <button
                          onClick={handleMarkAllRead}
                          className="text-[11px] text-[#2E7D32] font-bold hover:underline"
                        >
                          Mark all read
                        </button>
                      )}
                    </div>

                    <div className="max-h-72 overflow-y-auto divide-y divide-slate-100">
                      {notifications.length === 0 ? (
                        <div className="py-6 text-center text-xs text-slate-400">
                          No notifications currently.
                        </div>
                      ) : (
                        notifications.slice(0, 8).map((n) => (
                          <div
                            key={n.id}
                            onClick={() => handleMarkRead(n.id)}
                            className={`p-3 text-xs cursor-pointer transition-colors ${
                              n.is_read ? 'bg-white opacity-70' : 'bg-[#E8F5E9]/40'
                            } hover:bg-[#E8F5E9]/70`}
                          >
                            <div className="flex items-start justify-between gap-2">
                              <span className="font-bold text-slate-900">{n.title}</span>
                              <span className="text-[10px] text-slate-400 whitespace-nowrap">
                                {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                            <p className="text-slate-600 text-[11px] mt-1 line-clamp-2">{n.message}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Authenticated Role Status Badge (replaces arbitrary switcher) */}
            {renderRoleBadge()}

            {/* User Info (when logged in) */}
            {user && (
              <div className="hidden lg:flex flex-col text-right pr-1">
                <span className="text-xs font-bold text-white truncate max-w-[130px]">
                  {user.full_name || user.name || user.email}
                </span>
                <span className="text-[10px] text-emerald-200 truncate max-w-[130px]">
                  {user.email}
                </span>
              </div>
            )}

            {/* Auth Sign In / Register / Logout button */}
            {user ? (
              <button
                onClick={onLogout}
                className="p-2 rounded-xl text-emerald-200 hover:text-white hover:bg-[#2E7D32] transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onNavigate('/login')}
                  className="bg-white hover:bg-emerald-50 text-[#1B5E20] text-xs font-bold px-3 py-1.5 rounded-xl shadow-xs transition-all"
                >
                  Sign In
                </button>
                <button
                  onClick={() => onNavigate('/register')}
                  className="bg-[#2E7D32] hover:bg-emerald-600 border border-emerald-400/40 text-white text-xs font-bold px-3 py-1.5 rounded-xl shadow-xs transition-all hidden sm:inline-block"
                >
                  Register
                </button>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl text-emerald-100 hover:bg-[#2E7D32]"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer (Only authorized links shown) */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#144A18] px-4 pt-2 pb-4 space-y-1 text-xs border-t border-[#2E7D32]">
          {!user ? (
            <>
              <button
                onClick={() => { onNavigate('/'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                Public Home
              </button>
              <button
                onClick={() => { onNavigate('/about'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                About
              </button>
              <button
                onClick={() => { onNavigate('/how-it-works'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                How It Works
              </button>
              <button
                onClick={() => { onNavigate('/login'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white font-bold"
              >
                Sign In
              </button>
              <button
                onClick={() => { onNavigate('/register'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white font-bold"
              >
                Register
              </button>
            </>
          ) : userRole === 'farmer' ? (
            <>
              <button
                onClick={() => { onNavigate('/farmer'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white font-bold"
              >
                Farmer Dashboard
              </button>
              <button
                onClick={() => { onNavigate('/farmer/observation/new'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                Report Symptom
              </button>
              <button
                onClick={() => { onNavigate('/farmer/observations'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                My History
              </button>
              <button
                onClick={() => { onNavigate('/farmer/profile'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                Profile
              </button>
            </>
          ) : userRole === 'expert' ? (
            <>
              {isExpertVerified ? (
                <>
                  <button
                    onClick={() => { onNavigate('/expert'); setMobileMenuOpen(false); }}
                    className="block w-full text-left py-2 text-emerald-100 hover:text-white font-bold"
                  >
                    Expert Home
                  </button>
                  <button
                    onClick={() => { onNavigate('/expert/queue'); setMobileMenuOpen(false); }}
                    className="block w-full text-left py-2 text-emerald-100 hover:text-white"
                  >
                    Review Queue
                  </button>
                  <button
                    onClick={() => { onNavigate('/expert/history'); setMobileMenuOpen(false); }}
                    className="block w-full text-left py-2 text-emerald-100 hover:text-white"
                  >
                    Review History
                  </button>
                </>
              ) : (
                <button
                  onClick={() => { onNavigate('/expert/status'); setMobileMenuOpen(false); }}
                  className="block w-full text-left py-2 text-amber-200 hover:text-white font-bold"
                >
                  Verification Status ({vStatus})
                </button>
              )}
              <button
                onClick={() => { onNavigate('/expert/profile'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                Profile
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => { onNavigate('/admin'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white font-bold"
              >
                Admin Dashboard
              </button>
              <button
                onClick={() => { onNavigate('/admin/users'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                Users & Verifications
              </button>
              <button
                onClick={() => { onNavigate('/admin/crops'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                Crop Management
              </button>
              <button
                onClick={() => { onNavigate('/admin/analytics'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                Analytics & SLA
              </button>
              <button
                onClick={() => { onNavigate('/admin/model'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                Model & Data
              </button>
              <button
                onClick={() => { onNavigate('/admin/audit-logs'); setMobileMenuOpen(false); }}
                className="block w-full text-left py-2 text-emerald-100 hover:text-white"
              >
                Audit Logs
              </button>
            </>
          )}

          {user && (
            <button
              onClick={() => { onLogout(); setMobileMenuOpen(false); }}
              className="block w-full text-left py-2 text-rose-300 hover:text-rose-100 font-bold border-t border-[#2E7D32]/50 mt-2"
            >
              Sign Out
            </button>
          )}
        </div>
      )}
    </header>
  );
};
