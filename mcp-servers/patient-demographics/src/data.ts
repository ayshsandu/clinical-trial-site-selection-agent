import { PatientPool, RegionDemographics } from "./types.js";

export const patientPools: PatientPool[] = [
  {
    region_id: "US-NE-001",
    region_name: "Boston Metropolitan Area",
    disease: "Type 2 Diabetes",
    estimated_population: 45000,
    age_distribution: {
      "18-35": 5000,
      "36-50": 12000,
      "51-65": 18000,
      "66+": 10000,
    },
    demographics: {
      gender_ratio: { male: 0.52, female: 0.48 },
      ethnicity: {
        caucasian: 0.65,
        african_american: 0.15,
        hispanic: 0.12,
        asian: 0.08,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.087,
  },
  {
    region_id: "US-NE-001",
    region_name: "Boston Metropolitan Area",
    disease: "Hypertension",
    estimated_population: 78000,
    age_distribution: {
      "18-35": 8000,
      "36-50": 18000,
      "51-65": 32000,
      "66+": 20000,
    },
    demographics: {
      gender_ratio: { male: 0.49, female: 0.51 },
      ethnicity: {
        caucasian: 0.63,
        african_american: 0.18,
        hispanic: 0.11,
        asian: 0.08,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.15,
  },
  {
    region_id: "US-NE-002",
    region_name: "New York Metropolitan Area",
    disease: "Type 2 Diabetes",
    estimated_population: 125000,
    age_distribution: {
      "18-35": 15000,
      "36-50": 35000,
      "51-65": 50000,
      "66+": 25000,
    },
    demographics: {
      gender_ratio: { male: 0.51, female: 0.49 },
      ethnicity: {
        caucasian: 0.42,
        african_american: 0.25,
        hispanic: 0.23,
        asian: 0.1,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.092,
  },
  {
    region_id: "US-NE-003",
    region_name: "Philadelphia Metropolitan Area",
    disease: "Type 2 Diabetes",
    estimated_population: 52000,
    age_distribution: {
      "18-35": 6000,
      "36-50": 14000,
      "51-65": 21000,
      "66+": 11000,
    },
    demographics: {
      gender_ratio: { male: 0.5, female: 0.5 },
      ethnicity: {
        caucasian: 0.55,
        african_american: 0.28,
        hispanic: 0.1,
        asian: 0.07,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.089,
  },
  {
    region_id: "US-CA-001",
    region_name: "San Francisco Bay Area",
    disease: "Lung Cancer",
    estimated_population: 8500,
    age_distribution: {
      "18-35": 200,
      "36-50": 1500,
      "51-65": 4000,
      "66+": 2800,
    },
    demographics: {
      gender_ratio: { male: 0.54, female: 0.46 },
      ethnicity: {
        caucasian: 0.48,
        african_american: 0.08,
        hispanic: 0.22,
        asian: 0.22,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.0062,
  },
  {
    region_id: "US-CA-002",
    region_name: "Los Angeles Metropolitan Area",
    disease: "Lung Cancer",
    estimated_population: 15000,
    age_distribution: {
      "18-35": 400,
      "36-50": 2500,
      "51-65": 7000,
      "66+": 5100,
    },
    demographics: {
      gender_ratio: { male: 0.52, female: 0.48 },
      ethnicity: {
        caucasian: 0.35,
        african_american: 0.1,
        hispanic: 0.42,
        asian: 0.13,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.0068,
  },
  {
    region_id: "US-TX-001",
    region_name: "Houston Metropolitan Area",
    disease: "Type 2 Diabetes",
    estimated_population: 95000,
    age_distribution: {
      "18-35": 12000,
      "36-50": 28000,
      "51-65": 38000,
      "66+": 17000,
    },
    demographics: {
      gender_ratio: { male: 0.51, female: 0.49 },
      ethnicity: {
        caucasian: 0.38,
        african_american: 0.22,
        hispanic: 0.35,
        asian: 0.05,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.11,
  },
  {
    region_id: "US-FL-001",
    region_name: "Miami Metropolitan Area",
    disease: "Type 2 Diabetes",
    estimated_population: 72000,
    age_distribution: {
      "18-35": 8000,
      "36-50": 18000,
      "51-65": 28000,
      "66+": 18000,
    },
    demographics: {
      gender_ratio: { male: 0.48, female: 0.52 },
      ethnicity: {
        caucasian: 0.25,
        african_american: 0.2,
        hispanic: 0.52,
        asian: 0.03,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.095,
  },
  {
    region_id: "US-IL-001",
    region_name: "Chicago Metropolitan Area",
    disease: "Hypertension",
    estimated_population: 145000,
    age_distribution: {
      "18-35": 15000,
      "36-50": 35000,
      "51-65": 60000,
      "66+": 35000,
    },
    demographics: {
      gender_ratio: { male: 0.49, female: 0.51 },
      ethnicity: {
        caucasian: 0.52,
        african_american: 0.28,
        hispanic: 0.15,
        asian: 0.05,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.16,
  },
  {
    region_id: "US-WA-001",
    region_name: "Seattle Metropolitan Area",
    disease: "Metabolic Disorder",
    estimated_population: 3200,
    age_distribution: {
      "18-35": 800,
      "36-50": 1100,
      "51-65": 900,
      "66+": 400,
    },
    demographics: {
      gender_ratio: { male: 0.5, female: 0.5 },
      ethnicity: {
        caucasian: 0.68,
        african_american: 0.08,
        hispanic: 0.09,
        asian: 0.15,
        other: 0.0,
      },
    },
    disease_prevalence_rate: 0.0021,
  },
];

export const regionDemographics: RegionDemographics[] = [
  {
    region_id: "US-NE-001",
    region_name: "Boston Metropolitan Area",
    total_population: 4800000,
    healthcare_access: {
      insured_rate: 0.95,
      primary_care_access: 0.89,
      specialist_access: 0.82,
    },
    enrollment_velocity: {
      avg_days_to_consent: 14,
      screen_failure_rate: 0.23,
      retention_rate: 0.87,
    },
    socioeconomic: {
      median_income: 87500,
      education_level: {
        high_school: 0.91,
        bachelors: 0.52,
        graduate: 0.28,
      },
    },
  },
  {
    region_id: "US-NE-002",
    region_name: "New York Metropolitan Area",
    total_population: 19500000,
    healthcare_access: {
      insured_rate: 0.91,
      primary_care_access: 0.85,
      specialist_access: 0.88,
    },
    enrollment_velocity: {
      avg_days_to_consent: 16,
      screen_failure_rate: 0.25,
      retention_rate: 0.84,
    },
    socioeconomic: {
      median_income: 78000,
      education_level: {
        high_school: 0.87,
        bachelors: 0.42,
        graduate: 0.19,
      },
    },
  },
  {
    region_id: "US-NE-003",
    region_name: "Philadelphia Metropolitan Area",
    total_population: 6200000,
    healthcare_access: {
      insured_rate: 0.93,
      primary_care_access: 0.87,
      specialist_access: 0.79,
    },
    enrollment_velocity: {
      avg_days_to_consent: 15,
      screen_failure_rate: 0.24,
      retention_rate: 0.85,
    },
    socioeconomic: {
      median_income: 72000,
      education_level: {
        high_school: 0.89,
        bachelors: 0.38,
        graduate: 0.17,
      },
    },
  },
  {
    region_id: "US-CA-001",
    region_name: "San Francisco Bay Area",
    total_population: 7700000,
    healthcare_access: {
      insured_rate: 0.94,
      primary_care_access: 0.88,
      specialist_access: 0.86,
    },
    enrollment_velocity: {
      avg_days_to_consent: 13,
      screen_failure_rate: 0.21,
      retention_rate: 0.89,
    },
    socioeconomic: {
      median_income: 112000,
      education_level: {
        high_school: 0.92,
        bachelors: 0.58,
        graduate: 0.31,
      },
    },
  },
  {
    region_id: "US-CA-002",
    region_name: "Los Angeles Metropolitan Area",
    total_population: 13200000,
    healthcare_access: {
      insured_rate: 0.89,
      primary_care_access: 0.82,
      specialist_access: 0.81,
    },
    enrollment_velocity: {
      avg_days_to_consent: 17,
      screen_failure_rate: 0.26,
      retention_rate: 0.82,
    },
    socioeconomic: {
      median_income: 71000,
      education_level: {
        high_school: 0.83,
        bachelors: 0.36,
        graduate: 0.15,
      },
    },
  },
  {
    region_id: "US-TX-001",
    region_name: "Houston Metropolitan Area",
    total_population: 7100000,
    healthcare_access: {
      insured_rate: 0.86,
      primary_care_access: 0.79,
      specialist_access: 0.76,
    },
    enrollment_velocity: {
      avg_days_to_consent: 18,
      screen_failure_rate: 0.27,
      retention_rate: 0.81,
    },
    socioeconomic: {
      median_income: 68000,
      education_level: {
        high_school: 0.85,
        bachelors: 0.34,
        graduate: 0.13,
      },
    },
  },
  {
    region_id: "US-FL-001",
    region_name: "Miami Metropolitan Area",
    total_population: 6200000,
    healthcare_access: {
      insured_rate: 0.84,
      primary_care_access: 0.77,
      specialist_access: 0.74,
    },
    enrollment_velocity: {
      avg_days_to_consent: 19,
      screen_failure_rate: 0.28,
      retention_rate: 0.79,
    },
    socioeconomic: {
      median_income: 59000,
      education_level: {
        high_school: 0.81,
        bachelors: 0.31,
        graduate: 0.12,
      },
    },
  },
  {
    region_id: "US-IL-001",
    region_name: "Chicago Metropolitan Area",
    total_population: 9500000,
    healthcare_access: {
      insured_rate: 0.92,
      primary_care_access: 0.86,
      specialist_access: 0.83,
    },
    enrollment_velocity: {
      avg_days_to_consent: 15,
      screen_failure_rate: 0.24,
      retention_rate: 0.85,
    },
    socioeconomic: {
      median_income: 75000,
      education_level: {
        high_school: 0.88,
        bachelors: 0.41,
        graduate: 0.18,
      },
    },
  },
  {
    region_id: "US-WA-001",
    region_name: "Seattle Metropolitan Area",
    total_population: 4000000,
    healthcare_access: {
      insured_rate: 0.94,
      primary_care_access: 0.9,
      specialist_access: 0.85,
    },
    enrollment_velocity: {
      avg_days_to_consent: 13,
      screen_failure_rate: 0.2,
      retention_rate: 0.9,
    },
    socioeconomic: {
      median_income: 95000,
      education_level: {
        high_school: 0.93,
        bachelors: 0.55,
        graduate: 0.25,
      },
    },
  },
];
