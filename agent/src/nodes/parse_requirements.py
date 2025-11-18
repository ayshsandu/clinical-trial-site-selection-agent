"""Node for parsing trial requirements from user query."""

import logging
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..state import TrialSiteSelectionState, AuditEntry
import json

logger = logging.getLogger(__name__)


PARSE_REQUIREMENTS_PROMPT = """You are an expert clinical trial coordinator. Extract structured information from the user's query about finding clinical trial sites.

Extract the following information:
- disease: The disease or condition being studied
- indication: More specific indication if mentioned
- phase: Trial phase (e.g., "Phase I", "Phase II", "Phase III")
- target_enrollment: Target number of patients
- geographic_preferences: List of preferred geographic regions/locations
- therapeutic_area: Therapeutic area (e.g., "Oncology", "Cardiology", "Endocrinology")
- min_site_capacity: Minimum site capacity if mentioned
- special_requirements: Any special equipment, certifications, or capabilities needed

Return ONLY valid JSON with these fields. Use null for fields not mentioned in the query.

Example query: "Find sites for a Phase III Type 2 Diabetes trial targeting 200 patients in the Northeast US with strong endocrinology departments"

Example output:
{{
  "disease": "Type 2 Diabetes",
  "indication": "Type 2 Diabetes",
  "phase": "Phase III",
  "target_enrollment": 200,
  "geographic_preferences": ["US-Northeast"],
  "therapeutic_area": "Endocrinology",
  "min_site_capacity": null,
  "special_requirements": ["strong endocrinology departments"]
}}

User query: {query}

Return ONLY the JSON object, no other text."""


def parse_requirements(state: TrialSiteSelectionState) -> TrialSiteSelectionState:
    """
    Parse trial requirements from user query using LLM.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with parsed requirements
    """
    logger.info("Parsing trial requirements from user query")
    
    user_query = state["user_query"]
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )
    
    # Create prompt
    prompt = PARSE_REQUIREMENTS_PROMPT.format(query=user_query)
    
    try:
        # Call LLM
        messages = [
            SystemMessage(content="You are a clinical trial requirements parser. Return only valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        logger.info(f"LLM response received for requirements parsing: {response_text}")
        # Parse JSON response
        # Handle potential markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        requirements = json.loads(response_text)
        
        logger.info(f"Parsed requirements: {requirements}")
        
        # Create audit entry
        audit_entry: AuditEntry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": "parse_requirements",
            "action": "Parse trial requirements from query",
            "server": None,
            "tool": None,
            "parameters": {"query": user_query},
            "results_summary": f"Extracted {len([k for k, v in requirements.items() if v is not None])} fields"
        }
        
        # Update state
        return {
            **state,
            "trial_requirements": requirements,
            "audit_trail": state.get("audit_trail", []) + [audit_entry],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from LLM response: {e}")
        logger.error(f"Response was: {response_text}")
        
        # Create error audit entry
        audit_entry: AuditEntry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": "parse_requirements",
            "action": "Parse trial requirements from query",
            "server": None,
            "tool": None,
            "parameters": {"query": user_query},
            "results_summary": f"ERROR: Failed to parse JSON - {str(e)}"
        }
        
        return {
            **state,
            "error_message": f"Failed to parse requirements: {str(e)}",
            "audit_trail": state.get("audit_trail", []) + [audit_entry],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    
    except Exception as e:
        logger.error(f"Error parsing requirements: {e}")
        
        # Create error audit entry
        audit_entry: AuditEntry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": "parse_requirements",
            "action": "Parse trial requirements from query",
            "server": None,
            "tool": None,
            "parameters": {"query": user_query},
            "results_summary": f"ERROR: {str(e)}"
        }
        
        return {
            **state,
            "error_message": f"Error parsing requirements: {str(e)}",
            "audit_trail": state.get("audit_trail", []) + [audit_entry],
            "iteration_count": state.get("iteration_count", 0) + 1
        }
