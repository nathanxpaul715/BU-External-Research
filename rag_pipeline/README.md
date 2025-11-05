# RAG Pipeline with OpenSearch Serverless and Claude Sonnet 4

Complete RAG (Retrieval-Augmented Generation) pipeline implementation based on the RAG Architecture Document specifications.

## Architecture Overview

This pipeline implements a sophisticated multi-stage RAG system with:

- **Vector Store**: OpenSearch Serverless with k-NN search (HNSW algorithm)
- **Embeddings**: OpenAI text-embedding-3-large (3072 dimensions)
  - **Thomson Reuters OpenAI** (default) - Uses TR AI Platform authentication
  - **Direct OpenAI** (optional) - Uses personal API key
- **LLM**: Claude Sonnet 4 (via Thomson Reuters AI Platform)
- **Chunking**: Metadata-aware chunking (800 tokens, 150 overlap)
- **Multi-Stage Retrieval**:
  - Stage 1: Broad Recall (top-50 candidates)
  - Stage 2: Relevance Filtering (75% similarity threshold)
  - Stage 3: Cross-Encoder Reranking (top-15)
  - Stage 4: Context Assembly (deduplication, merging, optimization)
- **Job Memory**: Lightweight context preservation across stages
- **LangGraph**: Agentic workflow orchestration

> **For Thomson Reuters users:** This pipeline uses TR OpenAI by default - no personal OpenAI API key needed! See [TR_OPENAI_SETUP.md](TR_OPENAI_SETUP.md) for details.

## Project Structure

```
rag_pipeline/
├── config/              # Configuration settings
│   └── settings.py
├── llm/                 # LLM wrappers
│   └── claude_wrapper.py
├── embeddings/          # Embedding models
│   └── openai_embeddings.py
├── loaders/             # Document loaders
│   └── document_loader.py
├── vectorstore/         # Vector store implementation
│   └── opensearch_store.py
├── agents/              # RAG agents (R-03, R-04, R-05, R-06)
│   └── rag_agents.py
├── memory/              # Job memory system
│   └── job_memory.py
├── workflows/           # LangGraph workflows
│   └── agentic_rag.py
├── main.py             # Main execution script
└── requirements.txt    # Dependencies
```

## Setup Instructions

### 1. Install Dependencies

Fix the PyTorch DLL issue (Windows only):
```bash
# Install Visual C++ Redistributable
# Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

Install Python packages:
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file or set the following environment variables:

#### Option A: Thomson Reuters OpenAI (Default - Recommended for TR users)

```bash
# Thomson Reuters OpenAI (no personal API key needed!)
TR_WORKSPACE_ID=your_workspace_id
TR_ASSET_ID=your_asset_id

# AWS Credentials (for OpenSearch Serverless)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# OpenSearch Serverless Endpoint
OPENSEARCH_HOST=your-opensearch-endpoint.us-east-1.aoss.amazonaws.com
```

See [TR_OPENAI_SETUP.md](TR_OPENAI_SETUP.md) for detailed TR OpenAI setup instructions.

#### Option B: Direct OpenAI (requires personal API key)

Set `use_tr_openai = False` in [config/settings.py](config/settings.py), then:

```bash
# Direct OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# AWS Credentials (for OpenSearch Serverless)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# OpenSearch Serverless Endpoint
OPENSEARCH_HOST=your-opensearch-endpoint.us-east-1.aoss.amazonaws.com
```

### 3. Configure Settings (Optional)

Edit [config/settings.py](config/settings.py) to customize:
- Chunking parameters (token size, overlap)
- Retrieval settings (similarity threshold, top-k)
- OpenSearch configuration (k-NN parameters)
- Budget and quality constraints

## Usage

### Basic Usage

```python
from rag_pipeline.main import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

# Setup components
pipeline.setup()

# Load and index documents
pipeline.load_and_index_documents()

# Initialize retrieval
pipeline.initialize_retrieval()

# Query
result = pipeline.query("What are the main AI use cases?")
print(result['answer'])
```

### Run Main Script

```bash
cd rag_pipeline
python main.py
```

This will:
1. Initialize all components (Claude, OpenAI, OpenSearch)
2. Load documents from the configured input path
3. Generate embeddings and index in OpenSearch
4. Run example queries
5. Enter interactive mode for custom queries

### Interactive Mode

Once the pipeline is running, you can ask questions interactively:

```
Your question: What AI capabilities are mentioned in the marketing documents?

ANSWER:
[Answer based on retrieved context]

METADATA:
  Sources: 3 files
  Chunks: 12
  Retrieval time: 650ms
  Total time: 4.2s
  Cost: $0.0234
```

## Architecture Details

### Document Loading (Agent F-03)

- **Supported formats**: DOCX, CSV, XLSX
- **Chunking**: 800 tokens per chunk, 150 token overlap
- **Metadata preservation**: Section numbers, headings, page numbers
- **Token counting**: Uses tiktoken for accurate counts

### Vector Store (Section 7.2)

OpenSearch index configuration:
```json
{
  "embedding": {
    "type": "knn_vector",
    "dimension": 3072,
    "method": {
      "name": "hnsw",
      "space_type": "cosinesimilarity",
      "engine": "nmslib",
      "parameters": {
        "ef_construction": 512,
        "m": 16
      }
    }
  }
}
```

### Multi-Stage Retrieval (Section 7.6)

**Stage 1: Semantic Search (Agent R-03)**
- k-NN search with cosine similarity
- Retrieves top-50 candidates
- Duration: ~200ms

**Stage 2: Relevance Filtering (Agent R-04)**
- Applies 75% similarity threshold
- Filters to 25-30 high-relevance chunks
- Precision: 87%, Recall: 92%

**Stage 3: Reranking (Agent R-06)**
- Cross-encoder model for pairwise comparison
- Reranks to top-15 chunks
- Duration: ~300ms

**Stage 4: Context Assembly (Agent R-05)**
- Deduplication of similar chunks
- Merges adjacent chunks
- Token optimization (~12K tokens)
- Source attribution
- Duration: ~100ms

**Total Pipeline**: ~650ms, 92% token reduction

### Job Memory (Section 7.7)

Tracks state across stages:
- Executive summary
- Completed stages with key findings
- Current stage progress
- Gaps identified
- Budget and time constraints
- Quality scores and costs

Compressed to < 2K tokens for LLM context.

## Cost Tracking

The pipeline automatically tracks costs:

- **Embeddings**: $0.13 per 1M tokens (text-embedding-3-large)
- **Claude**: $3/M input tokens, $15/M output tokens
- **Total budget**: Configurable (default: $200)

Example costs for typical queries:
- Document indexing (1000 chunks): ~$0.50
- Single query: ~$0.02-0.05

## Configuration Options

### Chunking Settings

```python
from rag_pipeline.config.settings import ChunkingConfig

config = ChunkingConfig(
    chunk_size=800,           # tokens per chunk
    chunk_overlap=150,        # overlap between chunks
    preserve_metadata=True,   # preserve section info
    include_section_headers=True,
    include_page_numbers=True
)
```

### Retrieval Settings

```python
from rag_pipeline.config.settings import RetrievalConfig

config = RetrievalConfig(
    stage1_top_k=50,                    # broad recall
    similarity_threshold=0.75,          # 75% filtering
    stage3_top_k=15,                    # final reranking
    max_context_tokens=15000,           # token budget
    enable_deduplication=True,
    enable_chunk_merging=True,
    enable_source_attribution=True
)
```

## Troubleshooting

### PyTorch DLL Error (Windows)
```
OSError: [WinError 1114] A dynamic link library (DLL) initialization routine failed
```

**Solution**: Install Visual C++ Redistributable:
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Restart your computer

### OpenSearch Connection Error

**Check**:
1. AWS credentials are correct
2. OpenSearch endpoint is accessible
3. Security group allows access
4. IAM permissions include OpenSearch actions

### Out of Memory

**Solutions**:
1. Reduce batch size in document loading
2. Reduce `stage1_top_k` in retrieval config
3. Enable chunking for large documents

## Advanced Usage

### Custom Workflow

```python
from rag_pipeline.workflows.agentic_rag import SimpleRAGWorkflow
from rag_pipeline.agents.rag_agents import MultiStageRetriever

# Initialize retriever
retriever = MultiStageRetriever(
    vector_store=vector_store,
    embeddings=embeddings,
    config=retrieval_config
)

# Create workflow
workflow = SimpleRAGWorkflow(
    llm=claude_llm,
    retriever=retriever,
    job_memory=job_memory
)

# Query
result = workflow.query("Your question here")
```

### Using LangGraph Workflow

For more complex agentic behavior with query refinement:

```python
from rag_pipeline.workflows.agentic_rag import AgenticRAGWorkflow

workflow = AgenticRAGWorkflow(
    llm=claude_llm,
    retriever=retriever,
    job_memory=job_memory
)

result = workflow.query("Your question here")
```

## Performance Metrics

Typical performance (from architecture):
- **Retrieval time**: 650ms
- **Token reduction**: 92% (150K → 12K)
- **Precision**: 87%
- **Recall**: 92%
- **F1 Score**: 89.4%

## License

Internal use only - Thomson Reuters

## Contact

For questions or issues, please contact the project team.
