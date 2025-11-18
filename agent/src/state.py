"""State definitions for the Clinical Trial Site Selection Agent."""

from typing import TypedDict, Optional, Any
from datetime import datetime


class TrialRequirements(TypedDict, total=False):
    """Structured trial requirements extracted from user query."""
    disease: str
    indication: str
    phase: str
    target_enrollment: int
    geographic_preferences: list[str]
    therapeutic_area: Optional[str]
    min_site_capacity: Optional[int]
    special_requirements: Optional[list[str]]


class PatientDemographicsData(TypedDict, total=False):
    """Data from patient demographics MCP server."""
    pools: list[dict[str, Any]]
    regions: list[dict[str, Any]]
    total_count: int


class SitePerformanceData(TypedDict, total=False):
    """Data from site performance MCP server."""
    sites: list[dict[str, Any]]
    capabilities: list[dict[str, Any]]
    histories: list[dict[str, Any]]
    total_count: int


class SiteRecommendation(TypedDict):
    """A single site recommendation."""
    rank: int
    site_id: str
    site_name: str
    score: float
    reasoning: str
    key_strengths: list[str]
    concerns: list[str]
    patient_pool_match: dict[str, Any]
    historical_performance: dict[str, Any]


class AuditEntry(TypedDict):
    """Single audit trail entry."""
    timestamp: str
    node: str
    action: str
    server: Optional[str]
    tool: Optional[str]
    parameters: Optional[dict[str, Any]]
    results_summary: Optional[str]


class TrialSiteSelectionState(TypedDict):
    """Complete state for the trial site selection agent."""
    
    # Input
    user_query: str
    
    # Parsed requirements
    trial_requirements: Optional[TrialRequirements]
    
    # MCP server data
    patient_demographics: Optional[PatientDemographicsData]
    site_performance_data: Optional[SitePerformanceData]
    
    # Analysis results
    recommended_sites: list[SiteRecommendation]
    analysis_summary: str
    
    # Metadata
    audit_trail: list[AuditEntry]
    error_message: Optional[str]
    iteration_count: int
