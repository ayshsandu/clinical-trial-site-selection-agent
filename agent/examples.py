#!/usr/bin/env python3
"""
Example script demonstrating the Clinical Trial Site Selection Agent.

This shows how to use the agent programmatically.
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Import agent components
from src.agent import run_agent
from src.nodes import format_report, format_json_report


def example_1_basic_query():
    """Example 1: Basic query with text output."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Query")
    print("=" * 80)
    
    query = "Find sites for Phase III Type 2 Diabetes trial in Northeast US"
    print(f"\nQuery: {query}\n")
    
    # Run agent
    result = run_agent(query)
    
    # Format and print report
    report = format_report(result)
    print(report)
    
    return result


def example_2_json_output():
    """Example 2: Query with JSON output."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: JSON Output")
    print("=" * 80)
    
    query = "I need sites for Phase II lung cancer trial in California"
    print(f"\nQuery: {query}\n")
    
    # Run agent
    result = run_agent(query)
    
    # Format as JSON
    json_report = format_json_report(result)
    print(json.dumps(json_report, indent=2))
    
    return result


def example_3_programmatic_access():
    """Example 3: Programmatic access to results."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Programmatic Access")
    print("=" * 80)
    
    query = "Find sites with metabolic disorder experience"
    print(f"\nQuery: {query}\n")
    
    # Run agent
    result = run_agent(query)
    
    # Access specific fields
    requirements = result.get("trial_requirements", {})
    sites = result.get("recommended_sites", [])
    
    print(f"Disease: {requirements.get('disease')}")
    print(f"Found {len(sites)} recommended sites:\n")
    
    for site in sites[:3]:  # Top 3
        print(f"  {site['rank']}. {site['site_name']}")
        print(f"     Score: {site['score']:.2f}")
        print(f"     {site['reasoning'][:100]}...")
        print()
    
    return result


def example_4_error_handling():
    """Example 4: Error handling."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Error Handling")
    print("=" * 80)
    
    query = "Find sites for trial"  # Vague query
    print(f"\nQuery: {query}\n")
    
    try:
        result = run_agent(query)
        
        if result.get("error_message"):
            print(f"⚠️  Agent encountered an error: {result['error_message']}")
            print("\nAudit trail:")
            for entry in result.get("audit_trail", [])[-3:]:
                print(f"  - {entry['node']}: {entry['results_summary']}")
        else:
            print("✅ Query processed successfully")
            print(f"   Recommended {len(result['recommended_sites'])} sites")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return result


def example_5_save_to_file():
    """Example 5: Save results to files."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Save to Files")
    print("=" * 80)
    
    query = "Phase III hypertension trial in major metro areas"
    print(f"\nQuery: {query}\n")
    
    # Run agent
    result = run_agent(query)
    
    # Save text report
    text_file = Path("example_report.txt")
    text_file.write_text(format_report(result))
    print(f"✅ Text report saved to: {text_file}")
    
    # Save JSON report
    json_file = Path("example_results.json")
    json_file.write_text(json.dumps(format_json_report(result), indent=2))
    print(f"✅ JSON results saved to: {json_file}")
    
    return result


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("Clinical Trial Site Selection Agent - Examples")
    print("=" * 80)
    
    # Check prerequisites
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n❌ Error: GOOGLE_API_KEY not set")
        print("   Please set your API key in .env file")
        return
    
    print("\n📋 Running 5 examples...")
    print("   This will take a few minutes...\n")
    
    try:
        # Run examples
        example_1_basic_query()
        input("\nPress Enter to continue to Example 2...")
        
        example_2_json_output()
        input("\nPress Enter to continue to Example 3...")
        
        example_3_programmatic_access()
        input("\nPress Enter to continue to Example 4...")
        
        example_4_error_handling()
        input("\nPress Enter to continue to Example 5...")
        
        example_5_save_to_file()
        
        print("\n" + "=" * 80)
        print("✅ All examples completed!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.exception("Example failed")


if __name__ == "__main__":
    main()
