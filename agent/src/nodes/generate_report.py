"""Node for generating final report."""

import logging
import json
from datetime import datetime
from ..state import TrialSiteSelectionState, AuditEntry

logger = logging.getLogger(__name__)


def generate_report(state: TrialSiteSelectionState) -> TrialSiteSelectionState:
    """
    Generate final recommendation report.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final report
    """
    logger.info("Generating final report")
    
    # Just add an audit entry - the state already contains all the results
    audit_entry: AuditEntry = {
        "timestamp": datetime.utcnow().isoformat(),
        "node": "generate_report",
        "action": "Generate final recommendation report",
        "server": None,
        "tool": None,
        "parameters": None,
        "results_summary": "Report generated successfully"
    }
    
    return {
        **state,
        "audit_trail": state.get("audit_trail", []) + [audit_entry],
        "iteration_count": state.get("iteration_count", 0) + 1
    }


def format_report(state: TrialSiteSelectionState) -> str:
    """
    Format the final state as a readable report.
    
    Args:
        state: Final agent state
        
    Returns:
        Formatted report string
    """
    report_lines = []
    
    report_lines.append("=" * 80)
    report_lines.append("CLINICAL TRIAL SITE SELECTION REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Query
    report_lines.append(f"Query: {state['user_query']}")
    report_lines.append("")
    
    # Requirements
    requirements = state.get("trial_requirements", {})
    if requirements:
        report_lines.append("TRIAL REQUIREMENTS:")
        report_lines.append(f"  Disease: {requirements.get('disease', 'N/A')}")
        report_lines.append(f"  Phase: {requirements.get('phase', 'N/A')}")
        report_lines.append(f"  Target Enrollment: {requirements.get('target_enrollment', 'N/A')}")
        report_lines.append(f"  Geographic Preferences: {', '.join(requirements.get('geographic_preferences', []))}")
        if requirements.get('therapeutic_area'):
            report_lines.append(f"  Therapeutic Area: {requirements['therapeutic_area']}")
        report_lines.append("")
    
    # Analysis Summary
    if state.get("analysis_summary"):
        report_lines.append("ANALYSIS SUMMARY:")
        report_lines.append(f"  {state['analysis_summary']}")
        report_lines.append("")
    
    # Recommended Sites
    recommended_sites = state.get("recommended_sites", [])
    if recommended_sites:
        report_lines.append("RECOMMENDED SITES:")
        report_lines.append("")
        
        for site in recommended_sites[:7]:
            report_lines.append(f"#{site['rank']} - {site['site_name']} (Score: {site['score']:.2f})")
            report_lines.append(f"    Site ID: {site['site_id']}")
            report_lines.append(f"    Reasoning: {site['reasoning']}")
            
            if site.get('key_strengths'):
                report_lines.append("    Key Strengths:")
                for strength in site['key_strengths']:
                    report_lines.append(f"      • {strength}")
            
            if site.get('concerns'):
                report_lines.append("    Concerns:")
                for concern in site['concerns']:
                    report_lines.append(f"      • {concern}")
            
            patient_pool = site.get('patient_pool_match', {})
            if patient_pool:
                report_lines.append("    Patient Pool:")
                report_lines.append(f"      • Estimated Eligible: {patient_pool.get('estimated_eligible_patients', 'N/A')}")
                report_lines.append(f"      • Region: {patient_pool.get('region', 'N/A')}")
            
            historical = site.get('historical_performance', {})
            if historical:
                report_lines.append("    Historical Performance:")
                report_lines.append(f"      • Enrollment Rate: {historical.get('avg_enrollment_rate', 'N/A')}")
                report_lines.append(f"      • Retention Rate: {historical.get('retention_rate', 'N/A')}")
                report_lines.append(f"      • Completed Trials: {historical.get('completed_trials', 'N/A')}")
            
            report_lines.append("")
    
    # Error message if any
    if state.get("error_message"):
        report_lines.append("ERROR:")
        report_lines.append(f"  {state['error_message']}")
        report_lines.append("")
    
    # Audit Trail Summary
    audit_trail = state.get("audit_trail", [])
    if audit_trail:
        report_lines.append(f"AUDIT TRAIL: ({len(audit_trail)} entries)")
        for entry in audit_trail:
            timestamp = entry.get('timestamp', 'N/A')
            node = entry.get('node', 'N/A')
            action = entry.get('action', 'N/A')
            summary = entry.get('results_summary', 'N/A')
            report_lines.append(f"  [{timestamp}] {node}: {action}")
            if summary and summary != 'N/A':
                report_lines.append(f"    → {summary}")
        report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append(f"Report generated at: {datetime.utcnow().isoformat()}")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)


def format_json_report(state: TrialSiteSelectionState) -> dict:
    """
    Format the final state as a JSON report.
    
    Args:
        state: Final agent state
        
    Returns:
        Formatted report as dictionary
    """
    return {
        "user_query": state.get("user_query"),
        "trial_requirements": state.get("trial_requirements"),
        "recommended_sites": state.get("recommended_sites", []),
        "analysis_summary": state.get("analysis_summary"),
        "audit_trail": state.get("audit_trail", []),
        "error_message": state.get("error_message"),
        "data_sources": {
            "patient_pools_analyzed": len(state.get("patient_demographics", {}).get("pools", [])),
            "sites_analyzed": len(state.get("site_performance_data", {}).get("sites", [])),
        },
        "generated_at": datetime.utcnow().isoformat()
    }
