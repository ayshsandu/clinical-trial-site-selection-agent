import { z } from "zod";
import {
  SearchPatientPoolsParams,
  GetDemographicsByRegionParams,
} from "./types.js";
import { patientPools, regionDemographics } from "./data.js";

// Zod schemas for validation
export const SearchPatientPoolsSchema = z.object({
  disease: z.string()
    .optional()
    .describe("Disease or indication (e.g., 'Type 2 Diabetes', 'Lung Cancer')"),
  region: z.string().describe("Geographic region (e.g., 'US-Northeast', 'US-California')"),
  min_population: z.number().optional().default(0).describe("Minimum patient population size"),
});

export const GetDemographicsByRegionSchema = z.object({
  region_id: z.string().describe("Region identifier (e.g., 'US-NE-001')"),
  disease_filter: z.string().optional().describe("Optional disease filter"),
});

// Tool implementations
export function searchPatientPools(params: SearchPatientPoolsParams) {
  const { disease, region, min_population = 0 } = params;

  // Normalize region search (e.g., "US-Northeast" matches "US-NE-*")
  const regionPrefix = normalizeRegion(region);

  const matchingPools = patientPools.filter((pool) => {
    const diseaseMatch = pool.disease.toLowerCase().includes(disease.toLowerCase());
    const regionMatch = pool.region_id.startsWith(regionPrefix) || 
                        pool.region_name.toLowerCase().includes(region.toLowerCase());
    const populationMatch = pool.estimated_population >= min_population;

    return diseaseMatch && regionMatch && populationMatch;
  });

  return {
    pools: matchingPools,
    total_count: matchingPools.length,
    query: params,
  };
}

export function getDemographicsByRegion(params: GetDemographicsByRegionParams) {
  const { region_id, disease_filter } = params;

  const demographics = regionDemographics.find((r) => r.region_id === region_id);

  if (!demographics) {
    throw new Error(`Region not found: ${region_id}`);
  }

  // If disease filter is provided, include relevant patient pools
  let disease_specific_data = null;
  if (disease_filter) {
    const relevantPools = patientPools.filter(
      (pool) => pool.region_id === region_id && 
                pool.disease.toLowerCase().includes(disease_filter.toLowerCase())
    );
    disease_specific_data = relevantPools;
  }

  return {
    ...demographics,
    disease_specific_data,
  };
}

// Helper function to normalize region names
function normalizeRegion(region: string): string {
  const regionMap: Record<string, string> = {
    "northeast": "US-NE",
    "us-northeast": "US-NE",
    "california": "US-CA",
    "us-california": "US-CA",
    "texas": "US-TX",
    "us-texas": "US-TX",
    "florida": "US-FL",
    "us-florida": "US-FL",
    "illinois": "US-IL",
    "us-illinois": "US-IL",
    "washington": "US-WA",
    "us-washington": "US-WA",
  };

  const normalized = region.toLowerCase().replace(/\s+/g, "-");
  return regionMap[normalized] || region.toUpperCase();
}
