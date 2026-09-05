import {
  HealthStatus,
  CropConfig,
  ObservationCreateResponse,
  ObservationListItem,
  ObservationDetail,
  ExpertDashboardStats,
  ExpertReviewQueueItem,
  ExpertReviewDetail
} from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchCrops(category?: string, search?: string): Promise<CropConfig[]> {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (search) params.append('search', search);

  const url = `${API_BASE}/crops${params.toString() ? `?${params.toString()}` : ''}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch crop configuration: ${response.status}`);
  }
  return response.json();
}

export async function createObservation(formData: FormData): Promise<ObservationCreateResponse> {
  const response = await fetch(`${API_BASE}/observations`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || `Failed to submit observation (${response.status})`);
  }
  return response.json();
}

export async function getAIReview(observationId: string, forceRefresh: boolean = false): Promise<any> {
  const response = await fetch(`${API_BASE}/ai-review`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ observation_id: observationId, force_refresh: forceRefresh })
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || `Failed to generate AI Evidence Review (${response.status})`);
  }
  return response.json();
}

export async function getAIReviewSources(observationId: string): Promise<any[]> {
  const response = await fetch(`${API_BASE}/ai-review/${observationId}/sources`);
  if (!response.ok) {
    throw new Error(`Failed to fetch AI review sources (${response.status})`);
  }
  return response.json();
}

export async function fetchObservations(
  crop_id?: string,
  status?: string,
  user_id?: string
): Promise<ObservationListItem[]> {
  const params = new URLSearchParams();
  if (crop_id) params.append('crop_id', crop_id);
  if (status) params.append('status', status);
  if (user_id) params.append('user_id', user_id);

  const url = `${API_BASE}/observations${params.toString() ? `?${params.toString()}` : ''}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch observation history (${response.status})`);
  }
  return response.json();
}

export async function fetchObservationDetail(id: string): Promise<ObservationDetail> {
  const response = await fetch(`${API_BASE}/observations/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch observation detail (${response.status})`);
  }
  return response.json();
}

export async function requestExpertReview(
  id: string,
  reasonNotes?: string
): Promise<{ observation_id: string; escalation_id: string; status: string; reason: string; message: string }> {
  return escalateObservation(id, reasonNotes);
}

export async function escalateObservation(
  id: string,
  reasonNotes?: string
): Promise<{ observation_id: string; escalation_id: string; status: string; reason: string; message: string }> {
  const response = await fetch(`${API_BASE}/observations/${id}/escalate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ reason_notes: reasonNotes }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || `Failed to request expert review (${response.status})`);
  }
  return response.json();
}

// Expert APIs
export async function getExpertDashboardStats(): Promise<ExpertDashboardStats> {
  const response = await fetch(`${API_BASE}/expert/dashboard/stats`, {
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch expert dashboard metrics (${response.status})`);
  }
  return response.json();
}

export async function getExpertReviews(
  status?: string,
  crop_id?: string
): Promise<ExpertReviewQueueItem[]> {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (crop_id) params.append('crop_id', crop_id);

  const url = `${API_BASE}/expert/reviews${params.toString() ? `?${params.toString()}` : ''}`;
  const response = await fetch(url, {
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch expert review queue (${response.status})`);
  }
  return response.json();
}

export async function getExpertReviewDetail(review_id: string): Promise<ExpertReviewDetail> {
  const response = await fetch(`${API_BASE}/expert/reviews/${review_id}`, {
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch review detail (${response.status})`);
  }
  return response.json();
}

export async function completeExpertReview(
  review_id: string,
  payload: { expert_prediction: string; expert_notes?: string }
): Promise<any> {
  const response = await fetch(`${API_BASE}/expert/reviews/${review_id}/complete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || `Failed to complete expert review (${response.status})`);
  }
  return response.json();
}

export async function requestExpertInfo(
  review_id: string,
  payload: { info_note: string }
): Promise<any> {
  const response = await fetch(`${API_BASE}/expert/reviews/${review_id}/request-info`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || `Failed to submit information request (${response.status})`);
  }
  return response.json();
}

export async function fetchReviewedCases(): Promise<any[]> {
  const response = await fetch(`${API_BASE}/expert/reviewed`, {
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch reviewed cases (${response.status})`);
  }
  return response.json();
}

// Token helpers
export function getAuthToken(): string | null {
  return localStorage.getItem('hortisentry_token');
}

export function setAuthToken(token: string) {
  localStorage.setItem('hortisentry_token', token);
}

export function removeAuthToken() {
  localStorage.removeItem('hortisentry_token');
}
export const clearAuthToken = removeAuthToken;

export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Authentication APIs
export async function authLogin(payload: { email: string; password: string }): Promise<any> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || `Login failed (${res.status})`);
  }
  const data = await res.json();
  if (data.token) setAuthToken(data.token);
  return data;
}

export async function authRegister(payload: any): Promise<any> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || `Registration failed (${res.status})`);
  }
  const data = await res.json();
  // DO NOT store token; user must sign in manually
  return data;
}

export async function authDemoLogin(role: 'farmer' | 'expert' | 'admin'): Promise<any> {
  const res = await fetch(`${API_BASE}/auth/demo-login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || `Demo login failed (${res.status})`);
  }
  const data = await res.json();
  if (data.token) setAuthToken(data.token);
  return data;
}

export async function authGetMe(): Promise<any> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) {
    throw new Error('Unauthorized');
  }
  return res.json();
}

// Notification APIs
export async function fetchNotifications(): Promise<{ unread_count: number; items: any[] }> {
  const res = await fetch(`${API_BASE}/notifications`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) {
    return { unread_count: 0, items: [] };
  }
  return res.json();
}

export async function markNotificationRead(id: string): Promise<any> {
  const res = await fetch(`${API_BASE}/notifications/${id}/read`, {
    method: 'PATCH',
    headers: { ...getAuthHeaders() }
  });
  return res.json();
}

export async function markAllNotificationsRead(): Promise<any> {
  const res = await fetch(`${API_BASE}/notifications/read-all`, {
    method: 'POST',
    headers: { ...getAuthHeaders() }
  });
  return res.json();
}

// Admin APIs
export async function fetchAdminDashboard(): Promise<any> {
  const res = await fetch(`${API_BASE}/admin/dashboard`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch admin dashboard');
  return res.json();
}

export async function fetchAdminAnalytics(): Promise<any> {
  const res = await fetch(`${API_BASE}/admin/analytics`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch admin analytics');
  return res.json();
}

export async function fetchAdminUsers(): Promise<any> {
  const res = await fetch(`${API_BASE}/admin/users`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
}

export async function toggleUserStatus(userId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/admin/users/${userId}/toggle-status`, {
    method: 'PATCH',
    headers: { ...getAuthHeaders() }
  });
  return res.json();
}

export async function fetchExpertVerifications(status?: string): Promise<any[]> {
  const params = status ? `?status=${status}` : '';
  const res = await fetch(`${API_BASE}/admin/expert-verifications${params}`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch expert verifications');
  return res.json();
}

export async function updateExpertVerificationStatus(
  userId: string,
  action: 'APPROVE' | 'REJECT' | 'SUSPEND' | string
): Promise<any> {
  const res = await fetch(`${API_BASE}/admin/expert-verifications/${userId}/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify({ action })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || `Failed to update verification status (${res.status})`);
  }
  return res.json();
}

export async function fetchAdminModelMetrics(): Promise<any> {
  const res = await fetch(`${API_BASE}/admin/model-metrics`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch model metrics');
  return res.json();
}

export async function fetchAdminDatasetMetrics(): Promise<any> {
  const res = await fetch(`${API_BASE}/admin/dataset-metrics`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch dataset metrics');
  return res.json();
}

export async function fetchAdminAuditLogs(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/admin/audit-logs`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch audit logs');
  return res.json();
}

export async function fetchAdminCrops(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/admin/crops`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch crops');
  return res.json();
}
