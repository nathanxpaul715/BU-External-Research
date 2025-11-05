"""Agent 3: Use Case Enricher
Enriches each use case with all required sections using BU Intelligence context and research data
"""
import json
import time
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
from utils.rag_tools import get_rag_context_for_use_case, is_rag_available


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

        # Limit BU intelligence to reduce token usage
        bu_context = bu_intelligence[:6000] if len(bu_intelligence) > 6000 else bu_intelligence

        # Format research data concisely
        research_summary = self._format_research_summary(research_data)

        prompt = f"""You are a Senior Management Consultant enriching an AI use case. Return ONLY valid JSON.

USE CASE:
Name: {use_case['original_name']}
Function: {use_case['function']}
Description: {use_case['original_description']}
Tools: {use_case['ai_tools']}
Stage: {use_case['stage']}

CONTEXT: {bu_context[:3000]}

RESEARCH: {research_summary}

Return JSON with this EXACT structure (each field must contain properly formatted text with sub-headings):

{{
  "enriched_name": "AI-Powered [descriptive name]",
  "detailed_description": "Business Context & Problem:\\n[3-5 sentences with metrics]\\n\\nSolution & Technology:\\n[3-5 sentences]\\n\\nIntegration & Process:\\n[3-5 sentences]\\n\\nCurrent Status & Outcomes:\\n[3-5 sentences with current metrics]",
  "business_outcomes": "Productivity & Efficiency:\\n[3-5 sentences with % improvements]\\n\\nQuality & Consistency:\\n[3-5 sentences with metrics]\\n\\nCost & Financial Impact:\\n[3-5 sentences with $ amounts]\\n\\nStrategic Benefits:\\n[3-5 sentences]",
  "industry_alignment": "Competitive Landscape:\\n[3-5 sentences naming 2-3 competitors like LexisNexis, Bloomberg Law]\\n\\nTechnology & Vendors:\\n[3-5 sentences naming vendors like OpenAI, Anthropic, Cohere]\\n\\nIndustry Benchmarks:\\n[3-5 sentences with quantified benchmarks]\\n\\nStrategic Positioning:\\n[3-5 sentences]",
  "implementation": "Technical & Integration:\\n[3-5 sentences on technical approach]\\n\\nChange Management:\\n[3-5 sentences on adoption]\\n\\nRisk & Compliance:\\n[3-5 sentences on risks]\\n\\nOperational & Scaling:\\n[3-5 sentences on scaling]",
  "kpis": "Operational Metrics:\\n- Time savings: [X%]\\n- Volume increase: [X%]\\n\\nFinancial Metrics:\\n- Cost reduction: [$X]\\n- ROI: [X%]\\n\\nQuality Metrics:\\n- Accuracy: [X%]\\n- Consistency: [X%]\\n\\nStrategic Metrics:\\n- Market position\\n- Competitive advantage",
  "annotation": "Source:\\n- BU Intelligence Document\\n- {research_summary[:100]}\\n\\nConfidence Level: Medium\\n\\nRationale: Based on BU context and competitive research\\n\\nInformation Gaps: Need actual implementation metrics and ROI data"
}}

CRITICAL RULES:
1. Return ONLY the JSON object - no markdown, no ```json blocks
2. Start with {{ and end with }}
3. Use \\n\\n for paragraph breaks between sub-headings
4. Include specific numbers, percentages, and competitor names
5. Each sub-heading MUST start with exact label followed by colon

Begin JSON response:"""

        return prompt

    def _format_research_summary(self, research_data: Dict[str, Any]) -> str:
        """Format research data concisely"""
        summary_parts = []

        comp_intel = research_data.get('competitor_intelligence', {})
        if comp_intel:
            summary_parts.append(f"Competitors: {str(comp_intel)[:200]}")

        vendors = research_data.get('vendor_solutions', {})
        if vendors:
            summary_parts.append(f"Vendors: {str(vendors)[:200]}")

        benchmarks = research_data.get('industry_benchmarks', {})
        if benchmarks:
            summary_parts.append(f"Benchmarks: {str(benchmarks)[:200]}")

        return "; ".join(summary_parts)[:500]

    def _clean_json_response(self, response_text: str) -> str:
        """Clean and extract JSON from response text"""
        import re

        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)

        # Find JSON object
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json_match.group(0)

        return response_text

    def enrich_use_case(
        self,
        use_case: Dict[str, Any],
        bu_intelligence: str,
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enrich a single use case"""
        print(f"  Enriching: {use_case['original_name']}")

        # Use RAG-enhanced context if available, otherwise use provided bu_intelligence
        if is_rag_available():
            bu_context = get_rag_context_for_use_case(use_case, context_type="enrichment")
            if bu_context:
                print(f"  [RAG] Using {len(bu_context)} chars of RAG-enhanced context")
            else:
                bu_context = bu_intelligence[:6000]
                print(f"  [Fallback] Using truncated BU intelligence")
        else:
            bu_context = bu_intelligence
            print(f"  [Standard] Using provided BU intelligence")

        prompt = self._create_enrichment_prompt(use_case, bu_context, research_data)

        try:
            # Use reduced max_tokens to stay under rate limit
            message = self.api_client.create_message(
                model=MODEL,
                max_tokens=4000,  # Reduced from MAX_TOKENS to avoid rate limits
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            # Clean and extract JSON
            cleaned_json = self._clean_json_response(response_text)

            # Try to parse as JSON
            try:
                enriched_data = json.loads(cleaned_json)
                print(f"    [OK] Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                print(f"    ! Warning: Could not parse JSON: {e}")
                print(f"    ! Response preview: {response_text[:300]}...")

                # Create default structure with error info
                enriched_data = {
                    "enriched_name": use_case['original_name'],
                    "detailed_description": f"ERROR: Failed to parse LLM response.\n\nRaw response:\n{response_text[:800]}",
                    "business_outcomes": "ERROR: JSON parsing failed",
                    "industry_alignment": "ERROR: JSON parsing failed",
                    "implementation": "ERROR: JSON parsing failed",
                    "kpis": "ERROR: JSON parsing failed",
                    "annotation": f"Source: Parse Error\nConfidence Level: Low\nRationale: Could not extract JSON from LLM response\nInformation Gaps: Full re-enrichment needed"
                }

            # Validate required fields
            required_fields = ['enriched_name', 'detailed_description', 'business_outcomes',
                              'industry_alignment', 'implementation', 'kpis', 'annotation']
            for field in required_fields:
                if field not in enriched_data:
                    enriched_data[field] = f"ERROR: Missing field {field}"

            return {
                "success": True,
                "original_use_case": use_case,
                "enriched_data": enriched_data
            }

        except Exception as e:
            print(f"    [ERROR] Error enriching use case: {e}")
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

            # Add delay between use cases to avoid rate limiting
            # With 4000 tokens output + ~2000 input = ~6000 tokens per call
            # At 100k tokens/min limit, wait ~4 seconds between calls to be safe
            # Use 30 seconds to be extra conservative and avoid rate limits
            if i < len(use_cases) - 1:  # Don't wait after the last one
                print(f"  [THROTTLE] Waiting 30s before next enrichment to avoid rate limits...")
                time.sleep(30)

        print("\n[OK] USE CASE ENRICHMENT COMPLETE")
        print("=" * 80)

        return {
            "enriched_use_cases": enriched_use_cases,
            "total_enriched": len(enriched_use_cases)
        }


if __name__ == "__main__":
    print("Use Case Enricher Agent - requires ingestion and research data to run")
