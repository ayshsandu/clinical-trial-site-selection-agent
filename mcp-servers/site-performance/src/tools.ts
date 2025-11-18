import { z } from "zod";
import {
  SearchSitesParams,
  GetSiteCapabilitiesParams,
  GetEnrollmentHistoryParams,
} from "./types.js";
import { sites, siteCapabilities, enrollmentHistories } from "./data.js";

// Zod schemas for validation
export const SearchSitesSchema = z.object({
  region: z.string().describe("Geographic region (e.g., 'US-Northeast', 'US-California')"),
  therapeutic_area: z
    .string()
    .optional()
    .describe("Therapeutic area expertise required (e.g., 'Oncology', 'Cardiology')"),
  min_capacity: z
    .number()
    .optional()
    .default(0)
    .describe("Minimum patient enrollment capacity"),
});

export const GetSiteCapabilitiesSchema = z.object({
  site_id: z.string().describe("Site identifier (e.g., 'SITE-001')"),
});

export const GetEnrollmentHistorySchema = z.object({
  site_id: z.string().describe("Site identifier (e.g., 'SITE-001')"),
  years: z.number().optional().default(3).describe("Number of years of history to retrieve"),
});

// Tool implementations
export function searchSites(params: SearchSitesParams) {
  const { region, therapeutic_area, min_capacity = 0 } = params;

  // Normalize region search
  const regionPrefix = normalizeRegion(region);

  const matchingSites = sites.filter((site) => {
    const regionMatch =
      site.location.region_id.startsWith(regionPrefix) ||
      site.location.state.toLowerCase() === region.toLowerCase() ||
      region.toLowerCase().includes(site.location.state.toLowerCase());

    const therapeuticMatch =
      !therapeutic_area ||
      site.therapeutic_areas.some((area) =>
        area.toLowerCase().includes(therapeutic_area.toLowerCase())
      );

    const capacityMatch = site.capacity.patient_enrollment_capacity >= min_capacity;

    return regionMatch && therapeuticMatch && capacityMatch;
  });

  return {
    sites: matchingSites,
    total_count: matchingSites.length,
    query: params,
  };
}

export function getSiteCapabilities(params: GetSiteCapabilitiesParams) {
  const { site_id } = params;

  const capabilities = siteCapabilities.find((cap) => cap.site_id === site_id);

  if (!capabilities) {
    throw new Error(`Site capabilities not found: ${site_id}`);
  }

  return capabilities;
}

export function getEnrollmentHistory(params: GetEnrollmentHistoryParams) {
  const { site_id, years = 3 } = params;

  const history = enrollmentHistories.find((hist) => hist.site_id === site_id);

  if (!history) {
    throw new Error(`Enrollment history not found: ${site_id}`);
  }

  // Filter trials by year
  const currentYear = new Date().getFullYear();
  const cutoffYear = currentYear - years;

  const filteredTrials = history.historical_trials.filter(
    (trial) => trial.completion_year >= cutoffYear
  );

  return {
    site_id: history.site_id,
    site_name: history.site_name,
    historical_trials: filteredTrials,
    aggregate_metrics: history.aggregate_metrics,
    years_included: years,
  };
}

// Helper function to normalize region names
function normalizeRegion(region: string): string {
  const regionMap: Record<string, string> = {
    northeast: "US-NE",
    "us-northeast": "US-NE",
    california: "US-CA",
    "us-california": "US-CA",
    texas: "US-TX",
    "us-texas": "US-TX",
    florida: "US-FL",
    "us-florida": "US-FL",
    illinois: "US-IL",
    "us-illinois": "US-IL",
    washington: "US-WA",
    "us-washington": "US-WA",
  };

  const normalized = region.toLowerCase().replace(/\s+/g, "-");
  return regionMap[normalized] || region.toUpperCase();
}