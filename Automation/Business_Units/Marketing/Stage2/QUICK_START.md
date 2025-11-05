# RAG Integration - Quick Start Guide

## Installation

### 1. Install RAG Dependencies

```bash
# Core dependencies (no C++ compiler needed)
pip install faiss-cpu sentence-transformers python-docx docx2txt

# Langchain packages
pip install langchain langchain-community langchain-core langchain-text-splitters
```

**Or install all at once:**
```bash
pip install -r rag_requirements.txt
```

**Note**: If you get errors about `duckdb` or `hnswlib`, you can ignore them - they're not required for the RAG integration.

### 2. Verify Installation

```python
# Test imports
from utils.rag_tools import initialize_rag, get_rag_context_for_use_case, is_rag_available
print("✓ RAG tools imported successfully")

from agents.agent2_web_research import WebResearchAgent
from agents.agent3_use_case_enricher import UseCaseEnricherAgent
print("✓ Agents imported successfully")
```

## Usage

### Standard Usage (with RAG)

```bash
cd "Automation/Business_Units/Marketing/Stage2"
python orchestrator.py
```

**First run**: Will build vector store (~30-60 seconds)
**Subsequent runs**: Loads from cache (<5 seconds)

### What Happens

1. **Orchestrator starts** → Initializes RAG once
2. **Agent2 (Web Research)** → Uses RAG to get relevant BU context for each use case
3. **Agent3 (Enrichment)** → Uses RAG to get relevant BU context for each use case
4. **Agents 4 & 5** → Continue as normal

### Console Output

You'll see:
```
[*] Initializing RAG Service...
    Building FAISS vector store from BU Intelligence documents...
[RAG Tools] Loading existing vector store from cache
[RAG Tools] ✓ Vector store loaded
[OK] RAG Service initialized and ready

[*] Running Agent 2: Web Research...
    [RAG] RAG-enhanced context will be used automatically

Researching: Content Generation
  [RAG] Using 3847 chars of RAG-enhanced context
```

## How It Works

### Automatic RAG Usage

Agents automatically check for RAG and use it when available:

```python
# Inside Agent2 and Agent3
if is_rag_available():
    bu_context = get_rag_context_for_use_case(use_case, "enrichment")
    print(f"  [RAG] Using {len(bu_context)} chars of RAG-enhanced context")
else:
    bu_context = bu_intelligence  # Fallback to standard
```

### Context Retrieval

- **Agent2 (Research)**: Retrieves top 5 relevant chunks per use case
- **Agent3 (Enrichment)**: Retrieves top 8 relevant chunks per use case

### Fallback Behavior

If RAG initialization fails:
- Agents automatically fall back to standard behavior
- No errors or crashes
- Uses truncated BU Intelligence text (old approach)

## Configuration

### File Paths (config.py)

```python
BU_INTELLIGENCE_PATH = "path/to/1b-MKTG-BU Intelligence.docx"
OPTIONAL_FILES = {
    "internal_intelligence": "path/to/internal.docx",
    "gap_analysis": "path/to/gap.docx"
}
```

### RAG Parameters (utils/rag_tools.py)

```python
embedding_model = "all-MiniLM-L6-v2"  # 384-dimensional embeddings
chunk_size = 1000  # characters
chunk_overlap = 200  # characters
persist_dir = "Stage2/rag_cache/"  # cache location
```

## Disable RAG (if needed)

```python
from orchestrator import Stage2Orchestrator

# Initialize with RAG disabled
orchestrator = Stage2Orchestrator(use_rag=False)
result = orchestrator.run()
```

## Force Rebuild Vector Store

```python
orchestrator = Stage2Orchestrator()
orchestrator.initialize_rag_service(force_rebuild=True)
result = orchestrator.run()
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'faiss'"

```bash
pip install faiss-cpu
```

### "ModuleNotFoundError: No module named 'sentence_transformers'"

```bash
pip install sentence-transformers
```

### "ModuleNotFoundError: No module named 'langchain'"

```bash
pip install langchain langchain-community
```

### Vector Store Not Building

1. Check BU Intelligence file path in `config.py`
2. Verify file exists: `os.path.exists(BU_INTELLIGENCE_PATH)`
3. Check disk space for cache directory
4. Look for error messages in console output

### Poor Retrieval Quality

1. Check document quality (ensure proper formatting)
2. Increase `top_k` in `utils/rag_tools.py` (line ~185)
3. Rebuild vector store: `initialize_rag(..., force_rebuild=True)`

## Cache Management

### Cache Location
```
Stage2/rag_cache/
├── faiss.index    (~10-50MB)
└── metadata.pkl   (~5-20MB)
```

### Clear Cache
```bash
cd "Stage2"
rm -rf rag_cache/
```

Next run will rebuild the vector store.

## Performance

| Metric | Value |
|--------|-------|
| First-time build | 30-60 seconds |
| Cached load | <5 seconds |
| Per-use-case retrieval | ~0.1 seconds |
| Memory usage | ~50-100 MB |
| Token savings | ~30-50% |

## Benefits

✅ **10x More Context**: Up to 8 relevant chunks vs truncated text
✅ **Semantic Relevance**: Only contextually relevant sections
✅ **Better Enrichment**: Higher quality outputs
✅ **Token Efficiency**: No wasted tokens on irrelevant context
✅ **Scalability**: Works with large documents
✅ **Automatic**: No manual configuration needed

## File Structure

```
Stage2/
├── utils/
│   └── rag_tools.py              # All RAG functionality
├── agents/
│   ├── agent2_web_research.py    # Uses RAG automatically
│   └── agent3_use_case_enricher.py  # Uses RAG automatically
├── orchestrator.py               # Initializes RAG once
├── config.py                     # File paths configuration
└── rag_cache/                    # Vector store cache (auto-created)
```

## Support

For issues:
1. Check console output for error messages
2. Verify all dependencies installed: `pip list`
3. Check file paths in `config.py`
4. Review [RAG_INTEGRATION_SUMMARY.md](RAG_INTEGRATION_SUMMARY.md) for details

## Summary

RAG integration is now **transparent and automatic**:
- Install dependencies
- Run orchestrator
- RAG builds vector store on first run
- Agents automatically use RAG-enhanced context
- No manual configuration needed

That's it! The system handles everything else automatically.
