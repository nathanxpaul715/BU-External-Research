"""Agent 2: RAG-Enhanced Web Research & Competitive Intelligence
Performs external research with LLM summarization and integrates with RAG context
"""
import pandas as pd
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

from config import ANTHROPIC_API_URL, WORKSPACE_ID, MODEL, WEB_SEARCH_MAX_USES
from utils.api_client import get_api_client
from rag_tool import get_rag_tool


class RAGWebResearchAgent:
    """Agent responsible for web research enhanced with RAG context and LLM summarization"""

    def __init__(self):
        self.api_client = get_api_client(WORKSPACE_ID, ANTHROPIC_API_URL)
        self.rag_tool = get_rag_tool()
        print("[INFO] RAG Web Research Agent initialized")

    def get_tr_context_for_use_case(self, use_case_name: str, use_case_description: str) -> str:
        """Get relevant TR internal context from RAG for a specific use case"""
        print(f"    → Getting TR internal context from RAG...")

        query = f"""
        How does Thomson Reuters External Research relate to this use case:
        {use_case_name} - {use_case_description}

        Include: TR capabilities, existing offerings, strategic alignment, and any related initiatives.
        """

        tr_context = self.rag_tool.search_knowledge_base(
            query=query,
            top_k=3,
            summarize=True
        )

        return tr_context

    def get_gap_analysis_for_use_case(self, use_case_name: str) -> str:
        """Get gap analysis from RAG relevant to this use case"""
        print(f"    → Getting gap analysis from RAG...")

        gap_context = self.rag_tool.search_knowledge_base(
            query=f"What gaps or limitations exist in TR External Research related to {use_case_name}? What improvements are needed?",
            top_k=3,
            summarize=True
        )

        return gap_context

    def summarize_web_research_with_llm(self, raw_research_data: str, use_case_name: str, research_type: str) -> str:
        """
        Use LLM to summarize web research results instead of returning all content.
        This addresses the requirement to summarize web page content.
        """
        print(f"    → Summarizing {research_type} research with LLM...")

        summarization_prompt = f"""You are a research analyst. Summarize the following web research data concisely.

RESEARCH TYPE: {research_type}
USE CASE: {use_case_name}

RAW RESEARCH DATA:
{raw_research_data[:3000]}

Provide a concise summary with:
1. Key findings (3-5 bullet points)
2. Named companies/vendors (if applicable)
3. Specific metrics or data points
4. Actionable insights

Keep the summary under 500 words and focus on the most relevant information."""

        try:
            message = self.api_client.create_message(
                model=MODEL,
                max_tokens=1500,
                messages=[{"role": "user", "content": summarization_prompt}]
            )

            summary = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    summary += block.text

            return summary

        except Exception as e:
            print(f"    ✗ Error summarizing: {e}")
            return raw_research_data[:1000]  # Fallback to truncated raw data

    def research_competitor_intelligence(
        self,
        use_case_name: str,
        use_case_description: str,
        tr_context: str,
        gap_context: str
    ) -> Dict[str, Any]:
        """Research competitive landscape with RAG context integration"""
        print(f"  Researching competitive intelligence for: {use_case_name}")

        prompt = f"""You are a competitive intelligence researcher. Research and provide structured insights.

USE CASE: {use_case_name}
DESCRIPTION: {use_case_description}

INTERNAL TR CONTEXT (from RAG):
{tr_context[:1500]}

GAP ANALYSIS (from RAG):
{gap_context[:1000]}

Research and provide:
1. **Named Competitors**: At least 2-3 companies implementing similar AI use cases (e.g., LexisNexis, Bloomberg Law, Westlaw, etc.)
2. **Real-World Examples**: Specific examples with company names, results, metrics
3. **Market Positioning**: How competitors are positioning similar capabilities
4. **Differentiation Opportunities**: Based on TR's gaps, what differentiation opportunities exist?

Format your response as structured sections with clear headings."""

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

            # Summarize the web research results with LLM
            summarized_research = self.summarize_web_research_with_llm(
                response_text,
                use_case_name,
                "Competitive Intelligence"
            )

            return {
                "success": True,
                "data": summarized_research,
                "raw_data": response_text,  # Keep raw for reference
                "confidence": "High",
                "sources": self._extract_sources(message),
                "tr_context_used": tr_context[:500],
                "gap_context_used": gap_context[:500]
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
        tr_context: str,
        market_intel: str
    ) -> Dict[str, Any]:
        """Research vendor solutions with RAG market intelligence"""
        print(f"  Researching vendor solutions for: {use_case_name}")

        prompt = f"""You are a technology vendor analyst. Research and provide structured insights.

USE CASE: {use_case_name}
CURRENT AI TOOLS: {ai_tools}

INTERNAL TR CONTEXT (from RAG):
{tr_context[:1500]}

EXTERNAL MARKET INTELLIGENCE (from RAG):
{market_intel[:1000]}

Research and provide:
1. **Named Vendors/Solutions**: Specific products/platforms (e.g., OpenAI GPT-4, Anthropic Claude, Cohere, etc.)
2. **Product Comparisons**: Feature comparisons, pricing insights
3. **Implementation Cases**: Real case studies with ROI data, timelines, results
4. **Market Leaders**: Top 3-5 vendors in this space
5. **TR Alignment**: How these solutions align with TR's current capabilities and gaps

Format as structured sections with clear headings."""

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

            # Summarize with LLM
            summarized_research = self.summarize_web_research_with_llm(
                response_text,
                use_case_name,
                "Vendor Solutions"
            )

            return {
                "success": True,
                "data": summarized_research,
                "raw_data": response_text,
                "confidence": "High",
                "sources": self._extract_sources(message),
                "tr_context_used": tr_context[:500],
                "market_intel_used": market_intel[:500]
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
        use_case_description: str,
        market_intel: str
    ) -> Dict[str, Any]:
        """Research industry benchmarks with RAG market intelligence"""
        print(f"  Researching industry benchmarks for: {use_case_name}")

        prompt = f"""You are an industry analyst. Research and provide quantified benchmarks.

USE CASE: {use_case_name}
DESCRIPTION: {use_case_description}

EXTERNAL MARKET INTELLIGENCE (from RAG):
{market_intel[:1500]}

Research and provide:
1. **Quantified Metrics**: Specific benchmarks (time savings %, cost reduction $, ROI %, accuracy improvements)
2. **Industry Reports**: Relevant Gartner, Forrester, IDC, McKinsey, BCG reports
3. **Best Practices**: Industry best practices and success frameworks
4. **Market Trends**: Latest trends and future outlook (2024-2025)
5. **Competitive Benchmarks**: How do competitors perform on these metrics?

IMPORTANT: Include specific numbers, percentages, dollar amounts with sources.

Format as structured sections with clear headings."""

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

            # Summarize with LLM
            summarized_research = self.summarize_web_research_with_llm(
                response_text,
                use_case_name,
                "Industry Benchmarks"
            )

            return {
                "success": True,
                "data": summarized_research,
                "raw_data": response_text,
                "confidence": "High",
                "sources": self._extract_sources(message),
                "market_intel_used": market_intel[:500]
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
        rag_ingestion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive research for a single use case with RAG context"""
        print(f"\nResearching: {use_case['original_name']}")

        # Get TR internal context from RAG
        tr_context = self.get_tr_context_for_use_case(
            use_case["original_name"],
            use_case["original_description"]
        )

        # Get gap analysis from RAG
        gap_context = self.get_gap_analysis_for_use_case(use_case["original_name"])

        # Get market intelligence from RAG ingestion
        market_intel = rag_ingestion_data.get("market_intelligence", "")

        research_results = {
            "use_case_name": use_case["original_name"],

            # RAG-enhanced context
            "tr_internal_context": tr_context,
            "gap_analysis_context": gap_context,
            "market_intelligence_context": market_intel,

            # Web research with LLM summarization
            "competitor_intelligence": self.research_competitor_intelligence(
                use_case["original_name"],
                use_case["original_description"],
                tr_context,
                gap_context
            ),
            "vendor_solutions": self.research_vendor_solutions(
                use_case["original_name"],
                use_case["ai_tools"],
                tr_context,
                market_intel
            ),
            "industry_benchmarks": self.research_industry_benchmarks(
                use_case["original_name"],
                use_case["original_description"],
                market_intel
            ),

            # Metadata
            "rag_enhanced": True
        }

        return research_results

    def run(self, ingestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute RAG-enhanced web research for all use cases"""
        print("=" * 80)
        print("AGENT 2: RAG-ENHANCED WEB RESEARCH & COMPETITIVE INTELLIGENCE")
        print("=" * 80)

        use_cases = ingestion_data["use_cases"]

        all_research = []
        for i, use_case in enumerate(use_cases):
            research = self.research_use_case(use_case, ingestion_data)
            all_research.append(research)

            # Add delay between use cases to avoid rate limiting
            if i < len(use_cases) - 1:
                print(f"  [THROTTLE] Waiting 10s before next research to avoid rate limits...")
                time.sleep(10)

        print("\n[OK] RAG-ENHANCED WEB RESEARCH COMPLETE")
        print(f"  - Integrated RAG context for all {len(all_research)} use cases")
        print(f"  - Summarized web research with LLM")
        print("=" * 80)

        return {
            "research_results": all_research,
            "timestamp": pd.Timestamp.now().isoformat(),
            "rag_enhanced": True
        }


if __name__ == "__main__":
    print("RAG-Enhanced Web Research Agent - requires RAG ingestion data to run")
