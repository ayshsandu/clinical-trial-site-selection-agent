export interface Site {
  site_id: string;
  site_name: string;
  location: {
    city: string;
    state: string;
    country: string;
    region_id: string;
  };
  capacity: {
    max_concurrent_trials: number;
    available_slots: number;
    patient_enrollment_capacity: number;
  };
  therapeutic_areas: string[];
}

export interface SiteCapabilities {
  site_id: string;
  site_name: string;
  certifications: string[];
  equipment: {
    imaging: string[];
    laboratory: string[];
    specialized: string[];
  };
  staff: {
    principal_investigators: number;
    sub_investigators: number;
    research_coordinators: number;
    regulatory_specialists: number;
  };
  investigator_qualifications: {
    board_certified: number;
    avg_years_experience: number;
    publications: number;
  };
}

export interface HistoricalTrial {
  trial_id: string;
  phase: string;
  therapeutic_area: string;
  target_enrollment: number;
  actual_enrollment: number;
  enrollment_duration_days: number;
  screen_failure_rate: number;
  dropout_rate: number;
  protocol_deviations: number;
  completion_year: number;
}

export interface EnrollmentHistory {
  site_id: string;
  site_name: string;
  historical_trials: HistoricalTrial[];
  aggregate_metrics: {
    total_trials_completed: number;
    avg_enrollment_rate: number;
    avg_screen_failure_rate: number;
    avg_retention_rate: number;
    regulatory_inspection_results: string;
  };
}

export interface SearchSitesParams {
  region: string;
  therapeutic_area?: string;
  min_capacity?: number;
}

export interface GetSiteCapabilitiesParams {
  site_id: string;
}

export interface GetEnrollmentHistoryParams {
  site_id: string;
  years?: number;
}