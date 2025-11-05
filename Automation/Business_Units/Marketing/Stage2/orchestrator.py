"""Main Orchestrator for Stage 2 Automation
Coordinates all agents to execute the complete Stage 2 enrichment process
"""
import sys
import os
import json
import traceback
from datetime import datetime
from typing import Dict, Any

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from agents import (
    DataIngestionAgent,
    WebResearchAgent,
    UseCaseEnricherAgent,
    QualityAssuranceAgent,
    OutputFormatterAgent
)

# Import RAG tools (centralized)
from utils.rag_tools import initialize_rag, is_rag_available

# Import config for file paths
from config import BU_INTELLIGENCE_PATH, OPTIONAL_FILES


class Stage2Orchestrator:
    """Orchestrates all agents for Stage 2 automation"""

    def __init__(self, output_dir: str = None, use_rag: bool = True):
        self.start_time = None
        self.end_time = None
        self.results = {}
        self.use_rag = use_rag
        # Set output directory for intermediate JSON files
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'Business Units', 'Marketing', 'Stage 2', 'agent_outputs')
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def initialize_rag_service(self, force_rebuild: bool = False) -> bool:
        """Initialize RAG Service using centralized tools

        Args:
            force_rebuild: Force rebuild of vector store even if cache exists

        Returns:
            True if successful, False otherwise
        """
        if not self.use_rag:
            print("[RAG] RAG Service disabled (use_rag=False)")
            return False

        try:
            print("\n[*] Initializing RAG Service...")
            print("    Building FAISS vector store from BU Intelligence documents...")

            # Use centralized initialize_rag function
            success = initialize_rag(
                bu_intelligence_path=BU_INTELLIGENCE_PATH,
                optional_files=OPTIONAL_FILES,
                force_rebuild=force_rebuild
            )

            if success:
                print("[OK] RAG Service initialized and ready")
                return True
            else:
                print("[WARN] RAG Service initialization failed - falling back to non-RAG mode")
                return False

        except Exception as e:
            print(f"[ERROR] RAG Service initialization error: {e}")
            print(f"    Falling back to non-RAG mode")
            return False

    def print_banner(self, text: str):
        """Print a formatted banner"""
        print("\n")
        print("=" * 80)
        print(f"  {text}")
        print("=" * 80)
        print()

    def save_agent_output(self, agent_name: str, data: Dict[str, Any]):
        """Save agent output to JSON file for inspection"""
        output_file = os.path.join(self.output_dir, f"{agent_name}_output.json")

        # Create a serializable version of the data
        serializable_data = self._make_serializable(data)

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            print(f"    [SAVED] Agent output: {output_file}")
        except Exception as e:
            print(f"    [WARN] Could not save agent output: {e}")

    def _make_serializable(self, obj):
        """Convert object to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'to_dict'):  # pandas DataFrame/Series
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):  # custom objects
            return str(obj)
        else:
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)

    def run(self, skip_web_research: bool = False) -> Dict[str, Any]:
        """Execute the complete Stage 2 enrichment process

        Args:
            skip_web_research: If True, skip web research agent (faster, but less comprehensive)

        Returns:
            Dictionary with results from all agents
        """
        self.start_time = datetime.now()
        self.print_banner("STAGE 2 AUTOMATION - STARTING")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        try:
            # AGENT 1.5: Initialize RAG Service (build vector store once)
            rag_initialized = self.initialize_rag_service()
            if rag_initialized:
                print("[OK] RAG Service ready for use by Agent 2 and Agent 3\n")
            else:
                print("[WARN] Proceeding without RAG enhancement\n")

            # AGENT 1: Data Ingestion
            print("\n[*] Running Agent 1: Data Ingestion...")
            agent1 = DataIngestionAgent()
            ingestion_data = agent1.run()
            self.results['agent1_data_ingestion'] = ingestion_data
            self.save_agent_output("agent1_data_ingestion", {
                "context": ingestion_data["context"],
                "num_use_cases": len(ingestion_data["use_cases"]),
                "use_cases": ingestion_data["use_cases"],
                "bu_intelligence_length": len(ingestion_data["bu_intelligence"])
            })
            print("[OK] Agent 1 Complete\n")

            # AGENT 2: Web Research (Optional - can be skipped for faster processing)
            if not skip_web_research:
                print("\n[*] Running Agent 2: Web Research...")
                if is_rag_available():
                    print("    [RAG] RAG-enhanced context will be used automatically")
                agent2 = WebResearchAgent()
                research_data = agent2.run(ingestion_data)
                self.results['agent2_web_research'] = research_data
                self.save_agent_output("agent2_web_research", research_data)
                print("[OK] Agent 2 Complete\n")
            else:
                print("\n[SKIP] Skipping Agent 2: Web Research (as requested)")
                research_data = {"research_results": []}
                self.results['agent2_web_research'] = {"skipped": True}
                self.save_agent_output("agent2_web_research", {"skipped": True})

            # AGENT 3: Use Case Enrichment
            print("\n[*] Running Agent 3: Use Case Enricher...")
            if is_rag_available():
                print("    [RAG] RAG-enhanced context will be used automatically")
            agent3 = UseCaseEnricherAgent()
            enrichment_data = agent3.run(ingestion_data, research_data)
            self.results['agent3_enrichment'] = enrichment_data
            self.save_agent_output("agent3_enrichment", enrichment_data)
            print("[OK] Agent 3 Complete\n")

            # AGENT 4: Quality Assurance
            print("\n[*] Running Agent 4: Quality Assurance...")
            agent4 = QualityAssuranceAgent()
            qa_data = agent4.run(enrichment_data)
            self.results['agent4_qa'] = qa_data
            self.save_agent_output("agent4_quality_assurance", qa_data)
            print("[OK] Agent 4 Complete\n")

            # AGENT 5: Output Formatting
            print("\n[*] Running Agent 5: Output Formatter...")
            agent5 = OutputFormatterAgent()
            output_data = agent5.run(enrichment_data)
            self.results['agent5_output'] = output_data
            self.save_agent_output("agent5_output_formatter", output_data)
            print("[OK] Agent 5 Complete\n")

            # Final Summary
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()

            self.print_banner("STAGE 2 AUTOMATION - COMPLETE")
            print(f"[OK] All agents completed successfully!")
            print(f"\n[SUMMARY]:")
            print(f"   - Use Cases Processed: {ingestion_data['context']['num_use_cases']}")
            print(f"   - Use Cases Enriched: {enrichment_data['total_enriched']}")
            print(f"   - QA Passed: {qa_data['passed_count']}/{qa_data['passed_count'] + qa_data['failed_count']}")
            print(f"   - Output File: {output_data['output_file']}")
            print(f"   - Agent Outputs Dir: {self.output_dir}")
            print(f"   - Duration: {duration:.2f} seconds")
            print(f"   - End Time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

            if not qa_data['all_passed']:
                print(f"\n[WARNING] {qa_data['failed_count']} use case(s) failed QA validation")
                print("   Please review the validation results above for details.")

            print("\n" + "=" * 80 + "\n")

            return {
                "success": True,
                "results": self.results,
                "summary": {
                    "use_cases_processed": ingestion_data['context']['num_use_cases'],
                    "use_cases_enriched": enrichment_data['total_enriched'],
                    "qa_passed": qa_data['passed_count'],
                    "qa_failed": qa_data['failed_count'],
                    "output_file": output_data['output_file'],
                    "duration_seconds": duration,
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.end_time.isoformat()
                }
            }

        except Exception as e:
            self.end_time = datetime.now()
            print("\n" + "=" * 80)
            print("[ERROR] Stage 2 Automation Failed")
            print("=" * 80)
            print(f"\nError: {str(e)}")
            print("\nTraceback:")
            traceback.print_exc()
            print("\n" + "=" * 80 + "\n")

            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "results": self.results
            }


def main():
    """Main entry point for Stage 2 automation"""
    import argparse

    parser = argparse.ArgumentParser(description='Stage 2 Automation: AI Use Case Enrichment')
    parser.add_argument(
        '--skip-web-research',
        action='store_true',
        help='Skip web research for faster processing (less comprehensive)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose output'
    )

    args = parser.parse_args()

    # Run orchestrator
    orchestrator = Stage2Orchestrator()
    result = orchestrator.run(skip_web_research=args.skip_web_research)

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
