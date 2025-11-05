"""
Quick Setup Test Script
Tests that all components can be imported and basic configuration is correct
Run this before running the full pipeline to catch setup issues early
"""
import os
import sys

# Add parent directory to path (same as main.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print("=" * 70)
print("RAG PIPELINE SETUP TEST")
print("=" * 70)
print()

# Test 1: Import configuration
print("Test 1: Importing configuration...")
try:
    from rag_pipeline.config.settings import RAGPipelineConfig, get_config
    config = get_config()
    print("  ✓ Configuration imported successfully")
    print(f"  ✓ Using TR OpenAI: {config.use_tr_openai}")
except Exception as e:
    print(f"  ✗ Failed to import configuration: {e}")
    sys.exit(1)

# Test 2: Check environment variables
print("\nTest 2: Checking environment variables...")
required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'OPENSEARCH_HOST']

if config.use_tr_openai:
    required_vars.extend(['TR_WORKSPACE_ID', 'TR_ASSET_ID'])
    print("  Using Thomson Reuters OpenAI")
else:
    required_vars.append('OPENAI_API_KEY')
    print("  Using Direct OpenAI")

missing = []
for var in required_vars:
    if not os.getenv(var):
        missing.append(var)
        print(f"  ✗ Missing: {var}")
    else:
        # Show first few characters only
        value = os.getenv(var)
        masked = value[:4] + "..." if len(value) > 4 else "***"
        print(f"  ✓ Found: {var}={masked}")

if missing:
    print(f"\n✗ Missing {len(missing)} required environment variable(s)")
    print("\nPlease set these in your .env file or environment:")
    for var in missing:
        print(f"  - {var}")
    sys.exit(1)

# Test 3: Import modules
print("\nTest 3: Importing core modules...")
modules_to_test = [
    ("LLM", "rag_pipeline.llm.claude_wrapper", "ClaudeLLM"),
    ("Embeddings (OpenAI)", "rag_pipeline.embeddings.openai_embeddings", "CachedOpenAIEmbeddings"),
    ("Embeddings (TR OpenAI)", "rag_pipeline.embeddings.tr_openai_embeddings", "CachedTROpenAIEmbeddings"),
    ("Document Loader", "rag_pipeline.loaders.document_loader", "MultiFormatDocumentLoader"),
    ("Vector Store", "rag_pipeline.vectorstore.opensearch_store", "OpenSearchVectorStore"),
    ("RAG Agents", "rag_pipeline.agents.rag_agents", "MultiStageRetriever"),
    ("Job Memory", "rag_pipeline.memory.job_memory", "JobMemoryManager"),
    ("Workflows", "rag_pipeline.workflows.agentic_rag", "SimpleRAGWorkflow"),
]

failed_imports = []
for name, module, cls in modules_to_test:
    try:
        mod = __import__(module, fromlist=[cls])
        getattr(mod, cls)
        print(f"  ✓ {name}")
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        failed_imports.append(name)

if failed_imports:
    print(f"\n✗ Failed to import {len(failed_imports)} module(s)")
    sys.exit(1)

# Test 4: Check input data path
print("\nTest 4: Checking input data path...")
if os.path.exists(config.input_data_path):
    files = [f for f in os.listdir(config.input_data_path)
             if f.endswith(('.docx', '.csv', '.xlsx'))]
    print(f"  ✓ Input path exists: {config.input_data_path}")
    print(f"  ✓ Found {len(files)} input file(s)")
    if files:
        for f in files[:3]:  # Show first 3
            print(f"    - {f}")
        if len(files) > 3:
            print(f"    ... and {len(files) - 3} more")
else:
    print(f"  ✗ Input path not found: {config.input_data_path}")
    print("  Note: This is optional for testing, but required for running the pipeline")

# Test 5: Check dependencies
print("\nTest 5: Checking key dependencies...")
dependencies = [
    ("anthropic", "Claude API"),
    ("openai", "OpenAI API"),
    ("opensearchpy", "OpenSearch"),
    ("boto3", "AWS SDK"),
    ("langgraph", "LangGraph"),
    ("pandas", "Data processing"),
    ("docx", "Document loading"),
    ("sentence_transformers", "Reranking"),
]

missing_deps = []
for module, description in dependencies:
    try:
        __import__(module)
        print(f"  ✓ {description} ({module})")
    except ImportError:
        print(f"  ✗ {description} ({module}) - not installed")
        missing_deps.append(module)

if missing_deps:
    print(f"\n✗ Missing {len(missing_deps)} required package(s)")
    print("\nInstall missing packages with:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("SETUP TEST SUMMARY")
print("=" * 70)
print("✓ All tests passed!")
print("\nYour RAG pipeline is ready to run.")
print("\nNext steps:")
print("  1. Ensure OpenSearch Serverless collection is created")
print("  2. Run the pipeline: python main.py")
print("\nFor detailed setup instructions, see QUICKSTART.md")
print("=" * 70)
