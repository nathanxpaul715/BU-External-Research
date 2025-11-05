"""Agent 3: RAG-Enhanced Use Case Enricher
Enriches each use case using RAG context, web research, and LLM capabilities
"""
import json
import time
from typing import Dict, List, Any
import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
stage2_dir = os.path.dirname(current_dir)  # Stage2
marketing_dir = os.path.dirname(stage2_dir)  # Marketing
bu_dir = os.path.dirname(marketing_dir)  # Business_Units
automation_dir = os.path.dirname(bu_dir)  # Automation
project_root = os.path.dirname(automation_dir)  # Project root

sys.path.insert(0, stage2_dir)  # For config
sys.path.insert(0, project_root)  # For rag_tool

from config import (
    ANTHROPIC_API_URL,
    WORKSPACE_ID,
    MODEL,
    SUB_HEADINGS,
    MAX_TOKENS
)
from utils.api_client import get_api_client
from rag_tool import get_rag_tool


class RAGUseCaseEnricherAgent:
    """Agent responsible for enriching use cases with RAG-enhanced consulting-grade content"""

    def __init__(self):
        self.api_client = get_api_client(WORKSPACE_ID, ANTHROPIC_API_URL)
        self.rag_tool = get_rag_tool()
        print("[INFO] RAG Use Case Enricher Agent initialized")

    def _create_enrichment_prompt(
        self,
        use_case: Dict[str, Any],
        rag_context: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> str:
        """Create comprehensive enrichment prompt with RAG context"""

        # Extract RAG context elements
        tr_capabilities = rag_context.get("tr_capabilities", "")[:2000]
        tr_initiatives = rag_context.get("tr_initiatives", "")[:2000]
        tr_positioning = rag_context.get("tr_competitive_positioning", "")[:2000]
        gap_analysis = rag_context.get("gap_analysis", "")[:2000]
        market_intel = rag_context.get("market_intelligence", "")[:2000]

        # Extract research data
        research_summary = self._format_research_summary(research_data)
        tr_internal_context = research_data.get('tr_internal_context', '')[:1500]
        gap_context = research_data.get('gap_analysis_context', '')[:1500]

        prompt = f"""You are a Senior Management Consultant enriching an AI use case. Return ONLY valid JSON.

USE CASE:
Name: {use_case['original_name']}
Function: {use_case['function']}
Description: {use_case['original_description']}
Tools: {use_case['ai_tools']}
Stage: {use_case['stage']}

=== INTERNAL TR CONTEXT (From RAG Knowledge Base) ===

TR RESEARCH CAPABILITIES:
{tr_capabilities}

TR STRATEGIC INITIATIVES:
{tr_initiatives}

TR COMPETITIVE POSITIONING:
{tr_positioning}

GAP ANALYSIS:
{gap_analysis}

=== EXTERNAL MARKET CONTEXT (From RAG Knowledge Base) ===

MARKET INTELLIGENCE:
{market_intel}

=== USE CASE-SPECIFIC CONTEXT (From Web Research) ===

TR INTERNAL ALIGNMENT:
{tr_internal_context}

GAP OPPORTUNITIES:
{gap_context}

WEB RESEARCH INSIGHTS:
{research_summary}

=== ENRICHMENT TASK ===

Return JSON with this EXACT structure (each field must contain properly formatted text with sub-headings):

{{
  "enriched_name": "AI-Powered [descriptive name based on TR capabilities and market positioning]",
  "detailed_description": "Business Context & Problem:\\n[3-5 sentences mentioning TR's position and the gap this addresses]\\n\\nSolution & Technology:\\n[3-5 sentences on how TR is implementing this, tools used]\\n\\nIntegration & Process:\\n[3-5 sentences on how this integrates with TR systems]\\n\\nCurrent Status & Outcomes:\\n[3-5 sentences with current metrics from TR context]",
  "business_outcomes": "Productivity & Efficiency:\\n[3-5 sentences with % improvements from benchmarks]\\n\\nQuality & Consistency:\\n[3-5 sentences with metrics]\\n\\nCost & Financial Impact:\\n[3-5 sentences with $ amounts from research]\\n\\nStrategic Benefits:\\n[3-5 sentences on TR strategic alignment]",
  "industry_alignment": "Competitive Landscape:\\n[3-5 sentences naming 2-3 specific competitors from research like LexisNexis, Bloomberg Law, Westlaw]\\n\\nTechnology & Vendors:\\n[3-5 sentences naming specific vendors from research like OpenAI, Anthropic, Cohere]\\n\\nIndustry Benchmarks:\\n[3-5 sentences with quantified benchmarks from research]\\n\\nStrategic Positioning:\\n[3-5 sentences on TR's differentiation based on gap analysis]",
  "implementation": "Technical & Integration:\\n[3-5 sentences on technical approach based on TR capabilities]\\n\\nChange Management:\\n[3-5 sentences on adoption strategy]\\n\\nRisk & Compliance:\\n[3-5 sentences on risks, mentioning TR compliance requirements]\\n\\nOperational & Scaling:\\n[3-5 sentences on scaling within TR ecosystem]",
  "kpis": "Operational Metrics:\\n- Time savings: [X% from benchmarks]\\n- Volume increase: [X% from research]\\n\\nFinancial Metrics:\\n- Cost reduction: [$X from industry data]\\n- ROI: [X% from case studies]\\n\\nQuality Metrics:\\n- Accuracy: [X% improvement]\\n- Consistency: [X% improvement]\\n\\nStrategic Metrics:\\n- Market position enhancement\\n- Competitive advantage gained\\n- Gap closure progress",
  "annotation": "Source:\\n- TR Internal Knowledge Base (RAG)\\n- Gap Analysis (RAG)\\n- Market Intelligence (RAG)\\n- Web Research: {research_summary[:150]}\\n\\nConfidence Level: High (RAG-enhanced)\\n\\nRationale: Based on comprehensive TR internal context from RAG, gap analysis, market intelligence, and competitive web research\\n\\nInformation Gaps: {self._identify_gaps(research_data)}\\n\\nTR Alignment Score: {self._calculate_alignment_score(gap_analysis, tr_capabilities)}/10"
}}

CRITICAL RULES:
1. Return ONLY the JSON object - no markdown, no ```json blocks
2. Start with {{ and end with }}
3. Use \\n\\n for paragraph breaks between sub-headings
4. Include specific numbers, percentages, and names from the research
5. Each sub-heading MUST start with exact label followed by colon
6. Reference TR's capabilities, gaps, and strategic initiatives throughout
7. Use competitor and vendor names from the research data
8. Quantify everything possible with metrics from benchmarks

Begin JSON response:"""

        return prompt

    def _format_research_summary(self, research_data: Dict[str, Any]) -> str:
        """Format research data concisely"""
        summary_parts = []

        comp_intel = research_data.get('competitor_intelligence', {})
        if comp_intel and comp_intel.get('success'):
            summary_parts.append(f"Competitors: {comp_intel.get('data', '')[:300]}")

        vendors = research_data.get('vendor_solutions', {})
        if vendors and vendors.get('success'):
            summary_parts.append(f"Vendors: {vendors.get('data', '')[:300]}")

        benchmarks = research_data.get('industry_benchmarks', {})
        if benchmarks and benchmarks.get('success'):
            summary_parts.append(f"Benchmarks: {benchmarks.get('data', '')[:300]}")

        return " | ".join(summary_parts)[:1500] if summary_parts else "No web research available"

    def _identify_gaps(self, research_data: Dict[str, Any]) -> str:
        """Identify information gaps based on research data"""
        gaps = []

        comp_intel = research_data.get('competitor_intelligence', {})
        if not comp_intel or not comp_intel.get('success'):
            gaps.append("competitor analysis")

        vendors = research_data.get('vendor_solutions', {})
        if not vendors or not vendors.get('success'):
            gaps.append("vendor solutions")

        benchmarks = research_data.get('industry_benchmarks', {})
        if not benchmarks or not benchmarks.get('success'):
            gaps.append("quantified benchmarks")

        if gaps:
            return f"Missing or incomplete: {', '.join(gaps)}"
        else:
            return "No major gaps - comprehensive data available"

    def _calculate_alignment_score(self, gap_analysis: str, tr_capabilities: str) -> int:
        """Calculate a simple alignment score (1-10) based on context availability"""
        score = 5  # Base score

        # Increase score if we have substantial context
        if len(gap_analysis) > 500:
            score += 2
        if len(tr_capabilities) > 500:
            score += 2

        # Cap at 10
        return min(score, 10)

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
        rag_context: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enrich a single use case with RAG context"""
        print(f"  Enriching: {use_case['original_name']}")

        prompt = self._create_enrichment_prompt(use_case, rag_context, research_data)

        try:
            # Use reduced max_tokens to stay under rate limit
            message = self.api_client.create_message(
                model=MODEL,
                max_tokens=4000,
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
                print(f"    [OK] Successfully parsed JSON response with RAG context")
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
                "enriched_data": enriched_data,
                "rag_enhanced": True,
                "context_sources": {
                    "tr_capabilities": len(rag_context.get("tr_capabilities", "")),
                    "gap_analysis": len(rag_context.get("gap_analysis", "")),
                    "market_intel": len(rag_context.get("market_intelligence", "")),
                    "web_research": len(str(research_data))
                }
            }

        except Exception as e:
            print(f"    [ERROR] Error enriching use case: {e}")
            return {
                "success": False,
                "original_use_case": use_case,
                "error": str(e),
                "rag_enhanced": False
            }

    def run(
        self,
        ingestion_data: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute RAG-enhanced enrichment for all use cases"""
        print("=" * 80)
        print("AGENT 3: RAG-ENHANCED USE CASE ENRICHER")
        print("=" * 80)

        use_cases = ingestion_data["use_cases"]
        rag_context = {
            "tr_capabilities": ingestion_data.get("tr_capabilities", ""),
            "tr_initiatives": ingestion_data.get("tr_initiatives", ""),
            "tr_competitive_positioning": ingestion_data.get("tr_positioning", ""),
            "gap_analysis": ingestion_data.get("gap_analysis", ""),
            "market_intelligence": ingestion_data.get("market_intelligence", "")
        }

        research_results = research_data.get("research_results", [])

        enriched_use_cases = []
        for i, use_case in enumerate(use_cases):
            # Match research data to use case
            research_for_case = research_results[i] if i < len(research_results) else {}

            enriched = self.enrich_use_case(use_case, rag_context, research_for_case)
            enriched_use_cases.append(enriched)

            # Add delay between use cases to avoid rate limiting
            if i < len(use_cases) - 1:
                print(f"  [THROTTLE] Waiting 30s before next enrichment to avoid rate limits...")
                time.sleep(30)

        print("\n[OK] RAG-ENHANCED USE CASE ENRICHMENT COMPLETE")
        print(f"  - Enriched {len(enriched_use_cases)} use cases with RAG context")
        print(f"  - Used TR capabilities, gap analysis, and market intelligence")
        print("=" * 80)

        return {
            "enriched_use_cases": enriched_use_cases,
            "total_enriched": len(enriched_use_cases),
            "rag_enhanced": True
        }


if __name__ == "__main__":
    print("RAG-Enhanced Use Case Enricher Agent - requires RAG ingestion and research data to run")
