# Thomson Reuters OpenAI Setup Guide

This guide explains how to use the RAG pipeline with Thomson Reuters OpenAI authentication instead of direct OpenAI API keys.

## Overview

The pipeline supports two modes for OpenAI embeddings:

1. **Thomson Reuters OpenAI** (RECOMMENDED for TR users)
   - Uses TR AI Platform authentication
   - No need for personal OpenAI API keys
   - Billing through TR infrastructure
   - Same text-embedding-3-large model (3072 dimensions)

2. **Direct OpenAI API**
   - Requires personal OpenAI API key
   - Direct billing to your OpenAI account

## Configuration

### Step 1: Set Embedding Provider

Edit [config/settings.py](config/settings.py):

```python
@dataclass
class RAGPipelineConfig:
    """Complete RAG Pipeline Configuration"""
    # ...

    # Embedding provider selection
    use_tr_openai: bool = True  # True = TR OpenAI (default), False = Direct OpenAI
```

**Default is `True`** - uses Thomson Reuters OpenAI.

### Step 2: Get Your TR Credentials

You need two values from the TR AI Platform:

1. **Workspace ID**: Your workspace identifier
2. **Asset ID**: Your asset identifier

#### How to Find These:

1. Open the **TR AI Platform Workspace Console**
2. Navigate to your workspace
3. Copy your **Workspace ID**
4. Copy your **Asset ID**

Example values (replace with yours):
```
Workspace ID: ExternalResei8Dz
Asset ID: your-asset-id-here
```

### Step 3: Set Environment Variables

#### Option A: Using .env file (Recommended)

1. Copy the example file:
```bash
copy .env.example .env
```

2. Edit `.env` and set your TR credentials:
```bash
# Thomson Reuters OpenAI Configuration
TR_WORKSPACE_ID=ExternalResei8Dz
TR_ASSET_ID=your_asset_id_here

# AWS Configuration (for OpenSearch)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_secret_key
OPENSEARCH_HOST=your-collection.us-east-1.aoss.amazonaws.com
```

#### Option B: Direct in settings.py

Edit [config/settings.py](config/settings.py):

```python
@dataclass
class TROpenAIConfig:
    """Thomson Reuters OpenAI Configuration"""
    workspace_id: str = "ExternalResei8Dz"  # Your workspace ID
    asset_id: str = "your-asset-id-here"    # Your asset ID
    # ... rest of config
```

## How TR OpenAI Authentication Works

The authentication flow (based on your test_api.py):

```python
# 1. Request token from TR AI Platform
payload = {
    "workspace_id": "ExternalResei8Dz",
    "model_name": "gpt-4.1"
}

response = POST("https://aiplatform.gcs.int.thomsonreuters.com/v1/openai/token", payload)

# 2. Receive credentials
credentials = {
    "openai_key": "...",
    "azure_deployment": "...",
    "openai_api_version": "...",
    "token": "..."
}

# 3. Initialize AzureOpenAI client with TR headers
client = AzureOpenAI(
    azure_endpoint="https://eais2-use.int.thomsonreuters.com",
    api_key=credentials["openai_key"],
    api_version=credentials["openai_api_version"],
    azure_deployment=credentials["azure_deployment"],
    default_headers={
        "Authorization": f"Bearer {credentials['token']}",
        "x-tr-userid": workspace_id,
        "x-tr-asset-id": asset_id,
        # ... other TR headers
    }
)

# 4. Generate embeddings
response = client.embeddings.create(
    model="text-embedding-3-large",
    input="your text here",
    dimensions=3072
)
```

This is all handled automatically by the `TROpenAIEmbeddings` class!

## Usage Example

```python
from rag_pipeline.embeddings.tr_openai_embeddings import CachedTROpenAIEmbeddings
from rag_pipeline.config.settings import TROpenAIConfig

# Initialize (will authenticate automatically)
embeddings = CachedTROpenAIEmbeddings()

# Generate embedding
text = "What are the main AI use cases?"
embedding = embeddings.embed_text(text)

print(f"Embedding dimensions: {len(embedding)}")  # 3072
```

## Complete Pipeline with TR OpenAI

```python
from rag_pipeline.main import RAGPipeline

# Initialize pipeline (uses TR OpenAI by default)
pipeline = RAGPipeline()

# Setup components
pipeline.setup()
# Output:
#   [14:30:23] 1. Initializing Claude LLM...
#   [14:30:24] 2. Initializing Embeddings...
#      Using Thomson Reuters OpenAI embeddings
#   [14:30:25] TR OpenAI Embeddings authenticated successfully
#   [14:30:25] Using model: text-embedding-3-large
#   [14:30:25] Dimensions: 3072

# Load and index documents
pipeline.load_and_index_documents()

# Initialize retrieval
pipeline.initialize_retrieval()

# Query
result = pipeline.query("What are the main AI use cases?")
print(result['answer'])
```

## Running the Pipeline

```bash
# Make sure environment variables are set
echo %TR_WORKSPACE_ID%
echo %TR_ASSET_ID%

# Run pipeline
python main.py
```

Expected output:
```
================================
RAG PIPELINE INITIALIZATION
Job ID: job-20251104-143022
================================

[14:30:23] 1. Initializing Claude LLM...
[14:30:24] Claude client authenticated successfully

[14:30:24] 2. Initializing Embeddings...
   Using Thomson Reuters OpenAI embeddings
[14:30:25] TR OpenAI Embeddings authenticated successfully
[14:30:25] Using model: text-embedding-3-large
[14:30:25] Dimensions: 3072

[14:30:25] 3. Initializing OpenSearch Vector Store...
...
```

## Switching Between TR OpenAI and Direct OpenAI

### To Use TR OpenAI (Default)
1. Set `use_tr_openai = True` in [config/settings.py](config/settings.py)
2. Set environment variables: `TR_WORKSPACE_ID`, `TR_ASSET_ID`
3. Run pipeline

### To Use Direct OpenAI
1. Set `use_tr_openai = False` in [config/settings.py](config/settings.py)
2. Set environment variable: `OPENAI_API_KEY`
3. Run pipeline

## Troubleshooting

### Error: "Failed to get OpenAI credentials"

**Check:**
- Workspace ID is correct
- Asset ID is correct
- You have access to the TR AI Platform
- Your workspace has OpenAI access enabled

**Solution:**
```bash
# Verify credentials
echo %TR_WORKSPACE_ID%
echo %TR_ASSET_ID%

# Test authentication
python -c "from rag_pipeline.embeddings.tr_openai_embeddings import TROpenAIEmbeddings; e = TROpenAIEmbeddings()"
```

### Error: "Missing required environment variables: TR_WORKSPACE_ID"

**Solution:**
Set the environment variables:

```bash
# Windows Command Prompt
set TR_WORKSPACE_ID=ExternalResei8Dz
set TR_ASSET_ID=your_asset_id

# Windows PowerShell
$env:TR_WORKSPACE_ID="ExternalResei8Dz"
$env:TR_ASSET_ID="your_asset_id"

# Or use .env file (recommended)
```

### Error: "Connection timeout"

**Check:**
- You're on the Thomson Reuters network
- TR AI Platform endpoint is accessible: `https://aiplatform.gcs.int.thomsonreuters.com`
- Firewall/proxy settings allow access

### Embeddings generation is slow

**Normal performance:**
- 100 texts per batch
- ~2-5 minutes for 500 documents
- Same speed as direct OpenAI

**If slower:**
- Check network connection
- Verify not hitting rate limits
- Check TR platform status

## Cost Tracking

TR OpenAI embeddings have the same cost as direct OpenAI:
- **Model**: text-embedding-3-large
- **Cost**: $0.13 per 1M tokens
- **Typical**: ~$0.50 for 1000 document chunks

Cost is tracked automatically:
```python
result = pipeline.load_and_index_documents()
# Output:
#   Embedding cost: $0.0473
#   Total cost: $0.0473
```

## Comparison: TR OpenAI vs Direct OpenAI

| Feature | TR OpenAI | Direct OpenAI |
|---------|-----------|---------------|
| **Authentication** | TR workspace ID + asset ID | Personal API key |
| **Billing** | Through TR | Direct to OpenAI account |
| **Setup** | No OpenAI account needed | Requires OpenAI account |
| **Model** | text-embedding-3-large | text-embedding-3-large |
| **Dimensions** | 3072 | 3072 |
| **Quality** | Identical | Identical |
| **Speed** | Same | Same |
| **Cost** | $0.13/1M tokens | $0.13/1M tokens |
| **Network** | TR network required | Any network |

## Advanced Configuration

### Custom TR Settings

Edit [config/settings.py](config/settings.py):

```python
@dataclass
class TROpenAIConfig:
    """Thomson Reuters OpenAI Configuration"""
    workspace_id: str = "ExternalResei8Dz"
    asset_id: str = "your-asset-id"
    token_url: str = "https://aiplatform.gcs.int.thomsonreuters.com/v1/openai/token"
    base_url: str = "https://eais2-use.int.thomsonreuters.com"
    model_name: str = "gpt-4.1"
    embedding_model: str = "text-embedding-3-large"
    dimensions: int = 3072  # Can be 1536 or 3072
```

### Using Different Embedding Dimensions

To use 1536 dimensions instead of 3072:

```python
config = TROpenAIConfig()
config.dimensions = 1536

embeddings = TROpenAIEmbeddings(config)
```

Note: Also update OpenSearch index dimension in vector store!

## Testing TR OpenAI Setup

Quick test script:

```python
# test_tr_openai.py
import os
from rag_pipeline.embeddings.tr_openai_embeddings import TROpenAIEmbeddings
from rag_pipeline.config.settings import TROpenAIConfig

# Set credentials
os.environ["TR_WORKSPACE_ID"] = "ExternalResei8Dz"
os.environ["TR_ASSET_ID"] = "your_asset_id"

# Initialize
config = TROpenAIConfig()
embeddings = TROpenAIEmbeddings(config)

# Test embedding
text = "Hello, world!"
embedding = embeddings.embed_text(text)

print(f"✓ Authentication successful")
print(f"✓ Embedding generated: {len(embedding)} dimensions")
print(f"✓ First 5 values: {embedding[:5]}")
```

Run:
```bash
python test_tr_openai.py
```

Expected output:
```
[14:30:25] TR OpenAI Embeddings authenticated successfully
[14:30:25] Using model: text-embedding-3-large
[14:30:25] Dimensions: 3072
✓ Authentication successful
✓ Embedding generated: 3072 dimensions
✓ First 5 values: [0.123, -0.456, 0.789, ...]
```

## Support

For TR OpenAI issues:
1. Verify credentials in TR AI Platform console
2. Check network connectivity
3. Review TR AI Platform documentation
4. Contact TR AI Platform support

For pipeline issues:
1. Check [README.md](README.md) for general help
2. Review [QUICKSTART.md](QUICKSTART.md) for setup
3. Check logs for detailed error messages

## Summary

**For Thomson Reuters users, TR OpenAI is the recommended approach:**
- ✓ No need for personal OpenAI account
- ✓ Billing through TR infrastructure
- ✓ Same quality and performance
- ✓ Simple setup with workspace ID and asset ID

Just set your `TR_WORKSPACE_ID` and `TR_ASSET_ID`, and you're ready to go! 🚀
