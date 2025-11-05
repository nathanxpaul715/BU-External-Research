"""
RAG-Enhanced Stage 2 Automation Orchestrator

This orchestrator coordinates the RAG-enhanced agents for use case enrichment.

Key Differences from Original:
1. Agent 1: Uses RAG for context retrieval instead of loading BU Intelligence document
2. Agent 2: Includes LLM summarization of web content + RAG context integration
3. Agent 3: Uses RAG-retrieved context for enrichment
"""

import sys
import os
import argparse
from datetime import datetime

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
marketing_dir = os.path.dirname(current_dir)  # Marketing
bu_dir = os.path.dirname(marketing_dir)  # Business_Units
automation_dir = os.path.dirname(bu_dir)  # Automation
project_root = os.path.dirname(automation_dir)  # Project root

sys.path.insert(0, current_dir)  # For config and agents
sys.path.insert(0, project_root)  # For rag_tool

# Import RAG-enhanced agents
from agents.agent1_data_ingestion_rag import RAGDataIngestionAgent
from agents.agent2_web_research_rag import RAGWebResearchAgent
from agents.agent3_use_case_enricher_rag import RAGUseCaseEnricherAgent
from agents.agent4_quality_assurance import QualityAssuranceAgent
from agents.agent5_output_formatter import OutputFormatterAgent


def print_header():
    """Print system header"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║               RAG-ENHANCED STAGE 2 AUTOMATION SYSTEM                         ║
║              AI Use Case Enrichment with RAG Integration                     ║
║                                                                              ║
║  5 Specialized Agents + FAISS RAG + Claude 4.5 Sonnet:                      ║
║    1. RAG-Powered Context Builder (replaces file loading)                   ║
║    2. RAG-Enhanced Web Research (with LLM summarization)                    ║
║    3. RAG-Enhanced Use Case Enricher                                        ║
║    4. Quality Assurance & Validation                                        ║
║    5. Output Formatter & Excel Generator                                    ║
║                                                                              ║
║  RAG Features:                                                               ║
║    ✓ TR internal documents context                                          ║
║    ✓ Gap analysis from knowledge base                                       ║
║    ✓ Market intelligence from RAG                                           ║
║    ✓ LLM-summarized web research                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def run_rag_automation(skip_web_research: bool = False, debug: bool = False):
    """
    Run the complete RAG-enhanced Stage 2 automation process.

    Args:
        skip_web_research: If True, skip web research agent (faster)
        debug: If True, print debug information
    """
    start_time = datetime.now()

    print_header()

    print("\n" + "="*80)
    print(f"STARTING RAG-ENHANCED AUTOMATION")
    print(f"Timestamp: {start_time.isoformat()}")
    print(f"Skip Web Research: {skip_web_research}")
    print(f"Debug Mode: {debug}")
    print("="*80 + "\n")

    # =========================================================================
    # STAGE 1: RAG-POWERED CONTEXT BUILDER
    # =========================================================================
    print("\n🔄 STAGE 1: Initializing RAG-Powered Context Builder...")
    agent1 = RAGDataIngestionAgent()
    ingestion_result = agent1.run()

    print(f"\n✓ Context retrieved from RAG:")
    print(f"  - TR Capabilities: {len(ingestion_result.get('tr_capabilities', ''))} chars")
    print(f"  - Gap Analysis: {len(ingestion_result.get('gap_analysis', ''))} chars")
    print(f"  - Market Intelligence: {len(ingestion_result.get('market_intelligence', ''))} chars")
    print(f"  - Use Cases Loaded: {len(ingestion_result['use_cases'])}")

    if debug:
        print("\n[DEBUG] Ingestion Result Keys:", list(ingestion_result.keys()))
        print("[DEBUG] Sample TR Capabilities:")
        print(ingestion_result.get('tr_capabilities', '')[:500])

    # =========================================================================
    # STAGE 2: RAG-ENHANCED WEB RESEARCH
    # =========================================================================
    if not skip_web_research:
        print("\n🔄 STAGE 2: Initializing RAG-Enhanced Web Research...")
        agent2 = RAGWebResearchAgent()
        research_result = agent2.run(ingestion_result)

        print(f"\n✓ Web research completed:")
        print(f"  - Use cases researched: {len(research_result['research_results'])}")
        print(f"  - RAG context integrated: Yes")
        print(f"  - LLM summarization: Yes")

        if debug:
            print("\n[DEBUG] Research Result Keys:", list(research_result.keys()))
            if research_result['research_results']:
                print("[DEBUG] Sample Research Keys:", list(research_result['research_results'][0].keys()))
    else:
        print("\n⏭️  STAGE 2: Skipping web research (--skip-web-research flag)")
        research_result = {
            "research_results": [{}] * len(ingestion_result["use_cases"]),
            "timestamp": datetime.now().isoformat(),
            "rag_enhanced": False
        }

    # =========================================================================
    # STAGE 3: RAG-ENHANCED USE CASE ENRICHMENT
    # =========================================================================
    print("\n🔄 STAGE 3: Initializing RAG-Enhanced Use Case Enricher...")
    agent3 = RAGUseCaseEnricherAgent()
    enrichment_result = agent3.run(ingestion_result, research_result)

    print(f"\n✓ Use case enrichment completed:")
    print(f"  - Use cases enriched: {enrichment_result['total_enriched']}")
    print(f"  - RAG context used: Yes")
    print(f"  - Context sources: TR docs, gaps, market intel, web research")

    if debug:
        print("\n[DEBUG] Enrichment Result Keys:", list(enrichment_result.keys()))
        if enrichment_result['enriched_use_cases']:
            print("[DEBUG] Sample Enriched Keys:", list(enrichment_result['enriched_use_cases'][0].keys()))

    # =========================================================================
    # STAGE 4: QUALITY ASSURANCE
    # =========================================================================
    print("\n🔄 STAGE 4: Initializing Quality Assurance...")
    agent4 = QualityAssuranceAgent()
    qa_result = agent4.run(enrichment_result)

    print(f"\n✓ Quality assurance completed:")
    print(f"  - Use cases validated: {qa_result['total_validated']}")
    print(f"  - Validation checks: {qa_result.get('validation_summary', {})}")

    if debug:
        print("\n[DEBUG] QA Result Keys:", list(qa_result.keys()))

    # =========================================================================
    # STAGE 5: OUTPUT FORMATTING
    # =========================================================================
    print("\n🔄 STAGE 5: Initializing Output Formatter...")
    agent5 = OutputFormatterAgent()
    output_result = agent5.run(qa_result, ingestion_result)

    print(f"\n✓ Output formatting completed:")
    print(f"  - Output file: {output_result.get('output_file', 'N/A')}")
    print(f"  - Format: Excel (.xlsx)")

    if debug:
        print("\n[DEBUG] Output Result Keys:", list(output_result.keys()))

    # =========================================================================
    # COMPLETION SUMMARY
    # =========================================================================
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "="*80)
    print("✅ RAG-ENHANCED AUTOMATION COMPLETE!")
    print("="*80)
    print(f"Start Time:    {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time:      {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration:      {duration}")
    print(f"Output File:   {output_result.get('output_file', 'N/A')}")
    print(f"\nRAG Features Used:")
    print(f"  ✓ TR Internal Documents Context")
    print(f"  ✓ Gap Analysis from Knowledge Base")
    print(f"  ✓ External Market Intelligence")
    print(f"  ✓ LLM-Summarized Web Research")
    print("="*80)

    return output_result


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='RAG-Enhanced Stage 2 Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator_rag.py                    # Full process with web research
  python orchestrator_rag.py --skip-web-research # Faster, skip web research
  python orchestrator_rag.py --debug            # Debug mode with verbose output
        """
    )

    parser.add_argument(
        '--skip-web-research',
        action='store_true',
        help='Skip web research agent (faster execution)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose output'
    )

    args = parser.parse_args()

    try:
        result = run_rag_automation(
            skip_web_research=args.skip_web_research,
            debug=args.debug
        )
        return result
    except Exception as e:
        print(f"\n❌ ERROR: Automation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
