"""Node for querying site performance MCP server."""

import logging
import os
from datetime import datetime
from ..state import TrialSiteSelectionState, AuditEntry
from ..mcp_client import MCPClient

logger = logging.getLogger(__name__)


def query_performance(state: TrialSiteSelectionState) -> TrialSiteSelectionState:
    """
    Query site performance MCP server.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with site performance data
    """
    logger.info("Querying site performance server")
    
    requirements = state.get("trial_requirements")
    demographics = state.get("patient_demographics")
    
    if not requirements:
        logger.error("No trial requirements found in state")
        return {
            **state,
            "error_message": "No trial requirements to query site performance"
        }
    
    performance_url = os.getenv("PERFORMANCE_SERVER_URL", "http://localhost:4002/mcp")
    bearer_token = state.get("bearer_token")
    
    try:
        with MCPClient(performance_url, bearer_token) as client:
            sites = []
            capabilities = []
            histories = []
            audit_entries = []
            
            # Get search parameters
            geographic_prefs = requirements.get("geographic_preferences", ["US"])
            therapeutic_area = requirements.get("therapeutic_area")
            min_capacity = requirements.get("min_site_capacity")
            if min_capacity is None:
                min_capacity = 0
            
            # Search sites for each geographic preference
            for region in geographic_prefs:
                logger.info(f"Searching sites in {region}")
                
                search_params = {
                    "region": region,
                    "min_capacity": min_capacity
                }
                
                if therapeutic_area:
                    search_params["therapeutic_area"] = therapeutic_area
                
                try:
                    result = client.call_tool("search_sites", search_params)
                    
                    found_sites = result.get("sites", [])
                    sites.extend(found_sites)
                    
                    logger.info(f"Found {len(found_sites)} sites in {region}")
                    
                    # Create audit entry
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_performance",
                        "action": "Search clinical trial sites",
                        "server": "site-performance",
                        "tool": "search_sites",
                        "parameters": search_params,
                        "results_summary": f"Found {len(found_sites)} sites"
                    }
                    audit_entries.append(audit_entry)
                    
                except Exception as e:
                    logger.error(f"Error searching sites for {region}: {e}")
                    
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_performance",
                        "action": "Search clinical trial sites",
                        "server": "site-performance",
                        "tool": "search_sites",
                        "parameters": search_params,
                        "results_summary": f"ERROR: {str(e)}"
                    }
                    audit_entries.append(audit_entry)
            
            # Get capabilities and history for each unique site
            site_ids = list(set([site.get("site_id") for site in sites if site.get("site_id")]))
            
            # Limit to top sites to avoid too many API calls
            for site_id in site_ids[:10]:
                # Get capabilities
                logger.info(f"Getting capabilities for site {site_id}")
                
                try:
                    caps = client.call_tool(
                        "get_site_capabilities",
                        {"site_id": site_id}
                    )
                    capabilities.append(caps)
                    
                    logger.info(f"Retrieved capabilities for {site_id}")
                    
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_performance",
                        "action": "Get site capabilities",
                        "server": "site-performance",
                        "tool": "get_site_capabilities",
                        "parameters": {"site_id": site_id},
                        "results_summary": f"Retrieved capabilities for {caps.get('site_name', site_id)}"
                    }
                    audit_entries.append(audit_entry)
                    
                except Exception as e:
                    logger.error(f"Error getting capabilities for {site_id}: {e}")
                    
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_performance",
                        "action": "Get site capabilities",
                        "server": "site-performance",
                        "tool": "get_site_capabilities",
                        "parameters": {"site_id": site_id},
                        "results_summary": f"ERROR: {str(e)}"
                    }
                    audit_entries.append(audit_entry)
                
                # Get enrollment history
                logger.info(f"Getting enrollment history for site {site_id}")
                
                try:
                    history = client.call_tool(
                        "get_enrollment_history",
                        {"site_id": site_id, "years": 3}
                    )
                    histories.append(history)
                    
                    logger.info(f"Retrieved enrollment history for {site_id}")
                    
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_performance",
                        "action": "Get enrollment history",
                        "server": "site-performance",
                        "tool": "get_enrollment_history",
                        "parameters": {"site_id": site_id, "years": 3},
                        "results_summary": f"Retrieved history for {history.get('site_name', site_id)}"
                    }
                    audit_entries.append(audit_entry)
                    
                except Exception as e:
                    logger.error(f"Error getting history for {site_id}: {e}")
                    
                    audit_entry: AuditEntry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "node": "query_performance",
                        "action": "Get enrollment history",
                        "server": "site-performance",
                        "tool": "get_enrollment_history",
                        "parameters": {"site_id": site_id, "years": 3},
                        "results_summary": f"ERROR: {str(e)}"
                    }
                    audit_entries.append(audit_entry)
            
            # Update state
            logger.info(
                f"Performance query complete: {len(sites)} sites, "
                f"{len(capabilities)} capabilities, {len(histories)} histories"
            )
            
            return {
                **state,
                "site_performance_data": {
                    "sites": sites,
                    "capabilities": capabilities,
                    "histories": histories,
                    "total_count": len(sites)
                },
                "audit_trail": state.get("audit_trail", []) + audit_entries,
                "iteration_count": state.get("iteration_count", 0) + 1
            }
            
    except Exception as e:
        logger.error(f"Error querying site performance server: {e}")
        
        audit_entry: AuditEntry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": "query_performance",
            "action": "Query site performance server",
            "server": "site-performance",
            "tool": None,
            "parameters": None,
            "results_summary": f"ERROR: {str(e)}"
        }
        
        return {
            **state,
            "error_message": f"Failed to query site performance: {str(e)}",
            "audit_trail": state.get("audit_trail", []) + [audit_entry],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
