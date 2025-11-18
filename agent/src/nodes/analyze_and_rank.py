"""Node for analyzing data and ranking sites using LLM."""

import logging
import json
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..state import TrialSiteSelectionState, SiteRecommendation, AuditEntry

logger = logging.getLogger(__name__)


ANALYSIS_PROMPT = """You are an expert clinical trial site selection consultant. Analyze the provided data and rank the most suitable clinical trial sites.

TRIAL REQUIREMENTS:
{requirements}

PATIENT DEMOGRAPHICS DATA:
{demographics}

SITE PERFORMANCE DATA:
{performance}

Your task:
1. Match each site with relevant patient populations
2. Evaluate historical performance metrics
3. Assess site capabilities against requirements
4. Score each site (0-1.0) based on:
   - Patient population match (40%)
   - Historical performance (30%)
   - Site capabilities (30%)
5. Provide clear reasoning for each recommendation

Return ONLY valid JSON with this structure:
{{
  "recommended_sites": [
    {{
      "rank": 1,
      "site_id": "SITE-001",
      "site_name": "Site Name",
      "score": 0.92,
      "reasoning": "Clear explanation of why this site is recommended",
      "key_strengths": ["strength 1", "strength 2", "strength 3"],
      "concerns": ["concern 1 if any"],
      "patient_pool_match": {{
        "estimated_eligible_patients": 45000,
        "region": "Boston Metropolitan Area",
        "prevalence_rate": 0.087
      }},
      "historical_performance": {{
        "avg_enrollment_rate": 1.08,
        "retention_rate": 0.89,
        "completed_trials": 34
      }}
    }}
  ],
  "analysis_summary": "Overall analysis of the site selection landscape"
}}

Rank the top 5-7 sites. Be specific and data-driven in your reasoning."""


def analyze_and_rank(state: TrialSiteSelectionState) -> TrialSiteSelectionState:
    """
    Analyze data and rank sites using LLM.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with ranked site recommendations
    """
    logger.info("Analyzing data and ranking sites")
    
    requirements = state.get("trial_requirements")
    demographics = state.get("patient_demographics")
    performance = state.get("site_performance_data")
    
    if not all([requirements, demographics, performance]):
        logger.error("Missing required data for analysis")
        return {
            **state,
            "error_message": "Missing data for site analysis"
        }
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )
    
    try:
        # Prepare data summaries for the prompt
        requirements_json = json.dumps(requirements, indent=2)
        
        # Summarize demographics (to fit in context)
        demographics_summary = {
            "total_pools": len(demographics.get("pools", [])),
            "pools": demographics.get("pools", [])[:10],  # Limit to 10 pools
            "regions": demographics.get("regions", [])[:5]  # Limit to 5 regions
        }
        demographics_json = json.dumps(demographics_summary, indent=2)
        
        # Summarize performance data
        performance_summary = {
            "total_sites": len(performance.get("sites", [])),
            "sites": performance.get("sites", []),
            "capabilities": performance.get("capabilities", []),
            "histories": performance.get("histories", [])
        }
        performance_json = json.dumps(performance_summary, indent=2)
        
        # Create prompt
        prompt = ANALYSIS_PROMPT.format(
            requirements=requirements_json,
            demographics=demographics_json,
            performance=performance_json
        )
        
        logger.info("Sending analysis request to LLM")
        
        # Call LLM
        messages = [
            SystemMessage(content="You are a clinical trial site selection expert. Return only valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        logger.debug(f"LLM response: {response_text[:500]}...")
        
        # Parse JSON response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        analysis_result = json.loads(response_text)
        
        recommended_sites = analysis_result.get("recommended_sites", [])
        analysis_summary = analysis_result.get("analysis_summary", "Analysis complete")
        
        logger.info(f"Analysis complete: {len(recommended_sites)} sites ranked")
        
        # Create audit entry
        audit_entry: AuditEntry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": "analyze_and_rank",
            "action": "Analyze data and rank sites",
            "server": None,
            "tool": None,
            "parameters": {
                "sites_analyzed": len(performance.get("sites", [])),
                "pools_analyzed": len(demographics.get("pools", []))
            },
            "results_summary": f"Ranked {len(recommended_sites)} sites"
        }
        
        # Update state
        return {
            **state,
            "recommended_sites": recommended_sites,
            "analysis_summary": analysis_summary,
            "audit_trail": state.get("audit_trail", []) + [audit_entry],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from LLM response: {e}")
        logger.error(f"Response was: {response_text}")
        
        audit_entry: AuditEntry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": "analyze_and_rank",
            "action": "Analyze data and rank sites",
            "server": None,
            "tool": None,
            "parameters": None,
            "results_summary": f"ERROR: Failed to parse JSON - {str(e)}"
        }
        
        return {
            **state,
            "error_message": f"Failed to parse analysis results: {str(e)}",
            "audit_trail": state.get("audit_trail", []) + [audit_entry],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        
        audit_entry: AuditEntry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": "analyze_and_rank",
            "action": "Analyze data and rank sites",
            "server": None,
            "tool": None,
            "parameters": None,
            "results_summary": f"ERROR: {str(e)}"
        }
        
        return {
            **state,
            "error_message": f"Analysis failed: {str(e)}",
            "audit_trail": state.get("audit_trail", []) + [audit_entry],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
