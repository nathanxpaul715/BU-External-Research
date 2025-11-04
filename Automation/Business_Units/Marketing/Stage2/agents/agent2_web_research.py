"""Agent 2: Web Research & Competitive Intelligence
Performs external research to validate and enhance use case enrichment
"""
import pandas as pd
from typing import Dict, List, Any
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_URL, WORKSPACE_ID, MODEL, WEB_SEARCH_MAX_USES
from utils.api_client import get_api_client


class WebResearchAgent:
    """Agent responsible for web research and competitive intelligence"""

    def __init__(self):
        self.api_client = get_api_client(WORKSPACE_ID, ANTHROPIC_API_URL)

    def research_competitor_intelligence(
        self,
        use_case_name: str,
        use_case_description: str,
        bu_context: str
    ) -> Dict[str, Any]:
        """Research competitive landscape for a use case"""
        print(f"  Researching competitive intelligence for: {use_case_name}")

        prompt = f"""You are a competitive intelligence researcher. Research and provide:

USE CASE: {use_case_name}
DESCRIPTION: {use_case_description}

BUSINESS CONTEXT (from BU Intelligence - excerpt):
{bu_context[:2000]}...

Research and provide:
1. **Named Competitors**: At least 2-3 companies implementing similar AI use cases
2. **Real-World Examples**: Specific examples with company names, results, metrics
3. **Market Positioning**: How competitors are positioning similar capabilities

Format your response as structured JSON with keys: competitors, examples, positioning, sources"""

        try:
            message = self.api_client.create_message(
                model=MODEL,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": WEB_SEARCH_MAX_USES
                }]
            )

            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            return {
                "success": True,
                "data": response_text,
                "confidence": "High",  # Could be enhanced with actual confidence scoring
                "sources": self._extract_sources(message)
            }
        except Exception as e:
            print(f"    ✗ Error in competitive research: {e}")
            return {
                "success": False,
                "error": str(e),
                "confidence": "Low"
            }

    def research_vendor_solutions(
        self,
        use_case_name: str,
        ai_tools: str,
        bu_context: str
    ) -> Dict[str, Any]:
        """Research vendor solutions and technologies"""
        print(f"  Researching vendor solutions for: {use_case_name}")

        prompt = f"""You are a technology vendor analyst. Research and provide:

USE CASE: {use_case_name}
CURRENT AI TOOLS: {ai_tools}

BUSINESS CONTEXT (excerpt):
{bu_context[:2000]}...

Research and provide:
1. **Named Vendors/Solutions**: Specific products/platforms for this use case
2. **Product Comparisons**: Feature comparisons, pricing insights (if available)
3. **Implementation Cases**: Real case studies with ROI data, timelines, results
4. **Market Leaders**: Top 3-5 vendors in this space

Format as structured JSON with keys: vendors, comparisons, case_studies, market_leaders, sources"""

        try:
            message = self.api_client.create_message(
                model=MODEL,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": WEB_SEARCH_MAX_USES
                }]
            )

            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            return {
                "success": True,
                "data": response_text,
                "confidence": "High",
                "sources": self._extract_sources(message)
            }
        except Exception as e:
            print(f"    ✗ Error in vendor research: {e}")
            return {
                "success": False,
                "error": str(e),
                "confidence": "Low"
            }

    def research_industry_benchmarks(
        self,
        use_case_name: str,
        use_case_description: str
    ) -> Dict[str, Any]:
        """Research industry benchmarks and metrics"""
        print(f"  Researching industry benchmarks for: {use_case_name}")

        prompt = f"""You are an industry analyst. Research and provide quantified benchmarks:

USE CASE: {use_case_name}
DESCRIPTION: {use_case_description}

Research and provide:
1. **Quantified Metrics**: Specific benchmarks (time savings %, cost reduction $, ROI %, accuracy improvements)
2. **Industry Reports**: Relevant Gartner, Forrester, IDC, McKinsey, BCG reports
3. **Best Practices**: Industry best practices and success frameworks
4. **Market Trends**: Latest trends and future outlook (2024-2025)

IMPORTANT: Include specific numbers, percentages, dollar amounts with sources.

Format as structured JSON with keys: metrics, reports, best_practices, trends, sources"""

        try:
            message = self.api_client.create_message(
                model=MODEL,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": WEB_SEARCH_MAX_USES
                }]
            )

            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            return {
                "success": True,
                "data": response_text,
                "confidence": "High",
                "sources": self._extract_sources(message)
            }
        except Exception as e:
            print(f"    ✗ Error in benchmark research: {e}")
            return {
                "success": False,
                "error": str(e),
                "confidence": "Low"
            }

    def _extract_sources(self, message) -> List[str]:
        """Extract source URLs from web search results"""
        sources = []
        # The web_search tool results would be in the message content
        # This is a placeholder - actual implementation would parse tool use results
        return sources

    def research_use_case(
        self,
        use_case: Dict[str, Any],
        bu_intelligence: str
    ) -> Dict[str, Any]:
        """Perform comprehensive research for a single use case"""
        print(f"\nResearching: {use_case['original_name']}")

        research_results = {
            "use_case_name": use_case["original_name"],
            "competitor_intelligence": self.research_competitor_intelligence(
                use_case["original_name"],
                use_case["original_description"],
                bu_intelligence
            ),
            "vendor_solutions": self.research_vendor_solutions(
                use_case["original_name"],
                use_case["ai_tools"],
                bu_intelligence
            ),
            "industry_benchmarks": self.research_industry_benchmarks(
                use_case["original_name"],
                use_case["original_description"]
            )
        }

        return research_results

    def run(self, ingestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web research for all use cases"""
        print("=" * 80)
        print("AGENT 2: WEB RESEARCH & COMPETITIVE INTELLIGENCE")
        print("=" * 80)

        use_cases = ingestion_data["use_cases"]
        bu_intelligence = ingestion_data["bu_intelligence"]

        all_research = []
        for use_case in use_cases:
            research = self.research_use_case(use_case, bu_intelligence)
            all_research.append(research)

        print("\n✓ WEB RESEARCH COMPLETE")
        print("=" * 80)

        return {
            "research_results": all_research,
            "timestamp": pd.Timestamp.now().isoformat()
        }


if __name__ == "__main__":
    # Test the agent (requires ingestion data)
    print("Web Research Agent - requires ingestion data to run")
