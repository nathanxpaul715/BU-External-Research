"""Agent 3: Use Case Enricher
Enriches each use case with all required sections using BU Intelligence context and research data
"""
import json
from typing import Dict, List, Any
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    ANTHROPIC_API_URL,
    WORKSPACE_ID,
    MODEL,
    SUB_HEADINGS,
    MAX_TOKENS
)
from utils.api_client import get_api_client


class UseCaseEnricherAgent:
    """Agent responsible for enriching use cases with consulting-grade content"""

    def __init__(self):
        self.api_client = get_api_client(WORKSPACE_ID, ANTHROPIC_API_URL)

    def _create_enrichment_prompt(
        self,
        use_case: Dict[str, Any],
        bu_intelligence: str,
        research_data: Dict[str, Any]
    ) -> str:
        """Create comprehensive enrichment prompt"""

        prompt = f"""You are a Senior Management Consultant (15+ years, McKinsey/BCG caliber) tasked with enriching an AI use case to premium consulting quality.

=== USE CASE TO ENRICH ===
Original Name: {use_case['original_name']}
Function: {use_case['function']}
Original Description: {use_case['original_description']}
Original Outcomes: {use_case['original_outcomes']}
AI Tools: {use_case['ai_tools']}
Stage: {use_case['stage']}
Strategy: {use_case['strategy']}

=== BUSINESS CONTEXT (BU Intelligence Foundation) ===
{bu_intelligence[:8000]}
[... full context available ...]

=== EXTERNAL RESEARCH DATA ===
Competitor Intelligence:
{json.dumps(research_data.get('competitor_intelligence', {}), indent=2)}

Vendor Solutions:
{json.dumps(research_data.get('vendor_solutions', {}), indent=2)}

Industry Benchmarks:
{json.dumps(research_data.get('industry_benchmarks', {}), indent=2)}

=== YOUR TASK ===
Enrich this use case with consulting-grade content for the following sections. Each section MUST use the specified sub-headings and provide 3-5 quantified, detailed sentences per sub-heading.

**Section 1: Detailed Enriched Use Case Description**
Sub-headings:
- Business Context & Problem:
- Solution & Technology:
- Integration & Process:
- Current Status & Outcomes:

**Section 2: Enriched Business Outcomes/Deliverables**
Sub-headings:
- Productivity & Efficiency:
- Quality & Consistency:
- Cost & Financial Impact:
- Strategic Benefits:

**Section 3: Industry Alignment**
Sub-headings:
- Competitive Landscape: (MUST include at least 2-3 named competitors)
- Technology & Vendors: (MUST include specific vendor names and products)
- Industry Benchmarks: (MUST include quantified metrics with sources)
- Strategic Positioning:

**Section 4: Implementation Considerations**
Sub-headings:
- Technical & Integration:
- Change Management:
- Risk & Compliance:
- Operational & Scaling:

**Section 5: Suggested Success Metrics (KPIs)**
Sub-headings:
- Operational Metrics:
- Financial Metrics:
- Quality Metrics:
- Strategic Metrics:

**Section 6: Information Gaps & Annotation**
Sub-headings:
- Source: (List all sources - BU Intelligence, web URLs, reports)
- Confidence Level: (High/Medium/Low with rationale)
- Rationale: (Explain methodology and data quality)
- Information Gaps: (What data is missing or needs validation)

=== CRITICAL REQUIREMENTS ===
1. Start each sub-heading with the exact label followed by a colon
2. Provide 3-5 substantive, quantified sentences per sub-heading
3. Include specific metrics, competitor names, vendor names, and benchmarks
4. All external claims must reference sources
5. Maintain consulting-grade quality and depth throughout

=== OUTPUT FORMAT ===
Provide your response as a JSON object with these keys:
{{
  "enriched_name": "Enhanced name for the use case",
  "detailed_description": "Full section 1 content with all sub-headings",
  "business_outcomes": "Full section 2 content with all sub-headings",
  "industry_alignment": "Full section 3 content with all sub-headings",
  "implementation": "Full section 4 content with all sub-headings",
  "kpis": "Full section 5 content with all sub-headings",
  "annotation": "Full section 6 content with all sub-headings"
}}

Begin your enrichment now:"""

        return prompt

    def enrich_use_case(
        self,
        use_case: Dict[str, Any],
        bu_intelligence: str,
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enrich a single use case"""
        print(f"  Enriching: {use_case['original_name']}")

        prompt = self._create_enrichment_prompt(use_case, bu_intelligence, research_data)

        try:
            message = self.api_client.create_message(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            # Try to parse as JSON, fallback to raw text
            try:
                enriched_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If not JSON, create structured output from text
                enriched_data = {
                    "enriched_name": use_case['original_name'],
                    "detailed_description": response_text,
                    "business_outcomes": "",
                    "industry_alignment": "",
                    "implementation": "",
                    "kpis": "",
                    "annotation": "Source: BU Intelligence, Claude enrichment\nConfidence Level: Medium\nRationale: Generated from provided context\nInformation Gaps: May require additional validation"
                }

            return {
                "success": True,
                "original_use_case": use_case,
                "enriched_data": enriched_data
            }

        except Exception as e:
            print(f"    ✗ Error enriching use case: {e}")
            return {
                "success": False,
                "original_use_case": use_case,
                "error": str(e)
            }

    def run(
        self,
        ingestion_data: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute enrichment for all use cases"""
        print("=" * 80)
        print("AGENT 3: USE CASE ENRICHER")
        print("=" * 80)

        use_cases = ingestion_data["use_cases"]
        bu_intelligence = ingestion_data["bu_intelligence"]
        research_results = research_data.get("research_results", [])

        enriched_use_cases = []
        for i, use_case in enumerate(use_cases):
            # Match research data to use case
            research_for_case = research_results[i] if i < len(research_results) else {}

            enriched = self.enrich_use_case(use_case, bu_intelligence, research_for_case)
            enriched_use_cases.append(enriched)

        print("\n✓ USE CASE ENRICHMENT COMPLETE")
        print("=" * 80)

        return {
            "enriched_use_cases": enriched_use_cases,
            "total_enriched": len(enriched_use_cases)
        }


if __name__ == "__main__":
    print("Use Case Enricher Agent - requires ingestion and research data to run")
