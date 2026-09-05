export interface HealthStatus {
  status: string;
  database?: string;
  ml_mode: 'DEMO' | 'REAL';
  app_name?: string;
  environment: string;
  model_loaded?: boolean;
  model_name?: string;
  num_classes?: number;
  database_connected?: boolean;
}

export interface CropStage {
  key: string;
  display_name: string;
  description?: string;
}

export interface DiseaseClass {
  key: string;
  display_name: string;
  scientific_name?: string;
  severity?: string;
  description?: string;
}

export interface CropConfig {
  key: string;
  common_name?: string;
  display_name: string;
  display_name_en?: string;
  display_name_ta?: string;
  scientific_name?: string;
  category?: string;
  supported_status?: string;
  disease_knowledge_status?: string;
  vision_support_status?: string;
  model_id?: string;
  description?: string;
  is_active?: boolean;
  stages: CropStage[];
  symptoms: (string | { key: string; display_name: string })[];
  disease_classes: DiseaseClass[];
}

export interface ImageQualityResult {
  is_valid: boolean;
  is_blur_detected: boolean;
  is_exposure_issue: boolean;
  blur_score: number;
  brightness_score: number;
  width: number;
  height: number;
  quality_message: string;
}

export interface TopPredictionItem {
  class: string;
  confidence: number;
}

export interface PredictionDetailResponse {
  id: string;
  predicted_class: string;
  confidence: number;
  top_predictions: TopPredictionItem[];
  model_version: string;
  inference_time_ms: number;
  is_demo_mode: boolean;
}

export interface ImageMetadataResponse {
  id: string;
  file_name: string;
  image_url?: string;
  width?: number;
  height?: number;
  is_blur_detected?: boolean;
  is_exposure_issue?: boolean;
  blur_score?: number;
}

export interface EscalationSummaryResponse {
  is_escalated: boolean;
  reason?: string;
  status: string;
}

export interface ObservationCreateResponse {
  observation_id: string;
  status: string;
  crop: string;
  crop_stage: string;
  submitted_at: string;
  image: ImageMetadataResponse;
  quality_analysis: ImageQualityResult;
  prediction: PredictionDetailResponse;
  escalation: EscalationSummaryResponse;
}

export interface ObservationListItem {
  id: string;
  crop_id: string;
  crop_display_name: string;
  crop_stage: string;
  symptoms: string[];
  location_village: string;
  location_district: string;
  location_state: string;
  status: string;
  submitted_at: string;
  predicted_class?: string;
  confidence?: number;
  risk_level?: string;
}

export interface ObservationDetail {
  id: string;
  status: string;
  crop_id: string;
  crop_display_name: string;
  crop_stage: string;
  variety?: string;
  farmer_confidence?: number;
  symptoms: string[];
  location: {
    village: string;
    district: string;
    state: string;
  };
  notes?: string;
  timestamps: {
    symptom_observed_at?: string;
    submitted_at: string;
  };
  submitted_at?: string;
  predicted_class?: string;
  confidence?: number;
  escalation_reason?: string;
  image: ImageMetadataResponse;
  prediction: PredictionDetailResponse;
  escalation: EscalationSummaryResponse;
  expert_review: {
    status: string;
    expert_prediction?: string;
    expert_notes?: string;
    info_requested_note?: string;
    completed_at?: string;
    reviewed_at?: string;
    expert_name?: string;
    severity?: string;
    final_condition?: string;
    treatment_recommendation?: string;
  };
}

export interface ExpertDashboardStats {
  total_observations: number;
  pending_reviews: number;
  low_confidence_cases: number;
  completed_reviews: number;
  total_escalations: number;
}

export interface ExpertReviewQueueItem {
  review_id: string;
  observation_id: string;
  crop_display_name: string;
  predicted_class: string;
  confidence: number;
  escalation_reason: string;
  review_status: string;
  submitted_at: string;
  is_blur_detected: boolean;
}

export interface ExpertReviewDetail {
  review_id: string;
  observation_id: string;
  crop_display_name: string;
  crop_stage: string;
  symptoms: string[];
  location: string;
  farmer_notes?: string;
  symptom_observed_at?: string;
  submitted_at: string;
  image_url: string;
  quality_analysis: {
    is_blur_detected: boolean;
    is_exposure_issue: boolean;
    blur_score?: number;
    width?: number;
    height?: number;
  };
  ai_prediction: {
    predicted_class: string;
    confidence: number;
    top_predictions: TopPredictionItem[];
    is_demo_mode: boolean;
  };
  escalation_reason: string;
  review_status: string;
  expert_prediction?: string;
  expert_notes?: string;
  info_requested_note?: string;
  started_at?: string;
  completed_at?: string;
  turnaround_metrics?: {
    total_seconds: number;
    hours: number;
    days: number;
    formatted: string;
  };
}

export type UserRole = 'farmer' | 'expert' | 'admin' | 'public' | 'home';

export interface AuthUser {
  id: string;
  name?: string;
  full_name?: string;
  email: string;
  role: string;
  farmer_code?: string;
  phone?: string;
  location?: string;
  is_active?: boolean;
  verification_status?: string;
  account_status?: string;
}

export interface NotificationItem {
  id: string;
  observation_id?: string;
  title: string;
  message: string;
  status: 'UNREAD' | 'READ';
  is_read?: boolean;
  created_at: string;
}

export interface AdminDashboardStats {
  total_farmers?: number;
  total_experts?: number;
  total_users?: number;
  total_observations: number;
  pending_reviews?: number;
  pending_escalations?: number;
  completed_reviews: number;
  high_risk_cases?: number;
  active_model?: string;
  system_status?: string;
  system_health?: string;
}

export interface AdminAnalytics {
  overview?: {
    total_farmers: number;
    total_observations: number;
    total_escalations: number;
    total_expert_reviews: number;
    high_risk_percentage: number;
  };
  time_to_expert_kpi?: {
    average_hours: number;
    median_hours: number;
    min_hours: number;
    max_hours: number;
    p90_hours: number;
    target_hours: number;
    target_met: boolean;
    sample_count: number;
    unit: string;
  };
  baseline_comparison?: {
    baseline_review_time_hours: number;
    hortisentry_review_time_hours: number;
    improvement_percentage: number;
    evaluation_note: string;
  };
  distributions?: {
    disease_distribution: Record<string, number>;
    crop_distribution: Record<string, number>;
    location_distribution: Record<string, number>;
  };
  kpi_metrics?: any;
  disease_distribution?: any[];
  escalation_reasons?: any[];
  monthly_trend?: any[];
  [key: string]: any;
}

export interface AdminUserItem {
  id: string;
  name?: string;
  full_name?: string;
  email: string;
  role: string;
  farmer_code?: string;
  location?: string;
  phone?: string;
  is_active: boolean;
  verification_status?: string;
  account_status?: string;
  observations_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface ExpertVerificationItem {
  id: string;
  name: string;
  email: string;
  role: string;
  verification_status: 'NOT_REQUIRED' | 'PENDING' | 'VERIFIED' | 'REJECTED' | 'SUSPENDED' | string;
  account_status: 'ACTIVE' | 'SUSPENDED' | 'INACTIVE' | string;
  phone?: string;
  location?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AuditLogItem {
  id: string;
  timestamp?: string;
  created_at?: string;
  user_id?: string;
  user_email?: string;
  action: string;
  entity_type?: string;
  entity_id?: string;
  details?: any;
}
