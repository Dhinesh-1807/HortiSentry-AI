import React, { useEffect, useState } from 'react';
import {
  Users,
  Search,
  Filter,
  ShieldCheck,
  UserCheck,
  Lock,
  Unlock,
  AlertCircle,
  CheckCircle2,
  ArrowLeft,
  Clock,
  XCircle,
  Check,
  RefreshCw,
  Award,
  AlertTriangle
} from 'lucide-react';
import {
  fetchAdminUsers,
  toggleUserStatus,
  fetchExpertVerifications,
  updateExpertVerificationStatus
} from '../../services/api';
import { AdminUserItem, ExpertVerificationItem } from '../../types';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface UserManagementProps {
  onNavigate: (route: string) => void;
}

export const UserManagement: React.FC<UserManagementProps> = ({ onNavigate }) => {
  const [activeTab, setActiveTab] = useState<'members' | 'verifications'>('members');
  const [users, setUsers] = useState<AdminUserItem[]>([]);
  const [experts, setExperts] = useState<ExpertVerificationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Filters for Members Tab
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Filters for Expert Verifications Tab
  const [verificationFilter, setVerificationFilter] = useState<string>('ALL');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [usersData, expertsData] = await Promise.all([
        fetchAdminUsers(),
        fetchExpertVerifications()
      ]);
      setUsers(Array.isArray(usersData) ? usersData : usersData.users || []);
      setExperts(Array.isArray(expertsData) ? expertsData : []);
    } catch (err: any) {
      setError(err.message || 'Failed to load user directory and verifications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleStatus = async (user: AdminUserItem) => {
    setActionLoading(user.id);
    setFeedback(null);
    try {
      await toggleUserStatus(user.id);
      setUsers((prev) =>
        prev.map((u) => (u.id === user.id ? { ...u, is_active: !u.is_active } : u))
      );
      setFeedback({
        type: 'success',
        message: `Account for ${user.full_name || user.name || user.email} updated successfully.`
      });
    } catch (err: any) {
      setFeedback({
        type: 'error',
        message: `Could not change status: ${err.message}`
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleVerifyExpert = async (
    expertId: string,
    action: 'APPROVE' | 'REJECT' | 'SUSPEND'
  ) => {
    setActionLoading(expertId);
    setFeedback(null);
    try {
      const result = await updateExpertVerificationStatus(expertId, action);

      // Update experts list locally
      setExperts((prev) =>
        prev.map((exp) => {
          if (exp.id === expertId) {
            return {
              ...exp,
              verification_status: result.verification_status,
              account_status: result.account_status,
              is_active: result.account_status === 'ACTIVE'
            };
          }
          return exp;
        })
      );

      // Also sync users list
      setUsers((prev) =>
        prev.map((u) => {
          if (u.id === expertId) {
            return {
              ...u,
              verification_status: result.verification_status,
              account_status: result.account_status,
              is_active: result.account_status === 'ACTIVE'
            };
          }
          return u;
        })
      );

      const actionText =
        action === 'APPROVE' ? 'approved' : action === 'REJECT' ? 'rejected' : 'suspended';
      setFeedback({
        type: 'success',
        message: `Expert ${actionText} successfully. System access updated.`
      });
    } catch (err: any) {
      setFeedback({
        type: 'error',
        message: err.message || `Failed to update verification status.`
      });
    } finally {
      setActionLoading(null);
    }
  };

  const pendingCount = experts.filter(
    (e) => (e.verification_status || '').toUpperCase() === 'PENDING'
  ).length;

  const filteredUsers = users.filter((u) => {
    if (roleFilter !== 'ALL' && u.role.toLowerCase() !== roleFilter.toLowerCase()) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchName = (u.full_name || u.name || '').toLowerCase().includes(q);
      const matchEmail = u.email.toLowerCase().includes(q);
      const matchCode = u.farmer_code?.toLowerCase().includes(q);
      return matchName || matchEmail || matchCode;
    }
    return true;
  });

  const filteredExperts = experts.filter((exp) => {
    if (verificationFilter !== 'ALL') {
      return (exp.verification_status || '').toUpperCase() === verificationFilter.toUpperCase();
    }
    return true;
  });

  const renderVerificationBadge = (status?: string) => {
    const s = (status || 'NOT_REQUIRED').toUpperCase();
    switch (s) {
      case 'VERIFIED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-bold text-[11px] bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
            VERIFIED
          </span>
        );
      case 'PENDING':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-bold text-[11px] bg-amber-100 text-amber-800 border border-amber-300">
            <Clock className="w-3 h-3 text-amber-600" />
            PENDING
          </span>
        );
      case 'REJECTED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-bold text-[11px] bg-rose-100 text-rose-800 border border-rose-300">
            <XCircle className="w-3 h-3 text-rose-600" />
            REJECTED
          </span>
        );
      case 'SUSPENDED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-bold text-[11px] bg-red-100 text-red-800 border border-red-300">
            <AlertTriangle className="w-3 h-3 text-red-600" />
            SUSPENDED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-500">
            NOT REQUIRED
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 py-2">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <button
            onClick={() => onNavigate('/admin')}
            className="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-slate-800"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Admin Dashboard</span>
          </button>
          <h1 className="text-2xl font-extrabold text-[#1F2937] tracking-tight">
            User & Role Management
          </h1>
          <p className="text-xs text-slate-500">
            Audit cooperative members, certify horticultural expert credentials, and control platform access
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold bg-white text-slate-700 border border-slate-200 rounded-xl hover:bg-slate-50 shadow-xs self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-[#2E7D32] ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Action feedback message */}
      {feedback && (
        <div
          className={`p-3 rounded-xl text-xs font-bold flex items-center justify-between border ${
            feedback.type === 'success'
              ? 'bg-[#E8F5E9] text-[#1B5E20] border-[#C8E6C9]'
              : 'bg-rose-50 text-rose-800 border-rose-200'
          }`}
        >
          <span>{feedback.message}</span>
          <button
            onClick={() => setFeedback(null)}
            className="text-slate-400 hover:text-slate-600 text-sm font-black"
          >
            ✕
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('members')}
          className={`pb-3 px-4 text-xs font-extrabold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'members'
              ? 'border-[#2E7D32] text-[#1B5E20]'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>All Members & Roles ({users.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('verifications')}
          className={`pb-3 px-4 text-xs font-extrabold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'verifications'
              ? 'border-[#2E7D32] text-[#1B5E20]'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Award className="w-4 h-4" />
          <span>Expert Verifications</span>
          {pendingCount > 0 && (
            <span className="bg-amber-400 text-amber-950 font-black text-[10px] px-2 py-0.5 rounded-full shadow-xs animate-pulse">
              {pendingCount} PENDING
            </span>
          )}
        </button>
      </div>

      {/* TAB 1: ALL MEMBERS */}
      {activeTab === 'members' && (
        <div className="space-y-4">
          {/* Filter Toolbar */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row gap-3 items-center justify-between">
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search by name, email, or farmer code..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-[#2E7D32] focus:outline-none"
              />
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <span className="text-xs font-bold text-slate-500 whitespace-nowrap">Filter Role:</span>
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="p-2 rounded-xl border border-slate-300 text-xs font-semibold bg-white text-slate-800 focus:ring-2 focus:ring-[#2E7D32] focus:outline-none"
              >
                <option value="ALL">All Roles ({users.length})</option>
                <option value="farmer">
                  Farmers ({users.filter((u) => u.role.toLowerCase() === 'farmer').length})
                </option>
                <option value="expert">
                  Experts ({users.filter((u) => u.role.toLowerCase() === 'expert').length})
                </option>
                <option value="admin">
                  Coop Admins ({users.filter((u) => u.role.toLowerCase() === 'admin').length})
                </option>
              </select>
            </div>
          </div>

          {/* User Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            {loading ? (
              <div className="p-8">
                <LoadingSpinner message="Loading user directory..." />
              </div>
            ) : error ? (
              <div className="p-8 text-center text-rose-600 text-sm">{error}</div>
            ) : filteredUsers.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-sm">No matching users found.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#F8FAF8] text-slate-500 uppercase font-bold border-b border-slate-200">
                    <tr>
                      <th className="px-5 py-3.5">User</th>
                      <th className="px-5 py-3.5">Role</th>
                      <th className="px-5 py-3.5">Verification</th>
                      <th className="px-5 py-3.5">Farmer ID / Region</th>
                      <th className="px-5 py-3.5">Account Status</th>
                      <th className="px-5 py-3.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredUsers.map((u) => (
                      <tr key={u.id} className="hover:bg-[#F8FAF8]/80 transition-colors">
                        <td className="px-5 py-4">
                          <div className="font-bold text-slate-900">{u.full_name || u.name || 'Member'}</div>
                          <div className="text-slate-500 text-[11px]">{u.email}</div>
                        </td>
                        <td className="px-5 py-4">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full font-bold text-[11px] ${
                              u.role.toLowerCase() === 'admin'
                                ? 'bg-amber-100 text-amber-800'
                                : u.role.toLowerCase() === 'expert'
                                ? 'bg-indigo-100 text-indigo-800'
                                : 'bg-[#E8F5E9] text-[#1B5E20]'
                            }`}
                          >
                            {u.role.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-5 py-4">
                          {u.role.toLowerCase() === 'expert'
                            ? renderVerificationBadge(u.verification_status)
                            : (
                              <span className="text-[11px] text-slate-400 font-semibold">
                                Not Required
                              </span>
                            )}
                        </td>
                        <td className="px-5 py-4">
                          <div className="font-mono text-slate-700 font-semibold">
                            {u.farmer_code || '—'}
                          </div>
                          <div className="text-slate-400 text-[11px]">{u.location || 'Cooperative Area'}</div>
                        </td>
                        <td className="px-5 py-4">
                          {u.is_active ? (
                            <span className="inline-flex items-center gap-1 text-[#1B5E20] font-bold">
                              <CheckCircle2 className="w-3.5 h-3.5 text-[#2E7D32]" />
                              Active
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-rose-600 font-bold">
                              <AlertCircle className="w-3.5 h-3.5 text-rose-500" />
                              Suspended
                            </span>
                          )}
                        </td>
                        <td className="px-5 py-4 text-right">
                          <button
                            onClick={() => handleToggleStatus(u)}
                            disabled={actionLoading === u.id}
                            className={`text-xs font-bold px-3 py-1.5 rounded-lg border transition-all ${
                              u.is_active
                                ? 'border-rose-200 text-rose-700 hover:bg-rose-50'
                                : 'border-[#C8E6C9] text-[#1B5E20] hover:bg-[#E8F5E9]'
                            }`}
                          >
                            {actionLoading === u.id
                              ? 'Updating...'
                              : u.is_active
                              ? 'Suspend'
                              : 'Activate'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: EXPERT VERIFICATIONS */}
      {activeTab === 'verifications' && (
        <div className="space-y-4">
          {/* Sub-header info card */}
          <div className="bg-[#E8F5E9]/50 border border-[#C8E6C9] p-4 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-sm font-extrabold text-[#1B5E20]">
                Expert Verification & Credentialing Queue
              </h2>
              <p className="text-xs text-slate-600 mt-0.5">
                Review registered plant pathologists and agricultural officers. Unverified or pending experts cannot access the review queue or expert APIs.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-600">Filter Status:</span>
              <select
                value={verificationFilter}
                onChange={(e) => setVerificationFilter(e.target.value)}
                className="p-1.5 rounded-xl border border-slate-300 text-xs font-semibold bg-white text-slate-800 focus:ring-2 focus:ring-[#2E7D32] focus:outline-none"
              >
                <option value="ALL">All ({experts.length})</option>
                <option value="PENDING">
                  Pending ({experts.filter((e) => (e.verification_status || '').toUpperCase() === 'PENDING').length})
                </option>
                <option value="VERIFIED">
                  Verified ({experts.filter((e) => (e.verification_status || '').toUpperCase() === 'VERIFIED').length})
                </option>
                <option value="REJECTED">
                  Rejected ({experts.filter((e) => (e.verification_status || '').toUpperCase() === 'REJECTED').length})
                </option>
                <option value="SUSPENDED">
                  Suspended ({experts.filter((e) => (e.verification_status || '').toUpperCase() === 'SUSPENDED').length})
                </option>
              </select>
            </div>
          </div>

          {/* Expert Queue Cards / Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            {loading ? (
              <div className="p-8">
                <LoadingSpinner message="Loading expert verifications..." />
              </div>
            ) : filteredExperts.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-sm">
                No experts found matching the selected filter.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#F8FAF8] text-slate-500 uppercase font-bold border-b border-slate-200">
                    <tr>
                      <th className="px-5 py-3.5">Expert Name & Email</th>
                      <th className="px-5 py-3.5">Location / Affiliation</th>
                      <th className="px-5 py-3.5">Verification Status</th>
                      <th className="px-5 py-3.5">System Access</th>
                      <th className="px-5 py-3.5 text-right">Verification Decisions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredExperts.map((exp) => {
                      const vStatus = (exp.verification_status || 'PENDING').toUpperCase();
                      const isPending = vStatus === 'PENDING';
                      const isVerified = vStatus === 'VERIFIED';
                      const isRejected = vStatus === 'REJECTED';
                      const isSuspended = vStatus === 'SUSPENDED';

                      return (
                        <tr key={exp.id} className="hover:bg-[#F8FAF8]/80 transition-colors">
                          <td className="px-5 py-4">
                            <div className="font-bold text-slate-900">{exp.name || 'Horticulture Specialist'}</div>
                            <div className="text-slate-500 text-[11px]">{exp.email}</div>
                            {exp.phone && (
                              <div className="text-slate-400 text-[10px] mt-0.5">📞 {exp.phone}</div>
                            )}
                          </td>
                          <td className="px-5 py-4">
                            <div className="font-semibold text-slate-700">{exp.location || 'Agricultural Research Institute'}</div>
                            <div className="text-slate-400 text-[10px]">
                              Registered: {exp.created_at ? new Date(exp.created_at).toLocaleDateString() : '—'}
                            </div>
                          </td>
                          <td className="px-5 py-4">
                            {renderVerificationBadge(exp.verification_status)}
                          </td>
                          <td className="px-5 py-4">
                            {isVerified && exp.is_active ? (
                              <span className="inline-flex items-center gap-1 text-[#1B5E20] font-bold text-[11px]">
                                <CheckCircle2 className="w-3.5 h-3.5 text-[#2E7D32]" />
                                Full Expert Access
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-slate-500 font-medium text-[11px]">
                                <Lock className="w-3.5 h-3.5 text-slate-400" />
                                Access Denied (403)
                              </span>
                            )}
                          </td>
                          <td className="px-5 py-4 text-right">
                            <div className="inline-flex items-center justify-end gap-2">
                              {/* APPROVE BUTTON */}
                              {(!isVerified) && (
                                <button
                                  onClick={() => handleVerifyExpert(exp.id, 'APPROVE')}
                                  disabled={actionLoading === exp.id}
                                  className="inline-flex items-center gap-1 text-xs font-bold px-3 py-1.5 rounded-lg bg-[#2E7D32] hover:bg-[#1B5E20] text-white shadow-xs transition-all disabled:opacity-50"
                                >
                                  <Check className="w-3.5 h-3.5" />
                                  <span>{isSuspended || isRejected ? 'Re-Approve' : 'Approve'}</span>
                                </button>
                              )}

                              {/* REJECT BUTTON */}
                              {isPending && (
                                <button
                                  onClick={() => handleVerifyExpert(exp.id, 'REJECT')}
                                  disabled={actionLoading === exp.id}
                                  className="inline-flex items-center gap-1 text-xs font-bold px-3 py-1.5 rounded-lg border border-rose-300 text-rose-700 hover:bg-rose-50 transition-all disabled:opacity-50"
                                >
                                  <XCircle className="w-3.5 h-3.5 text-rose-500" />
                                  <span>Reject</span>
                                </button>
                              )}

                              {/* SUSPEND BUTTON */}
                              {isVerified && (
                                <button
                                  onClick={() => handleVerifyExpert(exp.id, 'SUSPEND')}
                                  disabled={actionLoading === exp.id}
                                  className="inline-flex items-center gap-1 text-xs font-bold px-3 py-1.5 rounded-lg border border-amber-300 text-amber-800 hover:bg-amber-50 transition-all disabled:opacity-50"
                                >
                                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                                  <span>Suspend</span>
                                </button>
                              )}
                            </div>
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
      )}
    </div>
  );
};
