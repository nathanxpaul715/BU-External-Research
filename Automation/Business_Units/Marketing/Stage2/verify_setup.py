"""
Quick verification script to check RAG setup
Run this to verify all dependencies and imports work correctly
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

def check_imports():
    """Check if all required imports work"""
    print("="*80)
    print("CHECKING RAG SETUP")
    print("="*80)

    checks_passed = 0
    checks_total = 0

    # Check 1: FAISS
    checks_total += 1
    try:
        import faiss
        print("✓ faiss-cpu installed")
        checks_passed += 1
    except ImportError as e:
        print(f"✗ faiss-cpu NOT installed: {e}")
        print("  Install with: pip install faiss-cpu")

    # Check 2: Sentence Transformers
    checks_total += 1
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers installed")
        checks_passed += 1
    except ImportError as e:
        print(f"✗ sentence-transformers NOT installed: {e}")
        print("  Install with: pip install sentence-transformers")

    # Check 3: Langchain
    checks_total += 1
    try:
        import langchain
        print("✓ langchain installed")
        checks_passed += 1
    except ImportError as e:
        print(f"✗ langchain NOT installed: {e}")
        print("  Install with: pip install langchain")

    # Check 4: Langchain Community
    checks_total += 1
    try:
        from langchain_community.document_loaders import Docx2txtLoader
        print("✓ langchain-community installed")
        checks_passed += 1
    except ImportError as e:
        print(f"✗ langchain-community NOT installed: {e}")
        print("  Install with: pip install langchain-community")

    # Check 5: RAG Tools
    checks_total += 1
    try:
        from utils.rag_tools import initialize_rag, get_rag_context_for_use_case, is_rag_available
        print("✓ RAG tools module found")
        checks_passed += 1
    except ImportError as e:
        print(f"✗ RAG tools module NOT found: {e}")
        print("  Check that utils/rag_tools.py exists")

    # Check 6: Agent2
    checks_total += 1
    try:
        from agents.agent2_web_research import WebResearchAgent
        print("✓ Agent2 imports correctly")
        checks_passed += 1
    except ImportError as e:
        print(f"✗ Agent2 import error: {e}")

    # Check 7: Agent3
    checks_total += 1
    try:
        from agents.agent3_use_case_enricher import UseCaseEnricherAgent
        print("✓ Agent3 imports correctly")
        checks_passed += 1
    except ImportError as e:
        print(f"✗ Agent3 import error: {e}")

    # Check 8: Config
    checks_total += 1
    try:
        from config import BU_INTELLIGENCE_PATH, OPTIONAL_FILES
        print("✓ Config imports correctly")
        checks_passed += 1

        # Check file existence
        import os
        if os.path.exists(BU_INTELLIGENCE_PATH):
            print(f"  ✓ BU Intelligence file found: {BU_INTELLIGENCE_PATH}")
        else:
            print(f"  ⚠ BU Intelligence file NOT found: {BU_INTELLIGENCE_PATH}")
            print(f"    Vector store will fail to build until this file is available")
    except ImportError as e:
        print(f"✗ Config import error: {e}")

    # Summary
    print("\n" + "="*80)
    print(f"RESULTS: {checks_passed}/{checks_total} checks passed")
    print("="*80)

    if checks_passed == checks_total:
        print("✓ All checks passed! RAG is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python orchestrator.py")
        print("  2. RAG will build vector store on first run (30-60s)")
        print("  3. Subsequent runs will load from cache (<5s)")
        return True
    else:
        print(f"✗ {checks_total - checks_passed} check(s) failed.")
        print("\nInstall missing dependencies:")
        print("  pip install faiss-cpu sentence-transformers langchain langchain-community")
        return False


if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)
