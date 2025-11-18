#!/usr/bin/env python3
"""
Main entry point for the Clinical Trial Site Selection Agent.

This script provides both a command-line interface and REST API to run the agent.
"""

import os
import sys
import logging
import argparse
import json
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import run_agent
from src.nodes import format_report, format_json_report
from src.auth import validate_token, security, set_jwks_url

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# FastAPI app
app = FastAPI(
    title="Clinical Trial Site Selection Agent API",
    description="API for running clinical trial site selection queries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    format: Optional[str] = "text"  # "text" or "json"


class QueryResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


# Configure JWKS URL for authentication
jwks_url = os.getenv("JWKS_URL")
if jwks_url:
    set_jwks_url(jwks_url)
    logger.info(f"JWKS URL configured: {jwks_url}")
else:
    logger.warning("JWKS_URL not set - API endpoints will not require authentication")


# API endpoints
@app.post("/api/query", response_model=QueryResponse)
async def run_query(request: QueryRequest, token_payload: dict = Depends(validate_token)):
    """
    Run a clinical trial site selection query.

    - **query**: The clinical trial site selection query
    - **format**: Response format ("text" or "json")
    """
    try:
        logger.info(f"API request: {request.query}")

        # Run the agent
        final_state = run_agent(request.query)

        # Check for errors
        if final_state.get("error_message"):
            logger.error(f"Agent error: {final_state['error_message']}")
            raise HTTPException(status_code=400, detail=final_state['error_message'])

        # Format output
        result = format_json_report(final_state)
        logger.info("Query completed successfully. Returning JSON formatted report")

        return QueryResponse(success=True, result=result)

    except Exception as e:
        logger.exception("Error processing query")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "clinical-trial-agent"}


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clinical Trial Site Selection Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py

  # Direct query
  python main.py --query "Find sites for Phase III Type 2 Diabetes trial in Northeast"

  # Output as JSON
  python main.py --query "Find sites..." --json --output results.json

  # Start API server
  python main.py --api --host 0.0.0.0 --port 8000
        """
    )

    parser.add_argument(
        "--query",
        type=str,
        help="Clinical trial site selection query"
    )

    parser.add_argument(
        "--api",
        action="store_true",
        help="Start the API server instead of running a single query"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="API server host (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--demographics-url",
        type=str,
        default=os.getenv("DEMOGRAPHICS_SERVER_URL", "http://localhost:4001/mcp"),
        help="Patient Demographics MCP server URL"
    )
    
    parser.add_argument(
        "--performance-url",
        type=str,
        default=os.getenv("PERFORMANCE_SERVER_URL", "http://localhost:4002/mcp"),
        help="Site Performance MCP server URL"
    )
    
    parser.add_argument(
        "--jwks-url",
        type=str,
        default=os.getenv("JWKS_URL"),
        help="JWKS URL for OAuth 2.0 token validation (required for API mode)"
    )
    
    args = parser.parse_args()

    # Set environment variables for MCP clients and JWKS
    os.environ["DEMOGRAPHICS_SERVER_URL"] = args.demographics_url
    os.environ["PERFORMANCE_SERVER_URL"] = args.performance_url
    
    if args.jwks_url:
        os.environ["JWKS_URL"] = args.jwks_url

    # Start API server if requested
    if args.api:
        logger.info(f"Starting API server on {args.host}:{args.port}")
        print(f"🚀 Starting Clinical Trial Site Selection Agent API")
        print(f"📡 Server will be available at: http://{args.host}:{args.port}")
        print(f"📚 API documentation: http://{args.host}:{args.port}/docs")
        print(f"🔍 Health check: http://{args.host}:{args.port}/api/health")
        print("\nPress Ctrl+C to stop the server\n")

        if args.jwks_url:
            print("JWKS_URL set to: " + args.jwks_url)

        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=False,
            log_level="info"
        )
        return

    # Set environment variables for MCP clients (already done above)
    # os.environ["DEMOGRAPHICS_SERVER_URL"] = args.demographics_url
    # os.environ["PERFORMANCE_SERVER_URL"] = args.performance_url
    
    # if args.jwks_url:
    #     os.environ["JWKS_URL"] = args.jwks_url
    #     logger.info("JWKS_URL set to: " + os.getenv("JWKS_URL", "Not Set"))

    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("GOOGLE_API_KEY environment variable not set")
        print("Error: Please set GOOGLE_API_KEY environment variable")
        sys.exit(1)
    
    # Check JWKS URL for API mode
    if args.api and not os.getenv("JWKS_URL"):
        logger.error("JWKS_URL environment variable not set. Use --jwks-url or set JWKS_URL env var")
        print("Error: Please set JWKS_URL environment variable or provide --jwks-url for API mode")
        sys.exit(1)
    
    # Get query
    if args.query:
        query = args.query
    else:
        # Interactive mode
        print("=" * 80)
        print("Clinical Trial Site Selection Agent")
        print("=" * 80)
        print("\nEnter your query (or 'quit' to exit):")
        print("\nExample queries:")
        print("  - Find sites for Phase III Type 2 Diabetes trial in Northeast US")
        print("  - I need sites for Phase II lung cancer trial in California")
        print("  - Looking for sites with metabolic disorder experience, any US location")
        print("\nQuery: ", end="")
        
        query = input().strip()
        
        if query.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            sys.exit(0)
        
        if not query:
            print("Error: Empty query")
            sys.exit(1)
    
    # Run agent
    logger.info(f"Processing query: {query}")
    print("\n🔍 Analyzing your request...")
    print("⏳ This may take 30-60 seconds...\n")
    
    try:
        final_state = run_agent(query)
        
        # Check for errors
        if final_state.get("error_message"):
            logger.error(f"Agent error: {final_state['error_message']}")
            print(f"\n❌ Error: {final_state['error_message']}")
            sys.exit(1)
        
        # Format output
        if args.json:
            output = json.dumps(format_json_report(final_state), indent=2)
        else:
            output = format_report(final_state)
        
        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output)
            print(f"\n✅ Results saved to: {output_path}")
            logger.info(f"Results written to {output_path}")
        else:
            print("\n")
            print(output)
        
        # Print summary
        recommended_count = len(final_state.get("recommended_sites", []))
        print(f"\n✅ Analysis complete: {recommended_count} sites recommended")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        logger.exception("Error running agent")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
