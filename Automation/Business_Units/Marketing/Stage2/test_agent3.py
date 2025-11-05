"""Test script for Agent 3 - Use Case Enricher
Tests a single use case enrichment to validate JSON output and formatting
"""
import json
import sys
from agents.agent3_use_case_enricher import UseCaseEnricherAgent

def test_agent3():
    """Test Agent 3 with a single use case"""

    print("=" * 80)
    print("TESTING AGENT 3: USE CASE ENRICHER")
    print("=" * 80)

    # Sample use case
    test_use_case = {
        "original_name": "Marketing Content Generation",
        "function": "Marketing",
        "original_description": "AI-powered content creation for marketing campaigns",
        "original_outcomes": "Faster content creation, improved consistency",
        "ai_tools": "GPT-4, Claude",
        "stage": "Production",
        "strategy": "Enhance productivity"
    }

    # Sample BU intelligence (shortened for testing)
    test_bu_intelligence = """
    Thomson Reuters Marketing function serves Legal, Tax & Accounting, and Corporate segments.
    The team focuses on customer acquisition and retention through personalized campaigns.
    Current challenges include content creation speed and maintaining brand consistency.
    Budget: $50M annually. Team size: 200+ marketing professionals.
    """

    # Sample research data
    test_research_data = {
        "competitor_intelligence": {
            "summary": "LexisNexis uses Harvey AI for content. Bloomberg Law has AI research tools."
        },
        "vendor_solutions": {
            "summary": "OpenAI GPT-4, Anthropic Claude, Cohere for enterprise content generation."
        },
        "industry_benchmarks": {
            "summary": "30-40% time savings typical. ROI of 200-300% within first year."
        }
    }

    # Initialize agent
    agent = UseCaseEnricherAgent()

    # Run enrichment
    print("\nEnriching test use case...")
    result = agent.enrich_use_case(test_use_case, test_bu_intelligence, test_research_data)

    # Display results
    print("\n" + "=" * 80)
    print("ENRICHMENT RESULTS")
    print("=" * 80)

    if result["success"]:
        print("[OK] Enrichment successful")
        enriched_data = result["enriched_data"]

        print("\n--- Enriched Name ---")
        print(enriched_data.get("enriched_name", "N/A"))

        print("\n--- Detailed Description (first 500 chars) ---")
        desc = enriched_data.get("detailed_description", "N/A")
        print(desc[:500] + ("..." if len(desc) > 500 else ""))

        print("\n--- Business Outcomes (first 500 chars) ---")
        outcomes = enriched_data.get("business_outcomes", "N/A")
        print(outcomes[:500] + ("..." if len(outcomes) > 500 else ""))

        print("\n--- Industry Alignment (first 500 chars) ---")
        industry = enriched_data.get("industry_alignment", "N/A")
        print(industry[:500] + ("..." if len(industry) > 500 else ""))

        # Check for required sub-headings
        print("\n" + "=" * 80)
        print("VALIDATION CHECKS")
        print("=" * 80)

        checks = [
            ("Detailed Description", desc, ["Business Context & Problem", "Solution & Technology",
                                           "Integration & Process", "Current Status & Outcomes"]),
            ("Business Outcomes", outcomes, ["Productivity & Efficiency", "Quality & Consistency",
                                           "Cost & Financial Impact", "Strategic Benefits"]),
            ("Industry Alignment", industry, ["Competitive Landscape", "Technology & Vendors",
                                            "Industry Benchmarks", "Strategic Positioning"])
        ]

        for section_name, section_text, required_headings in checks:
            print(f"\n{section_name}:")
            for heading in required_headings:
                present = heading in section_text or f"{heading}:" in section_text
                status = "[OK]" if present else "[FAIL]"
                print(f"  {status} {heading}")

        # Save full output to file
        output_file = "test_agent3_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Full output saved to: {output_file}")

    else:
        print("[FAIL] Enrichment failed")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return False

    return True

if __name__ == "__main__":
    try:
        success = test_agent3()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
