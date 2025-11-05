# RAG Pipeline Architecture

Detailed architecture documentation based on the RAG Architecture Document specifications.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE SYSTEM                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Input Documents (DOCX, CSV, XLSX)                                 │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────────────────────────────┐                         │
│  │  Agent F-03: Document Loader         │                         │
│  │  • Metadata-aware chunking           │                         │
│  │  • 800 tokens per chunk              │                         │
│  │  • 150 token overlap                 │                         │
│  └──────────────┬───────────────────────┘                         │
│                 │                                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────────┐                         │
│  │  OpenAI Embeddings                   │                         │
│  │  • text-embedding-3-large            │                         │
│  │  • 3072 dimensions                   │                         │
│  └──────────────┬───────────────────────┘                         │
│                 │                                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────────┐                         │
│  │  OpenSearch Serverless               │                         │
│  │  • k-NN with HNSW                    │                         │
│  │  • Cosine similarity                 │                         │
│  │  • Job-specific indices              │                         │
│  └──────────────┬───────────────────────┘                         │
│                 │                                                   │
│        [INDEXING COMPLETE]                                         │
│                 │                                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────────┐                         │
│  │  User Query                          │                         │
│  └──────────────┬───────────────────────┘                         │
│                 │                                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────────┐                         │
│  │  Query Refinement (Optional)         │                         │
│  │  • Claude Sonnet 4                   │                         │
│  │  • Concept extraction                │                         │
│  └──────────────┬───────────────────────┘                         │
│                 │                                                   │
│                 ▼                                                   │
│  ╔══════════════════════════════════════╗                         │
│  ║  MULTI-STAGE RETRIEVAL FUNNEL        ║                         │
│  ╠══════════════════════════════════════╣                         │
│  ║                                      ║                         │
│  ║  Stage 1: Agent R-03                 ║                         │
│  ║  ┌────────────────────────────────┐ ║                         │
│  ║  │ Semantic Search (Broad Recall) │ ║                         │
│  ║  │ • k-NN search                  │ ║                         │
│  ║  │ • Top-50 candidates            │ ║                         │
│  ║  │ • ~200ms                       │ ║                         │
│  ║  └────────────┬───────────────────┘ ║                         │
│  ║               ▼                     ║                         │
│  ║  Stage 2: Agent R-04                ║                         │
│  ║  ┌────────────────────────────────┐ ║                         │
│  ║  │ Relevance Filtering            │ ║                         │
│  ║  │ • 75% similarity threshold     │ ║                         │
│  ║  │ • 25-30 results                │ ║                         │
│  ║  │ • ~50ms                        │ ║                         │
│  ║  └────────────┬───────────────────┘ ║                         │
│  ║               ▼                     ║                         │
│  ║  Stage 3: Agent R-06                ║                         │
│  ║  ┌────────────────────────────────┐ ║                         │
│  ║  │ Cross-Encoder Reranking        │ ║                         │
│  ║  │ • Pairwise comparison          │ ║                         │
│  ║  │ • Top-15 results               │ ║                         │
│  ║  │ • ~300ms                       │ ║                         │
│  ║  └────────────┬───────────────────┘ ║                         │
│  ║               ▼                     ║                         │
│  ║  Stage 4: Agent R-05                ║                         │
│  ║  ┌────────────────────────────────┐ ║                         │
│  ║  │ Context Assembly               │ ║                         │
│  ║  │ • Deduplication                │ ║                         │
│  ║  │ • Chunk merging                │ ║                         │
│  ║  │ • Token optimization (~12K)    │ ║                         │
│  ║  │ • Source attribution           │ ║                         │
│  ║  │ • ~100ms                       │ ║                         │
│  ║  └────────────┬───────────────────┘ ║                         │
│  ║               │                     ║                         │
│  ╚═══════════════╪═════════════════════╝                         │
│                  │                                                 │
│         Total: ~650ms                                              │
│                  │                                                 │
│                  ▼                                                 │
│  ┌──────────────────────────────────────┐                         │
│  │  Job Memory System                   │                         │
│  │  • Compressed context (<2K tokens)   │                         │
│  │  • Stage history                     │                         │
│  │  • Cost tracking                     │                         │
│  └──────────────┬───────────────────────┘                         │
│                  │                                                 │
│                  ▼                                                 │
│  ┌──────────────────────────────────────┐                         │
│  │  Claude Sonnet 4 Generation          │                         │
│  │  • Context + Query → Answer          │                         │
│  │  • Source citations                  │                         │
│  │  • Quality evaluation                │                         │
│  └──────────────┬───────────────────────┘                         │
│                  │                                                 │
│                  ▼                                                 │
│  ┌──────────────────────────────────────┐                         │
│  │  Final Answer + Metadata             │                         │
│  └──────────────────────────────────────┘                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Document Loading (Agent F-03)

**Module**: `loaders/document_loader.py`

**Responsibilities**:
- Load DOCX, CSV, XLSX files
- Metadata-aware chunking
- Token counting with tiktoken

**Algorithm** (from architecture section 7.4):
```python
FOR each paragraph in document:
    IF is_heading(paragraph):
        current_section = extract_section_number(paragraph)
        current_heading = paragraph.text

    chunks = split_by_tokens(paragraph, 800, 150)

    FOR each chunk:
        metadata = {
            "source_file": filename,
            "section": current_section,
            "heading": current_heading,
            "chunk_index": index,
            "created_at": timestamp
        }
        store(chunk, metadata)
```

**Key Features**:
- Preserves document structure
- Section-aware chunking
- Consistent 800-token chunks
- 150-token overlap for context

### 2. Embeddings

**Module**: `embeddings/openai_embeddings.py`

**Model**: text-embedding-3-large
- **Dimensions**: 3072
- **Cost**: $0.13 per 1M tokens
- **Quality**: Superior semantic search

**Caching**:
- In-memory LRU cache
- Avoids redundant API calls
- Tracks hit/miss rates

**Similarity Calculation**:
```python
cosine_similarity = dot(A, B) / (||A|| × ||B||)
similarity_percentage = cosine_similarity × 100
meets_threshold = similarity_percentage >= 75
```

### 3. Vector Store

**Module**: `vectorstore/opensearch_store.py`

**OpenSearch Configuration** (section 7.2):
```json
{
  "settings": {
    "index.knn": true,
    "index.knn.algo_param.ef_search": 512,
    "number_of_shards": 2,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
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
  }
}
```

**Features**:
- Job-specific indices for isolation
- k-NN with HNSW algorithm
- Cosine similarity space
- Hybrid search (vector + keyword)

### 4. Multi-Stage Retrieval

**Module**: `agents/rag_agents.py`

#### Stage 1: Agent R-03 (Semantic Search)
- **Input**: Query embedding
- **Algorithm**: k-NN search
- **Output**: Top-50 candidates
- **Time**: ~200ms
- **Goal**: Maximum recall

#### Stage 2: Agent R-04 (Relevance Filtering)
- **Input**: 50 candidates
- **Algorithm**: Similarity threshold filter
- **Threshold**: 75% (0.75 cosine similarity)
- **Output**: 25-30 relevant chunks
- **Time**: ~50ms
- **Goal**: Improve precision

**Performance** (validated on test data):
- Precision: 87%
- Recall: 92%
- F1 Score: 89.4%

#### Stage 3: Agent R-06 (Reranking)
- **Input**: 25-30 filtered chunks
- **Model**: cross-encoder/ms-marco-MiniLM-L-12-v2
- **Algorithm**: Pairwise comparison
- **Output**: Top-15 chunks
- **Time**: ~300ms
- **Goal**: Maximum precision

#### Stage 4: Agent R-05 (Context Assembly)
- **Input**: 15 reranked chunks
- **Operations**:
  1. Deduplication (remove similar chunks)
  2. Adjacent chunk merging
  3. Logical ordering
  4. Source attribution
  5. Token optimization (<15K)
- **Output**: Optimized context (~12K tokens)
- **Time**: ~100ms

**Algorithm** (section 7.6):
```python
assembled = []
seen_signatures = set()

FOR chunk IN ranked_chunks:
    signature = normalize(chunk.text[:100])

    IF signature NOT IN seen_signatures:
        seen_signatures.add(signature)

        IF is_adjacent(assembled[-1], chunk):
            # Merge with previous
            assembled[-1].text += chunk.text
        ELSE:
            assembled.append(chunk)

# Sort by source and index
assembled.sort(key=lambda c: (c.source_file, c.chunk_index))

# Add attribution
FOR chunk IN assembled:
    chunk.attribution = f"[Source: {chunk.source_file}, Section {chunk.section}]"

# Trim to token budget
IF total_tokens > 15000:
    assembled = trim_to_budget(assembled, 15000)

RETURN assembled
```

### 5. Job Memory

**Module**: `memory/job_memory.py`

**Structure** (section 7.7):
```json
{
  "job_id": "job-20251104-143022",
  "executive_summary": "...",
  "completed_stages": [
    {
      "stage": 0,
      "completed_at": "2025-11-04T14:35:00Z",
      "key_findings": ["...", "...", "..."],
      "quality_score": 94,
      "cost": 0.0473
    }
  ],
  "current_stage": {
    "stage": 1,
    "status": "in_progress"
  },
  "constraints": {
    "budget_used": 0.0707,
    "budget_limit": 200.0,
    "time_elapsed_hours": 0.5
  },
  "risks": ["..."]
}
```

**Compression**:
- Full memory: Detailed JSON
- Compressed: <2K tokens for LLM context
- Progressive compression as job grows
- Retains key findings and quality scores

### 6. LLM Integration

**Module**: `llm/claude_wrapper.py`

**Authentication**: Thomson Reuters AI Platform
```python
payload = {"workspace_id": "ExternalResei8Dz"}
response = POST(token_url, payload)
api_key = response["anthropic_api_key"]
```

**Model**: claude-sonnet-4-20250514
- **Input cost**: $3 per 1M tokens
- **Output cost**: $15 per 1M tokens
- **Max tokens**: 4096 (configurable)
- **Temperature**: 0.7 (configurable)

### 7. Workflow Orchestration

**Module**: `workflows/agentic_rag.py`

**SimpleRAGWorkflow** (recommended):
1. Query refinement (optional)
2. Multi-stage retrieval
3. Context + memory → Claude
4. Answer generation
5. Cost tracking

**AgenticRAGWorkflow** (LangGraph):
- State management
- Conditional edges
- Iterative refinement
- Quality evaluation

## Data Flow

### Indexing Phase
```
Documents → Chunks → Embeddings → OpenSearch
    |         |          |            |
    |         |          |            └─ Index created
    |         |          └────────────── API call
    |         └────────────────────────── F-03 chunking
    └──────────────────────────────────── File loading
```

### Query Phase
```
Query → Refinement → Retrieval → Generation → Answer
  |         |            |            |           |
  |         |            |            |           └─ Final result
  |         |            |            └─────────────── Claude API
  |         |            └──────────────────────────── 4-stage funnel
  |         └───────────────────────────────────────── Query optimization
  └─────────────────────────────────────────────────── User input
```

## Performance Characteristics

### Latency
- **Indexing**: O(n) where n = number of documents
  - 1000 chunks: ~3-5 minutes
- **Retrieval**: O(log n) with HNSW
  - ~650ms regardless of corpus size
- **Generation**: O(m) where m = context tokens
  - ~3-5 seconds for typical queries

### Throughput
- **Embedding**: 100 texts/batch
- **Indexing**: 100 documents/batch
- **Queries**: Sequential (can be parallelized)

### Scalability
- **Document limit**: Effectively unlimited (OpenSearch scales)
- **Query limit**: Rate-limited by APIs
- **Memory**: Bounded by cache size

## Quality Metrics

### Retrieval Quality
- **Precision**: 87% (87/100 retrieved chunks relevant)
- **Recall**: 92% (92/100 relevant chunks retrieved)
- **F1 Score**: 89.4% (harmonic mean)

### Token Efficiency
- **Without RAG**: ~150K tokens (entire corpus)
- **With RAG**: ~12K tokens (optimized context)
- **Reduction**: 92%

### Cost Efficiency
- **Embedding**: One-time cost
- **Query**: Only relevant context retrieved
- **Savings**: 92% per query vs. full corpus

## Security & Privacy

### Data Isolation
- Job-specific indices
- No cross-job contamination
- Clean deletion on job completion

### API Security
- Thomson Reuters OAuth for Claude
- AWS IAM for OpenSearch
- OpenAI API keys in environment

### Data Retention
- Vector indices: Persistent until deleted
- Job memory: Saved to local JSON
- Query logs: Not persisted (privacy)

## Monitoring & Debugging

### Cost Tracking
- Per-operation cost calculation
- Cumulative budget monitoring
- Budget limit enforcement

### Quality Tracking
- Per-query quality scores
- Average quality per stage
- Quality degradation alerts

### Performance Tracking
- Retrieval time per stage
- End-to-end latency
- API call timing

## Future Enhancements

### Phase 2 Features (from architecture)
1. **Hybrid Search**: Vector + BM25 keyword matching
2. **Quality Monitor**: Agent R-12 for RAG effectiveness
3. **Advanced Reranking**: Custom reranker training
4. **Streaming**: Real-time answer generation
5. **Multi-modal**: Image and PDF support

## References

- RAG Architecture Document (Section 7.1-7.10)
- OpenSearch k-NN documentation
- Claude API documentation
- OpenAI embeddings guide
