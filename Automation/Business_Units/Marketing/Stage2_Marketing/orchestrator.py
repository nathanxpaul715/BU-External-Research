"""Main Orchestrator for Stage 2 Automation
Coordinates all agents to execute the complete Stage 2 enrichment process
"""
import sys
import os
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


class Stage2Orchestrator:
    """Orchestrates all agents for Stage 2 automation"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {}

    def print_banner(self, text: str):
        """Print a formatted banner"""
        print("\n")
        print("=" * 80)
        print(f"  {text}")
        print("=" * 80)
        print()

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
            # AGENT 1: Data Ingestion
            print("\n🔄 Running Agent 1: Data Ingestion...")
            agent1 = DataIngestionAgent()
            ingestion_data = agent1.run()
            self.results['agent1_data_ingestion'] = ingestion_data
            print("✅ Agent 1 Complete\n")

            # AGENT 2: Web Research (Optional - can be skipped for faster processing)
            if not skip_web_research:
                print("\n🔄 Running Agent 2: Web Research...")
                agent2 = WebResearchAgent()
                research_data = agent2.run(ingestion_data)
                self.results['agent2_web_research'] = research_data
                print("✅ Agent 2 Complete\n")
            else:
                print("\n⏭️  Skipping Agent 2: Web Research (as requested)")
                research_data = {"research_results": []}
                self.results['agent2_web_research'] = {"skipped": True}

            # AGENT 3: Use Case Enrichment
            print("\n🔄 Running Agent 3: Use Case Enricher...")
            agent3 = UseCaseEnricherAgent()
            enrichment_data = agent3.run(ingestion_data, research_data)
            self.results['agent3_enrichment'] = enrichment_data
            print("✅ Agent 3 Complete\n")

            # AGENT 4: Quality Assurance
            print("\n🔄 Running Agent 4: Quality Assurance...")
            agent4 = QualityAssuranceAgent()
            qa_data = agent4.run(enrichment_data)
            self.results['agent4_qa'] = qa_data
            print("✅ Agent 4 Complete\n")

            # AGENT 5: Output Formatting
            print("\n🔄 Running Agent 5: Output Formatter...")
            agent5 = OutputFormatterAgent()
            output_data = agent5.run(enrichment_data)
            self.results['agent5_output'] = output_data
            print("✅ Agent 5 Complete\n")

            # Final Summary
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()

            self.print_banner("STAGE 2 AUTOMATION - COMPLETE")
            print(f"✅ All agents completed successfully!")
            print(f"\n📊 SUMMARY:")
            print(f"   - Use Cases Processed: {ingestion_data['context']['num_use_cases']}")
            print(f"   - Use Cases Enriched: {enrichment_data['total_enriched']}")
            print(f"   - QA Passed: {qa_data['passed_count']}/{qa_data['passed_count'] + qa_data['failed_count']}")
            print(f"   - Output File: {output_data['output_file']}")
            print(f"   - Duration: {duration:.2f} seconds")
            print(f"   - End Time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

            if not qa_data['all_passed']:
                print(f"\n⚠️  WARNING: {qa_data['failed_count']} use case(s) failed QA validation")
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
            print("❌ ERROR: Stage 2 Automation Failed")
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
