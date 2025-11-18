"""Node for querying patient demographics MCP server."""

import logging
import os
from datetime import datetime
from ..state import TrialSiteSelectionState, AuditEntry
from ..mcp_client import MCPClient

logger = logging.getLogger(__name__)


def query_demographics(state: TrialSiteSelectionState) -> TrialSiteSelectionState:
    """
    Query patient demographics MCP server.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with demographics data
    """
    logger.info("Querying patient demographics server")
    
    requirements = state.get("trial_requirements")
    if not requirements:
        logger.error("No trial requirements found in state")
        return {
            **state,
            "error_message": "No trial requirements to query demographics"
        }
    
    demographics_url = os.getenv("DEMOGRAPHICS_SERVER_URL", "http://localhost:4001/mcp")
    
    try:
        with MCPClient(demographics_url) as client:
            pools = []
            regions = []
            audit_entries = []
            
            # Get disease and geographic preferences
            disease = requirements.get("disease") or requirements.get("indication", "")
            geographic_prefs = requirements.get("geographic_preferences", [])
            
            # If no geographic preferences, use a broad search
            if not geographic_prefs:
                geographic_prefs = ["US"]
            
            # Search patient pools for each geographic preference
            for region in geographic_prefs:
                logger.info(f"Searching patient pools for {disease} in {region}")
                
                try:
                    min_population = requirements.get("min_site_capacity", 0)
                    if min_population is None:
                        min_population = 0
                    
                    result = client.call_tool(
                        "search_patient_pools",
                        {
                            "disease": disease,
                            "region": region,
                            "min_population": min_population
                        }
                    )
                    
                    found_pools = result.get("pools", [])
                    pools.extend(found_pools)
                    
                    logger.info(f"Found {len(found_pools)} patient pools in {region}")
                    
                    # Create audit entry
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_demographics",
                        "action": "Search patient pools",
                        "server": "patient-demographics",
                        "tool": "search_patient_pools",
                        "parameters": {
                            "disease": disease,
                            "region": region,
                            "min_population": min_population
                        },
                        "results_summary": f"Found {len(found_pools)} pools"
                    }
                    audit_entries.append(audit_entry)
                    
                except Exception as e:
                    logger.error(f"Error searching pools for {region}: {e}")
                    
                    min_population = requirements.get("min_site_capacity", 0)
                    if min_population is None:
                        min_population = 0
                    
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_demographics",
                        "action": "Search patient pools",
                        "server": "patient-demographics",
                        "tool": "search_patient_pools",
                        "parameters": {
                            "disease": disease,
                            "region": region,
                            "min_population": min_population
                        },
                        "results_summary": f"ERROR: {str(e)}"
                    }
                    audit_entries.append(audit_entry)
            
            # Get detailed demographics for unique regions
            region_ids = list(set([pool.get("region_id") for pool in pools if pool.get("region_id")]))
            
            for region_id in region_ids[:5]:  # Limit to 5 regions to avoid too many calls
                logger.info(f"Getting demographics for region {region_id}")
                
                try:
                    result = client.call_tool(
                        "get_demographics_by_region",
                        {
                            "region_id": region_id,
                            "disease_filter": disease
                        }
                    )
                    
                    regions.append(result)
                    
                    logger.info(f"Retrieved demographics for {region_id}")
                    
                    # Create audit entry
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_demographics",
                        "action": "Get region demographics",
                        "server": "patient-demographics",
                        "tool": "get_demographics_by_region",
                        "parameters": {
                            "region_id": region_id,
                            "disease_filter": disease
                        },
                        "results_summary": f"Retrieved demographics for {result.get('region_name', region_id)}"
                    }
                    audit_entries.append(audit_entry)
                    
                except Exception as e:
                    logger.error(f"Error getting demographics for {region_id}: {e}")
                    
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_demographics",
                        "action": "Get region demographics",
                        "server": "patient-demographics",
                        "tool": "get_demographics_by_region",
                        "parameters": {
                            "region_id": region_id,
                            "disease_filter": disease
                        },
                        "results_summary": f"ERROR: {str(e)}"
                    }
                    audit_entries.append(audit_entry)
            
            # Update state
            logger.info(f"Demographics query complete: {len(pools)} pools, {len(regions)} regions")
            
            return {
                **state,
                "patient_demographics": {
                    "pools": pools,
                    "regions": regions,
                    "total_count": len(pools)
                },
                "audit_trail": state.get("audit_trail", []) + audit_entries,
                "iteration_count": state.get("iteration_count", 0) + 1
            }
            
    except Exception as e:
        logger.error(f"Error querying demographics server: {e}")
        
        audit_entry: AuditEntry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": "query_demographics",
            "action": "Query demographics server",
            "server": "patient-demographics",
            "tool": None,
            "parameters": None,
            "results_summary": f"ERROR: {str(e)}"
        }
        
        return {
            **state,
            "error_message": f"Failed to query demographics: {str(e)}",
            "audit_trail": state.get("audit_trail", []) + [audit_entry],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
