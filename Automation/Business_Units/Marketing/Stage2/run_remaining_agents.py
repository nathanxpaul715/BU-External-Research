"""
Run only Agents 3, 4, and 5 using existing Agent 1 and Agent 2 outputs
"""
import sys
import os
import json
from datetime import datetime

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from agents import (
    DataIngestionAgent,
    UseCaseEnricherAgent,
    QualityAssuranceAgent,
    OutputFormatterAgent
)

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("\n" + "=" * 80)
    print("  RUNNING AGENTS 3, 4, 5 (Using existing Agent 1 & 2 outputs)")
    print("=" * 80 + "\n")

    # Paths
    base_dir = os.path.dirname(__file__)
    output_dir = os.path.join(base_dir, '..', '..', '..', 'data', 'Business Units', 'Marketing', 'Stage 2', 'agent_outputs')

    try:
        # Load existing Agent 2 output
        agent2_path = os.path.join(output_dir, 'agent2_web_research_output.json')
        print(f"[*] Loading Agent 2 output from: {agent2_path}")
        research_data = load_json(agent2_path)
        print(f"    Found {len(research_data['research_results'])} research results")

        # Run Agent 1 to get fresh ingestion data
        print("\n[*] Running Agent 1: Data Ingestion (to get fresh context)...")
        agent1 = DataIngestionAgent()
        ingestion_data = agent1.run()
        print(f"    Loaded {len(ingestion_data['use_cases'])} use cases")

        # AGENT 3: Use Case Enrichment
        print("\n[*] Running Agent 3: Use Case Enricher...")
        agent3 = UseCaseEnricherAgent()
        enrichment_data = agent3.run(ingestion_data, research_data)

        # Save Agent 3 output
        agent3_output = os.path.join(output_dir, 'agent3_use_case_enrichment_output.json')
        with open(agent3_output, 'w', encoding='utf-8') as f:
            json.dump(enrichment_data, f, indent=2, ensure_ascii=False)
        print(f"    [SAVED] {agent3_output}")
        print("[OK] Agent 3 Complete\n")

        # AGENT 4: Quality Assurance
        print("\n[*] Running Agent 4: Quality Assurance...")
        agent4 = QualityAssuranceAgent()
        qa_data = agent4.run(enrichment_data)

        # Save Agent 4 output
        agent4_output = os.path.join(output_dir, 'agent4_qa_output.json')
        with open(agent4_output, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, indent=2, ensure_ascii=False)
        print(f"    [SAVED] {agent4_output}")
        print("[OK] Agent 4 Complete\n")

        # AGENT 5: Output Formatting
        print("\n[*] Running Agent 5: Output Formatter...")
        agent5 = OutputFormatterAgent()
        output_data = agent5.run(enrichment_data)

        # Save Agent 5 output
        agent5_output = os.path.join(output_dir, 'agent5_output_formatter_output.json')
        with open(agent5_output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"    [SAVED] {agent5_output}")
        print("[OK] Agent 5 Complete\n")

        # Summary
        print("\n" + "=" * 80)
        print("  AGENTS 3, 4, 5 COMPLETE")
        print("=" * 80)
        print(f"\n[SUMMARY]:")
        print(f"   - Use Cases Enriched: {enrichment_data['total_enriched']}")
        print(f"   - QA Passed: {qa_data['passed_count']}/{qa_data['passed_count'] + qa_data['failed_count']}")
        print(f"   - Output File: {output_data['output_file']}")
        print(f"   - Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if not qa_data['all_passed']:
            print(f"\n[WARNING] {qa_data['failed_count']} use case(s) failed QA validation")

        print("\n" + "=" * 80 + "\n")

    except FileNotFoundError as e:
        print(f"\n[ERROR] Could not find required file: {e}")
        print("Make sure Agent 2 has run successfully first.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
