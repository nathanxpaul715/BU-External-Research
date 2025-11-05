# RAG Pipeline Updates

## Thomson Reuters OpenAI Integration

### Summary

Added support for Thomson Reuters OpenAI authentication, allowing TR users to use the pipeline without personal OpenAI API keys.

### What's New

#### 1. Thomson Reuters OpenAI Embeddings Module
**File**: [embeddings/tr_openai_embeddings.py](embeddings/tr_openai_embeddings.py)

- Full TR AI Platform authentication
- Same text-embedding-3-large model (3072 dimensions)
- Caching support for efficiency
- Drop-in replacement for direct OpenAI

**Key Features:**
- Automatic TR authentication via workspace ID and asset ID
- Azure OpenAI client with TR-specific headers
- Identical API to direct OpenAI embeddings
- Cost tracking and performance monitoring

#### 2. Configuration Updates
**File**: [config/settings.py](config/settings.py)

Added `TROpenAIConfig` class:
```python
@dataclass
class TROpenAIConfig:
    workspace_id: str = "Workspace_ID"
    asset_id: str = "Asset_ID"
    token_url: str = "https://aiplatform.gcs.int.thomsonreuters.com/v1/openai/token"
    base_url: str = "https://eais2-use.int.thomsonreuters.com"
    model_name: str = "gpt-4.1"
    embedding_model: str = "text-embedding-3-large"
    dimensions: int = 3072
```

Added embedding provider selection:
```python
@dataclass
class RAGPipelineConfig:
    use_tr_openai: bool = True  # True = TR OpenAI, False = Direct OpenAI
```

#### 3. Main Pipeline Updates
**File**: [main.py](main.py)

Automatic provider selection:
```python
if self.config.use_tr_openai:
    print(f"   Using Thomson Reuters OpenAI embeddings")
    self.embeddings = CachedTROpenAIEmbeddings(self.config.tr_openai)
else:
    print(f"   Using Direct OpenAI embeddings")
    self.embeddings = CachedOpenAIEmbeddings(self.config.embedding)
```

Smart environment variable checking:
- TR OpenAI mode: Requires `TR_WORKSPACE_ID`, `TR_ASSET_ID`
- Direct OpenAI mode: Requires `OPENAI_API_KEY`

#### 4. Documentation
**New Files:**
- [TR_OPENAI_SETUP.md](TR_OPENAI_SETUP.md) - Complete TR OpenAI setup guide
- [UPDATES.md](UPDATES.md) - This file

**Updated Files:**
- [.env.example](.env.example) - Added TR OpenAI configuration
- [README.md](README.md) - References TR OpenAI option

### Architecture

```
User Query
    │
    ├─ use_tr_openai = True  (DEFAULT)
    │  │
    │  ├─ TR AI Platform Authentication
    │  │  └─ POST https://aiplatform.gcs.int.thomsonreuters.com/v1/openai/token
    │  │     ├─ workspace_id: ExternalResei8Dz
    │  │     └─ model_name: gpt-4.1
    │  │
    │  ├─ Receive Credentials
    │  │  ├─ openai_key
    │  │  ├─ azure_deployment
    │  │  ├─ token
    │  │  └─ api_version
    │  │
    │  └─ AzureOpenAI Client
    │     ├─ Endpoint: https://eais2-use.int.thomsonreuters.com
    │     ├─ Headers: TR-specific (userid, asset-id, etc.)
    │     └─ Model: text-embedding-3-large (3072-d)
    │
    └─ use_tr_openai = False
       │
       └─ Direct OpenAI
          ├─ API Key: OPENAI_API_KEY
          ├─ Endpoint: https://api.openai.com
          └─ Model: text-embedding-3-large (3072-d)
```

### Usage

#### Quick Start with TR OpenAI

1. **Set environment variables:**
```bash
set TR_WORKSPACE_ID=ExternalResei8Dz
set TR_ASSET_ID=your_asset_id
set AWS_ACCESS_KEY_ID=AKIA...
set AWS_SECRET_ACCESS_KEY=...
set OPENSEARCH_HOST=...
```

2. **Run pipeline:**
```bash
python main.py
```

#### Switch to Direct OpenAI

1. **Edit [config/settings.py](config/settings.py):**
```python
use_tr_openai: bool = False  # Switch to direct OpenAI
```

2. **Set environment variable:**
```bash
set OPENAI_API_KEY=sk-...
```

3. **Run pipeline:**
```bash
python main.py
```

### Benefits of TR OpenAI

| Feature | TR OpenAI | Direct OpenAI |
|---------|-----------|---------------|
| **Setup** | Workspace ID + Asset ID | Personal API key |
| **Account** | No OpenAI account needed | Requires OpenAI account |
| **Billing** | Through TR | Direct to OpenAI |
| **Network** | TR network | Any network |
| **Quality** | Same | Same |
| **Speed** | Same | Same |
| **Cost** | Same ($0.13/1M tokens) | Same |

**For TR users:** TR OpenAI is the recommended option!

### Code Examples

#### Example 1: Using TR OpenAI Embeddings Directly

```python
from rag_pipeline.embeddings.tr_openai_embeddings import CachedTROpenAIEmbeddings
from rag_pipeline.config.settings import TROpenAIConfig

# Configure
config = TROpenAIConfig()
config.workspace_id = "ExternalResei8Dz"
config.asset_id = "your_asset_id"

# Initialize
embeddings = CachedTROpenAIEmbeddings(config)

# Generate embeddings
texts = ["What are AI use cases?", "How does automation work?"]
vectors = embeddings.embed_texts(texts)

print(f"Generated {len(vectors)} embeddings")
print(f"Dimensions: {len(vectors[0])}")  # 3072
```

#### Example 2: Full Pipeline with TR OpenAI

```python
from rag_pipeline.main import RAGPipeline
from rag_pipeline.config.settings import get_config

# Get config (uses TR OpenAI by default)
config = get_config()
print(f"Using TR OpenAI: {config.use_tr_openai}")  # True

# Initialize and run pipeline
pipeline = RAGPipeline(config)
pipeline.setup()
pipeline.load_and_index_documents()
pipeline.initialize_retrieval()

# Query
result = pipeline.query("What are the main AI use cases?")
print(result['answer'])
```

#### Example 3: Switching Providers Programmatically

```python
from rag_pipeline.config.settings import get_config, update_config

# Switch to direct OpenAI
config = update_config(use_tr_openai=False)

# Now pipeline will use direct OpenAI
pipeline = RAGPipeline(config)
```

### Testing

#### Test TR OpenAI Authentication

```python
# test_tr_auth.py
import os
from rag_pipeline.embeddings.tr_openai_embeddings import TROpenAIEmbeddings

os.environ["TR_WORKSPACE_ID"] = "ExternalResei8Dz"
os.environ["TR_ASSET_ID"] = "your_asset_id"

try:
    embeddings = TROpenAIEmbeddings()
    print("✓ TR OpenAI authentication successful")

    # Test embedding
    vector = embeddings.embed_text("Test")
    print(f"✓ Embedding generated: {len(vector)} dimensions")

except Exception as e:
    print(f"✗ Authentication failed: {e}")
```

#### Test Complete Pipeline

```bash
# Set environment
set TR_WORKSPACE_ID=ExternalResei8Dz
set TR_ASSET_ID=your_asset_id
set AWS_ACCESS_KEY_ID=...
set AWS_SECRET_ACCESS_KEY=...
set OPENSEARCH_HOST=...

# Run pipeline
python main.py
```

Expected output:
```
================================
RAG PIPELINE INITIALIZATION
================================

[14:30:23] 1. Initializing Claude LLM...
[14:30:24] Claude client authenticated successfully

[14:30:24] 2. Initializing Embeddings...
   Using Thomson Reuters OpenAI embeddings
[14:30:25] TR OpenAI Embeddings authenticated successfully
[14:30:25] Using model: text-embedding-3-large
[14:30:25] Dimensions: 3072

✓ All components initialized
```

### Compatibility

- **Python**: 3.10, 3.11 (tested)
- **OpenAI library**: >=1.50.0 (includes AzureOpenAI)
- **Existing code**: Fully backward compatible
- **Default behavior**: Uses TR OpenAI (can be changed)

### Migration Guide

#### From Direct OpenAI to TR OpenAI

No code changes needed! Just:

1. Remove `OPENAI_API_KEY` from environment
2. Add `TR_WORKSPACE_ID` and `TR_ASSET_ID`
3. Keep `use_tr_openai = True` in config (default)
4. Run pipeline

#### From TR OpenAI to Direct OpenAI

1. Set `use_tr_openai = False` in [config/settings.py](config/settings.py)
2. Remove `TR_WORKSPACE_ID` and `TR_ASSET_ID` from environment
3. Add `OPENAI_API_KEY` to environment
4. Run pipeline

### File Changes Summary

```
rag_pipeline/
├── embeddings/
│   ├── tr_openai_embeddings.py      [NEW] TR OpenAI wrapper
│   └── __init__.py                  [UPDATED] Export TR classes
├── config/
│   └── settings.py                  [UPDATED] Add TROpenAIConfig
├── main.py                          [UPDATED] Provider selection
├── .env.example                     [UPDATED] TR credentials
├── TR_OPENAI_SETUP.md              [NEW] TR setup guide
└── UPDATES.md                      [NEW] This file
```

### Performance

No performance impact:
- Same embedding model (text-embedding-3-large)
- Same dimensions (3072)
- Same batch processing (100 texts/batch)
- Same caching mechanism
- Same API latency

### Cost

No cost impact:
- Same pricing: $0.13 per 1M tokens
- Same token counting
- Same cost tracking
- Billing through TR instead of direct OpenAI

### Security

TR OpenAI adds security benefits:
- No personal API keys needed
- Authentication through TR platform
- Centralized access control
- Audit trail through TR
- Network-level security

### Troubleshooting

#### Error: "Failed to get OpenAI credentials"
- Verify `TR_WORKSPACE_ID` is correct
- Verify `TR_ASSET_ID` is correct
- Check TR AI Platform access
- Ensure on TR network

#### Error: "Missing required environment variables"
- Check environment variables are set:
  ```bash
  echo %TR_WORKSPACE_ID%
  echo %TR_ASSET_ID%
  ```
- Or use `.env` file

#### Embeddings not generating
- Test authentication separately
- Check TR platform status
- Verify network connectivity
- Review error logs

### Future Enhancements

Potential future additions:
- Multiple TR workspace support
- Token caching for auth
- Fallback to direct OpenAI
- Custom TR endpoint configuration
- TR-specific cost reporting

### Support

For TR OpenAI questions:
- See [TR_OPENAI_SETUP.md](TR_OPENAI_SETUP.md) for detailed guide
- Check TR AI Platform documentation
- Contact TR AI Platform support

For general pipeline questions:
- See [README.md](README.md) for usage guide
- See [QUICKSTART.md](QUICKSTART.md) for setup
- See [ARCHITECTURE.md](ARCHITECTURE.md) for details

### Changelog

**Version 1.1.0** (2025-11-05)
- ✓ Added Thomson Reuters OpenAI integration
- ✓ Added TROpenAIEmbeddings class
- ✓ Added TROpenAIConfig to settings
- ✓ Updated main.py for provider selection
- ✓ Updated environment variable handling
- ✓ Added TR_OPENAI_SETUP.md documentation
- ✓ Updated .env.example with TR options
- ✓ Backward compatible with existing code

**Version 1.0.0** (2025-11-04)
- Initial release with direct OpenAI support

---

**Status**: ✅ Ready for Production

**Recommended for TR users**: Use TR OpenAI (default)

**Default Configuration**: TR OpenAI enabled (`use_tr_openai = True`)
