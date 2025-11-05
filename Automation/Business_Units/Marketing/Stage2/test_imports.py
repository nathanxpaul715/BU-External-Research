"""
Test script to verify all imports work correctly for RAG agents
"""
import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
marketing_dir = os.path.dirname(current_dir)  # Marketing
bu_dir = os.path.dirname(marketing_dir)  # Business_Units
automation_dir = os.path.dirname(bu_dir)  # Automation
project_root = os.path.dirname(automation_dir)  # Project root

sys.path.insert(0, current_dir)  # For config and agents
sys.path.insert(0, project_root)  # For rag_tool

print("Testing imports...")
print(f"Project root: {project_root}")
print(f"Current dir: {current_dir}")
print()

try:
    print("1. Testing rag_tool import...")
    from rag_tool import get_rag_tool
    print("   ✓ rag_tool imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import rag_tool: {e}")

try:
    print("2. Testing config import...")
    from config import WORKSPACE_ID, MODEL
    print(f"   ✓ config imported successfully")
    print(f"   - Workspace ID: {WORKSPACE_ID}")
    print(f"   - Model: {MODEL}")
except ImportError as e:
    print(f"   ✗ Failed to import config: {e}")

try:
    print("3. Testing Agent 1 import...")
    from agents.agent1_data_ingestion_rag import RAGDataIngestionAgent
    print("   ✓ Agent 1 imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import Agent 1: {e}")

try:
    print("4. Testing Agent 2 import...")
    from agents.agent2_web_research_rag import RAGWebResearchAgent
    print("   ✓ Agent 2 imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import Agent 2: {e}")

try:
    print("5. Testing Agent 3 import...")
    from agents.agent3_use_case_enricher_rag import RAGUseCaseEnricherAgent
    print("   ✓ Agent 3 imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import Agent 3: {e}")

try:
    print("6. Testing Agent 4 import...")
    from agents.agent4_quality_assurance import QualityAssuranceAgent
    print("   ✓ Agent 4 imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import Agent 4: {e}")

try:
    print("7. Testing Agent 5 import...")
    from agents.agent5_output_formatter import OutputFormatterAgent
    print("   ✓ Agent 5 imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import Agent 5: {e}")

print()
print("=" * 60)
print("Import test complete!")
print("=" * 60)
