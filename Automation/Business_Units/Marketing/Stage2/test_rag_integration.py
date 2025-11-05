"""
Test script for RAG integration
Verifies that the RAG pipeline is properly integrated with the agent workflow
"""
import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))
sys.path.insert(0, os.path.dirname(__file__))

from agents.agent1_5_rag_service import RAGService
from agents.agent2_rag_helper import get_bu_context_for_research
from agents.agent3_rag_helper import get_enrichment_context
from config import BU_INTELLIGENCE_PATH, OPTIONAL_FILES


def test_rag_service_initialization():
    """Test 1: Verify RAG Service can be initialized and build vector store"""
    print("\n" + "="*80)
    print("TEST 1: RAG Service Initialization")
    print("="*80)

    try:
        # Initialize RAG Service
        rag_service = RAGService()

        # Build vector store
        success = rag_service.build_vector_store(
            bu_intelligence_path=BU_INTELLIGENCE_PATH,
            optional_files=OPTIONAL_FILES,
            force_rebuild=False
        )

        if success:
            print("[PASS] RAG Service initialized successfully")
            print(f"       Vector store location: {rag_service.persist_dir}")
            return rag_service
        else:
            print("[FAIL] RAG Service initialization failed")
            return None

    except Exception as e:
        print(f"[FAIL] Error initializing RAG Service: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_rag_retrieval(rag_service):
    """Test 2: Verify RAG retrieval works for sample use cases"""
    print("\n" + "="*80)
    print("TEST 2: RAG Retrieval")
    print("="*80)

    if not rag_service:
        print("[SKIP] Skipping test - RAG Service not initialized")
        return False

    # Sample use cases to test
    test_use_cases = [
        {
            "original_name": "Content Generation for Marketing Campaigns",
            "original_description": "Use AI to generate personalized marketing content"
        },
        {
            "original_name": "Customer Segmentation Analysis",
            "original_description": "AI-powered customer segmentation based on behavior"
        },
        {
            "original_name": "Social Media Post Optimization",
            "original_description": "Optimize social media posts for maximum engagement"
        }
    ]

    all_passed = True

    for idx, use_case in enumerate(test_use_cases, 1):
        print(f"\nTest Case {idx}: {use_case['original_name']}")
        print("-" * 80)

        try:
            # Test research context retrieval
            research_context = get_bu_context_for_research(use_case, rag_service)
            if research_context:
                print(f"[PASS] Retrieved research context ({len(research_context)} chars)")
                print(f"       Preview: {research_context[:200]}...")
            else:
                print("[WARN] Empty research context retrieved")
                all_passed = False

            # Test enrichment context retrieval
            enrichment_context = get_enrichment_context(use_case, rag_service, top_k=5)
            if enrichment_context:
                print(f"[PASS] Retrieved enrichment context ({len(enrichment_context)} chars)")
                print(f"       Preview: {enrichment_context[:200]}...")
            else:
                print("[WARN] Empty enrichment context retrieved")
                all_passed = False

        except Exception as e:
            print(f"[FAIL] Error retrieving context: {e}")
            all_passed = False

    if all_passed:
        print("\n[PASS] All retrieval tests passed")
    else:
        print("\n[WARN] Some retrieval tests had warnings")

    return all_passed


def test_vector_store_persistence(rag_service):
    """Test 3: Verify vector store can be saved and loaded"""
    print("\n" + "="*80)
    print("TEST 3: Vector Store Persistence")
    print("="*80)

    if not rag_service:
        print("[SKIP] Skipping test - RAG Service not initialized")
        return False

    try:
        # Create a new RAG Service instance
        new_rag_service = RAGService(persist_dir=rag_service.persist_dir)

        # Try to load existing vector store
        success = new_rag_service.build_vector_store(
            bu_intelligence_path=BU_INTELLIGENCE_PATH,
            optional_files=OPTIONAL_FILES,
            force_rebuild=False  # Should load from cache
        )

        if success:
            print("[PASS] Vector store successfully loaded from cache")
            print(f"       Location: {new_rag_service.persist_dir}")

            # Test that loaded store works
            test_query = "marketing automation"
            results = new_rag_service.retrieve_context(test_query, top_k=3)

            if results:
                print(f"[PASS] Loaded vector store can perform retrieval ({len(results)} results)")
                return True
            else:
                print("[FAIL] Loaded vector store returned no results")
                return False
        else:
            print("[FAIL] Could not load vector store from cache")
            return False

    except Exception as e:
        print(f"[FAIL] Error testing persistence: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wrapper_agents():
    """Test 4: Verify wrapper agents can be instantiated"""
    print("\n" + "="*80)
    print("TEST 4: Wrapper Agents")
    print("="*80)

    try:
        from agents.agent2_rag_wrapper import WebResearchAgentRAG
        from agents.agent3_rag_wrapper import UseCaseEnricherAgentRAG

        # Test Agent2 wrapper
        agent2 = WebResearchAgentRAG(rag_service=None)
        print("[PASS] Agent2 RAG wrapper instantiated successfully")

        # Test Agent3 wrapper
        agent3 = UseCaseEnricherAgentRAG(rag_service=None)
        print("[PASS] Agent3 RAG wrapper instantiated successfully")

        return True

    except Exception as e:
        print(f"[FAIL] Error instantiating wrapper agents: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all RAG integration tests"""
    print("\n" + "="*80)
    print("RAG INTEGRATION TEST SUITE")
    print("="*80)
    print(f"\nBU Intelligence Path: {BU_INTELLIGENCE_PATH}")
    print(f"Optional Files: {OPTIONAL_FILES}")

    results = {}

    # Test 1: Initialization
    rag_service = test_rag_service_initialization()
    results['initialization'] = rag_service is not None

    # Test 2: Retrieval
    results['retrieval'] = test_rag_retrieval(rag_service)

    # Test 3: Persistence
    results['persistence'] = test_vector_store_persistence(rag_service)

    # Test 4: Wrapper Agents
    results['wrappers'] = test_wrapper_agents()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name.upper()}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! RAG integration is working correctly.")
        return True
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
