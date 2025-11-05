"""Agent 1: RAG-Powered Context Builder
Replaces traditional file ingestion with RAG-based context retrieval
"""
import pandas as pd
from typing import Dict, List, Any
import os
import sys

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
    USE_CASES_CSV_PATH,
    FUNCTION_UPDATES_CSV_PATH
)
from rag_tool import get_rag_tool


class RAGDataIngestionAgent:
    """Agent responsible for loading use cases and retrieving context from RAG"""

    def __init__(self):
        self.use_cases = None
        self.function_updates = None
        self.rag_tool = get_rag_tool()
        self.rag_context = {}
        print("[INFO] RAG Data Ingestion Agent initialized")

    def load_use_cases(self) -> pd.DataFrame:
        """Load AI Use Cases CSV"""
        print("Loading AI Use Cases CSV...")
        self.use_cases = pd.read_csv(USE_CASES_CSV_PATH)
        print(f"[OK] Loaded {len(self.use_cases)} use cases")
        print(f"  Columns: {list(self.use_cases.columns)}")
        return self.use_cases

    def load_function_updates(self) -> pd.DataFrame:
        """Load Function Updates CSV"""
        print("Loading Function Updates CSV...")
        self.function_updates = pd.read_csv(FUNCTION_UPDATES_CSV_PATH)
        print(f"[OK] Loaded {len(self.function_updates)} function updates")
        return self.function_updates

    def retrieve_tr_internal_context(self) -> Dict[str, str]:
        """Retrieve TR internal documents context from RAG"""
        print("Retrieving TR internal documents context from RAG...")

        contexts = {}

        # Query 1: TR External Research capabilities
        print("  - Querying TR research capabilities...")
        contexts["research_capabilities"] = self.rag_tool.search_knowledge_base(
            query="What are Thomson Reuters External Research capabilities, offerings, and products?",
            top_k=5,
            summarize=True
        )

        # Query 2: TR strategic initiatives
        print("  - Querying TR strategic initiatives...")
        contexts["strategic_initiatives"] = self.rag_tool.search_knowledge_base(
            query="What are Thomson Reuters External Research strategic initiatives, priorities, and roadmap?",
            top_k=5,
            summarize=True
        )

        # Query 3: TR competitive positioning
        print("  - Querying TR competitive positioning...")
        contexts["competitive_positioning"] = self.rag_tool.search_knowledge_base(
            query="What is Thomson Reuters competitive positioning, market position, and differentiation in external research?",
            top_k=5,
            summarize=True
        )

        print(f"[OK] Retrieved {len(contexts)} context sections from RAG")
        return contexts

    def retrieve_gap_analysis_context(self) -> str:
        """Retrieve gap analysis and areas for improvement from RAG"""
        print("Retrieving gap analysis from RAG...")

        gap_analysis = self.rag_tool.search_knowledge_base(
            query="What are the gap areas, weaknesses, and areas for improvement in Thomson Reuters External Research offerings? What capabilities are missing or need enhancement?",
            top_k=7,
            summarize=True
        )

        print(f"[OK] Retrieved gap analysis context ({len(gap_analysis)} characters)")
        return gap_analysis

    def retrieve_market_intelligence(self) -> str:
        """Retrieve external market intelligence from RAG"""
        print("Retrieving external market intelligence from RAG...")

        market_intel = self.rag_tool.search_knowledge_base(
            query="What is the external market landscape, industry trends, and competitive environment for external research and legal/financial research services?",
            top_k=5,
            summarize=True
        )

        print(f"[OK] Retrieved market intelligence ({len(market_intel)} characters)")
        return market_intel

    def get_use_case_specific_context(self, use_case_name: str, use_case_description: str) -> Dict[str, Any]:
        """Get specific context for a use case from RAG"""
        # Combine use case name and description for better query
        query = f"{use_case_name}: {use_case_description}"

        # Get raw context chunks for this specific use case
        relevant_chunks = self.rag_tool.get_relevant_context(
            query=query,
            top_k=3
        )

        return {
            "relevant_documents": relevant_chunks,
            "summary": self.rag_tool.search_knowledge_base(
                query=f"How does Thomson Reuters External Research relate to {use_case_name}?",
                top_k=3,
                summarize=True
            )
        }

    def extract_key_context(self) -> Dict[str, Any]:
        """Extract and structure all RAG-based context"""
        print("Extracting comprehensive RAG context...")

        # Retrieve all context types
        tr_internal = self.retrieve_tr_internal_context()
        gap_analysis = self.retrieve_gap_analysis_context()
        market_intel = self.retrieve_market_intelligence()

        context = {
            # TR Internal Context
            "tr_research_capabilities": tr_internal.get("research_capabilities", ""),
            "tr_strategic_initiatives": tr_internal.get("strategic_initiatives", ""),
            "tr_competitive_positioning": tr_internal.get("competitive_positioning", ""),

            # Gap Analysis
            "gap_analysis": gap_analysis,

            # Market Intelligence
            "external_market_intelligence": market_intel,

            # Metadata
            "num_use_cases": len(self.use_cases) if self.use_cases is not None else 0,
            "use_case_list": self.use_cases["Use Case Name"].tolist() if self.use_cases is not None else [],
            "context_source": "RAG (FAISS Vector Store + Claude 4.5 Sonnet)",
            "rag_enabled": True
        }

        # Create consolidated context for downstream agents
        context["consolidated_bu_intelligence"] = self._consolidate_context(tr_internal, gap_analysis, market_intel)

        self.rag_context = context
        print(f"[OK] RAG context extracted with {len(context)} elements")
        return context

    def _consolidate_context(self, tr_internal: Dict[str, str], gap_analysis: str, market_intel: str) -> str:
        """Consolidate all RAG context into a single comprehensive text"""
        consolidated = f"""
# THOMSON REUTERS EXTERNAL RESEARCH - COMPREHENSIVE CONTEXT

## 1. TR RESEARCH CAPABILITIES & OFFERINGS
{tr_internal.get("research_capabilities", "N/A")}

## 2. TR STRATEGIC INITIATIVES & PRIORITIES
{tr_internal.get("strategic_initiatives", "N/A")}

## 3. TR COMPETITIVE POSITIONING & DIFFERENTIATION
{tr_internal.get("competitive_positioning", "N/A")}

## 4. GAP ANALYSIS & AREAS FOR IMPROVEMENT
{gap_analysis}

## 5. EXTERNAL MARKET INTELLIGENCE & TRENDS
{market_intel}

---
Context Source: RAG-powered retrieval from TR External Research knowledge base
Generated using FAISS vector store with Claude 4.5 Sonnet summarization
"""
        return consolidated.strip()

    def prepare_use_cases_for_enrichment(self) -> List[Dict[str, Any]]:
        """Prepare use cases as structured dictionaries with RAG context for enrichment"""
        print("Preparing use cases with RAG context for enrichment...")

        use_cases_list = []
        for idx, row in self.use_cases.iterrows():
            use_case = {
                "index": idx,
                "function": row.get("Segment / Function", "Marketing"),
                "original_name": row.get("Use Case Name", ""),
                "original_description": row.get("Use Case Description", "") if pd.notna(row.get("Use Case Description")) else "",
                "original_outcomes": row.get("Outcomes/Deliverables", "") if pd.notna(row.get("Outcomes/Deliverables")) else "",
                "ai_tools": row.get("AI Tools", "") if pd.notna(row.get("AI Tools")) else "",
                "stage": row.get("Stage", "") if pd.notna(row.get("Stage")) else "",
                "strategy": row.get("Use Case Strategy", "") if pd.notna(row.get("Use Case Strategy")) else "",
                "full_row": row.to_dict()
            }

            # OPTIONAL: Get use case specific context (can be slow, comment out if not needed)
            # print(f"  - Getting RAG context for: {use_case['original_name']}")
            # use_case["rag_specific_context"] = self.get_use_case_specific_context(
            #     use_case["original_name"],
            #     use_case["original_description"]
            # )

            use_cases_list.append(use_case)

        print(f"[OK] Prepared {len(use_cases_list)} use cases with RAG context")
        return use_cases_list

    def run(self) -> Dict[str, Any]:
        """Execute RAG-powered data ingestion and context building"""
        print("=" * 80)
        print("AGENT 1: RAG-POWERED CONTEXT BUILDER")
        print("=" * 80)

        # Load structured data (CSV files)
        self.load_use_cases()
        self.load_function_updates()

        # Retrieve context from RAG instead of loading files
        self.extract_key_context()

        # Prepare use cases with RAG context
        use_cases_prepared = self.prepare_use_cases_for_enrichment()

        result = {
            # RAG-retrieved context (replaces BU Intelligence document)
            "bu_intelligence": self.rag_context.get("consolidated_bu_intelligence", ""),
            "tr_capabilities": self.rag_context.get("tr_research_capabilities", ""),
            "tr_initiatives": self.rag_context.get("tr_strategic_initiatives", ""),
            "tr_positioning": self.rag_context.get("tr_competitive_positioning", ""),
            "gap_analysis": self.rag_context.get("gap_analysis", ""),
            "market_intelligence": self.rag_context.get("external_market_intelligence", ""),

            # Structured data
            "use_cases": use_cases_prepared,
            "function_updates": self.function_updates,

            # Metadata
            "context": self.rag_context,
            "rag_enabled": True
        }

        print("\n[OK] RAG-POWERED DATA INGESTION COMPLETE")
        print(f"  - Retrieved context from {len(self.rag_context)} RAG queries")
        print(f"  - Total consolidated context: {len(result['bu_intelligence'])} characters")
        print("=" * 80)
        return result


if __name__ == "__main__":
    # Test the agent
    agent = RAGDataIngestionAgent()
    result = agent.run()
    print(f"\nResult keys: {list(result.keys())}")
    print(f"Number of use cases: {len(result['use_cases'])}")
    print(f"RAG enabled: {result.get('rag_enabled', False)}")
    print(f"\nSample TR Capabilities (first 500 chars):")
    print(result.get('tr_capabilities', '')[:500])
