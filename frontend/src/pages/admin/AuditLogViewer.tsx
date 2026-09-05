import React, { useEffect, useState } from 'react';
import { History, Search, ArrowLeft, ShieldCheck, FileText, CheckCircle2, Clock } from 'lucide-react';
import { fetchAdminAuditLogs } from '../../services/api';
import { AuditLogItem } from '../../types';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface AuditLogViewerProps {
  onNavigate: (route: string) => void;
}

export const AuditLogViewer: React.FC<AuditLogViewerProps> = ({ onNavigate }) => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [actionFilter, setActionFilter] = useState<string>('ALL');

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const data = await fetchAdminAuditLogs();
        setLogs(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load audit trail');
      } finally {
        setLoading(false);
      }
    };
    loadLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    if (actionFilter !== 'ALL' && log.action !== actionFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchAction = log.action.toLowerCase().includes(q);
      const matchEntity = (log.entity_type || '').toLowerCase().includes(q);
      const matchId = (log.entity_id || '').toLowerCase().includes(q);
      const matchDetails = typeof log.details === 'string' ? log.details.toLowerCase().includes(q) : false;
      return matchAction || matchEntity || matchId || matchDetails;
    }
    return true;
  });

  const uniqueActions = Array.from(new Set(logs.map((l) => l.action)));

  return (
    <div className="space-y-6 py-2">
      {/* Top Bar */}
      <div className="space-y-1">
        <button
          onClick={() => onNavigate('/admin')}
          className="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-slate-800"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Dashboard</span>
        </button>
        <h1 className="text-2xl font-extrabold text-[#1F2937] tracking-tight">
          Cooperative Compliance Audit Trail
        </h1>
        <p className="text-xs text-slate-500">
          Immutable audit record of all observation submissions, AI screening triggers, and expert review overrides
        </p>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by action, entity ID, or details..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-[#2E7D32]"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs font-bold text-slate-500 whitespace-nowrap">Filter Action:</span>
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="p-2 rounded-xl border border-slate-300 text-xs font-semibold bg-white text-slate-800 focus:ring-2 focus:ring-[#2E7D32]"
          >
            <option value="ALL">All Actions ({logs.length})</option>
            {uniqueActions.map((act) => (
              <option key={act} value={act}>
                {act}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-8"><LoadingSpinner message="Loading audit trail..." /></div>
        ) : error ? (
          <div className="p-8 text-center text-rose-600 text-sm">{error}</div>
        ) : filteredLogs.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">No audit logs recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F8FAF8] text-slate-500 uppercase font-bold border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3.5">Timestamp</th>
                  <th className="px-5 py-3.5">Action Event</th>
                  <th className="px-5 py-3.5">Target Entity</th>
                  <th className="px-5 py-3.5">Entity ID</th>
                  <th className="px-5 py-3.5">Audit Context / Payload</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-[#F8FAF8]/80 transition-colors">
                    <td className="px-5 py-3.5 text-slate-500 whitespace-nowrap">
                      {new Date(log.created_at || log.timestamp || Date.now()).toLocaleString()}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="font-bold text-[#1B5E20] bg-[#E8F5E9] px-2 py-0.5 rounded border border-[#C8E6C9]">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-700 font-semibold uppercase">
                      {log.entity_type}
                    </td>
                    <td className="px-5 py-3.5 text-slate-600">
                      {log.entity_id ? log.entity_id.slice(0, 8) : '—'}
                    </td>
                    <td className="px-5 py-3.5 text-slate-500 font-sans max-w-xs truncate text-[11px]">
                      {log.details || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
