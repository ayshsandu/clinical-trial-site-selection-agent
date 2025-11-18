export interface PatientPool {
  region_id: string;
  region_name: string;
  disease: string;
  estimated_population: number;
  age_distribution: {
    "18-35": number;
    "36-50": number;
    "51-65": number;
    "66+": number;
  };
  demographics: {
    gender_ratio: {
      male: number;
      female: number;
    };
    ethnicity: {
      caucasian: number;
      african_american: number;
      hispanic: number;
      asian: number;
      other: number;
    };
  };
  disease_prevalence_rate: number;
}

export interface RegionDemographics {
  region_id: string;
  region_name: string;
  total_population: number;
  healthcare_access: {
    insured_rate: number;
    primary_care_access: number;
    specialist_access: number;
  };
  enrollment_velocity: {
    avg_days_to_consent: number;
    screen_failure_rate: number;
    retention_rate: number;
  };
  socioeconomic: {
    median_income: number;
    education_level: {
      high_school: number;
      bachelors: number;
      graduate: number;
    };
  };
}

export interface SearchPatientPoolsParams {
  disease: string;
  region: string;
  min_population?: number;
}

export interface GetDemographicsByRegionParams {
  region_id: string;
  disease_filter?: string;
}
