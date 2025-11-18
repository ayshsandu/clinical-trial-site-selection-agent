#!/usr/bin/env python3
"""
Main entry point for the Clinical Trial Site Selection Agent.

This script provides a command-line interface to run the agent.
"""

import os
import sys
import logging
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import run_agent
from src.nodes import format_report, format_json_report

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


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
        """
    )
    
    parser.add_argument(
        "--query",
        type=str,
        help="Clinical trial site selection query"
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
    
    args = parser.parse_args()
    
    # Set environment variables for MCP clients
    os.environ["DEMOGRAPHICS_SERVER_URL"] = args.demographics_url
    os.environ["PERFORMANCE_SERVER_URL"] = args.performance_url
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("GOOGLE_API_KEY environment variable not set")
        print("Error: Please set GOOGLE_API_KEY environment variable")
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
