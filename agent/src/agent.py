"""Clinical Trial Site Selection Agent using LangGraph."""

import logging
from langgraph.graph import StateGraph, END
from .state import TrialSiteSelectionState
from .nodes import (
    parse_requirements,
    query_demographics,
    query_performance,
    analyze_and_rank,
    generate_report,
)

logger = logging.getLogger(__name__)


def create_agent() -> StateGraph:
    """
    Create the Clinical Trial Site Selection Agent graph.
    
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Creating Clinical Trial Site Selection Agent")
    
    # Create workflow
    workflow = StateGraph(TrialSiteSelectionState)
    
    # Add nodes
    workflow.add_node("parse_requirements", parse_requirements)
    workflow.add_node("query_demographics", query_demographics)
    workflow.add_node("query_performance", query_performance)
    workflow.add_node("analyze_and_rank", analyze_and_rank)
    workflow.add_node("generate_report", generate_report)
    
    # Set entry point
    workflow.set_entry_point("parse_requirements")
    
    # Add edges (linear flow)
    workflow.add_edge("parse_requirements", "query_demographics")
    workflow.add_edge("query_demographics", "query_performance")
    workflow.add_edge("query_performance", "analyze_and_rank")
    workflow.add_edge("analyze_and_rank", "generate_report")
    workflow.add_edge("generate_report", END)
    
    # Compile workflow
    app = workflow.compile()
    
    logger.info("Agent workflow created successfully")
    
    return app


def run_agent(user_query: str) -> TrialSiteSelectionState:
    """
    Run the agent with a user query.
    
    Args:
        user_query: User's clinical trial site selection query
        
    Returns:
        Final state with recommendations
    """
    logger.info(f"Running agent with query: {user_query}")
    
    # Create agent
    app = create_agent()
    
    # Initial state
    initial_state: TrialSiteSelectionState = {
        "user_query": user_query,
        "trial_requirements": None,
        "patient_demographics": None,
        "site_performance_data": None,
        "recommended_sites": [],
        "analysis_summary": "",
        "audit_trail": [],
        "error_message": None,
        "iteration_count": 0,
    }
    
    # Run workflow
    final_state = app.invoke(initial_state)
    
    logger.info("Agent execution complete")
    
    return final_state


async def run_agent_async(user_query: str) -> TrialSiteSelectionState:
    """
    Run the agent asynchronously with a user query.
    
    Args:
        user_query: User's clinical trial site selection query
        
    Returns:
        Final state with recommendations
    """
    logger.info(f"Running agent asynchronously with query: {user_query}")
    
    # Create agent
    app = create_agent()
    
    # Initial state
    initial_state: TrialSiteSelectionState = {
        "user_query": user_query,
        "trial_requirements": None,
        "patient_demographics": None,
        "site_performance_data": None,
        "recommended_sites": [],
        "analysis_summary": "",
        "audit_trail": [],
        "error_message": None,
        "iteration_count": 0,
    }
    
    # Run workflow asynchronously
    final_state = await app.ainvoke(initial_state)
    
    logger.info("Agent execution complete")
    
    return final_state
