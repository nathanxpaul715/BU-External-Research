# Quick Start Guide

Get the RAG pipeline running in 5 minutes!

## Prerequisites

- Python 3.10 or 3.11 (Python 3.12 may have PyTorch compatibility issues on Windows)
- OpenAI API key
- AWS account with OpenSearch Serverless access
- Visual C++ Redistributable (Windows only)

## Step 1: Fix PyTorch DLL Issue (Windows Only)

**Download and install Visual C++ Redistributable:**
https://aka.ms/vs/17/release/vc_redist.x64.exe

**Restart your computer** after installation.

## Step 2: Install Dependencies

```bash
# Navigate to the rag_pipeline directory
cd "C:\Users\6122504\Documents\BU External Research\BU-External-Research\rag_pipeline"

# Install requirements
pip install -r requirements.txt
```

## Step 3: Set Up Environment Variables

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and add your credentials:

**For Thomson Reuters users (Default):**
```
TR_WORKSPACE_ID=ExternalResei8Dz
TR_ASSET_ID=your_asset_id_here
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-secret-key
OPENSEARCH_HOST=your-collection.us-east-1.aoss.amazonaws.com
```

**For external users (Direct OpenAI):**
- Set `use_tr_openai = False` in `config/settings.py`
- Then set:
```
OPENAI_API_KEY=sk-your-actual-key-here
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-secret-key
OPENSEARCH_HOST=your-collection.us-east-1.aoss.amazonaws.com
```

## Step 4: Create OpenSearch Serverless Collection

### Option A: Using AWS Console

1. Go to AWS Console > OpenSearch Service > Serverless
2. Click "Create collection"
3. Choose "Search" as the collection type
4. Set collection name (e.g., "rag-pipeline")
5. Configure network settings (allow access from your IP)
6. Configure data access (grant your IAM user access)
7. Wait for collection to be created
8. Copy the OpenSearch endpoint to your `.env` file

### Option B: Using AWS CLI

```bash
aws opensearchserverless create-collection \
  --name rag-pipeline \
  --type SEARCH \
  --region us-east-1
```

## Step 5: Verify Input Documents

Make sure your documents are in the correct location:
```
C:\Users\6122504\Documents\BU External Research\BU-External-Research\data\RAGInput\
```

The pipeline supports:
- `.docx` files (Word documents)
- `.csv` files (CSV data)
- `.xlsx` files (Excel spreadsheets)

## Step 6: Run the Pipeline

```bash
# Make sure you're in the rag_pipeline directory
cd "C:\Users\6122504\Documents\BU External Research\BU-External-Research\rag_pipeline"

# Run the pipeline
python main.py
```

## What Happens Next?

The pipeline will:

1. **Initialize** (30 seconds)
   - Connect to Claude API
   - Initialize OpenAI embeddings
   - Connect to OpenSearch
   - Create vector index

2. **Load Documents** (1-2 minutes)
   - Read all documents from RAGInput folder
   - Chunk documents (800 tokens, 150 overlap)
   - Extract metadata

3. **Generate Embeddings** (2-5 minutes)
   - Generate 3072-dimensional embeddings
   - Cost: ~$0.50 for 1000 chunks

4. **Index in OpenSearch** (1-2 minutes)
   - Store embeddings and text
   - Configure k-NN search

5. **Run Example Queries** (2-3 minutes)
   - Executes 4 example queries
   - Shows retrieval and generation

6. **Interactive Mode**
   - Ask your own questions
   - Type `quit` to exit

## Example Session

```
================================
RAG PIPELINE INITIALIZATION
Job ID: job-20251104-143022
================================

[14:30:22] 1. Initializing Claude LLM...
[14:30:23] Claude client authenticated successfully

[14:30:23] 2. Initializing OpenAI Embeddings...
[14:30:24] OpenAI Embeddings initialized: text-embedding-3-large

[14:30:24] 3. Initializing OpenSearch Vector Store...
[14:30:25] Connected to OpenSearch Serverless
[14:30:26] Created index: rag_job_job-20251104-143022

[14:30:26] ✓ All components initialized

================================
DOCUMENT LOADING AND INDEXING
================================

[14:30:27] Loading documents from: C:\Users\...\RAGInput

[14:30:28] Loaded 87 chunks from 0b-FULL OUTPUT_Internal Company Intelligence.docx
[14:30:29] Loaded 112 chunks from 0d-FULL OUTPUT_External Industry Intelligence.docx
...

  Total chunks: 456
  Total tokens: 364,800
  Avg tokens/chunk: 800
  Files processed: 7

[14:30:45] Generating embeddings...
  Embedded 456/456 texts
  Embeddings generated: 456
  Embedding cost: $0.0473

[14:30:52] Indexing in OpenSearch...
  Indexed 456/456 documents

[14:30:56] ✓ Indexing complete

================================
INTERACTIVE QUERY MODE
Type your questions (or 'quit' to exit)
================================

Your question: What are the main AI use cases in marketing?

[Multi-stage retrieval happens here...]

ANSWER:
Based on the documents, the main AI use cases in marketing include:

1. Content Generation and Personalization
   - AI-powered content creation for marketing materials
   - Personalized email campaigns
   - Dynamic website content adaptation

2. Customer Insights and Analytics
   - Predictive customer behavior modeling
   - Sentiment analysis of customer feedback
   - Market trend analysis

...

METADATA:
  Sources: 3 files
  Chunks: 12
  Retrieval time: 648ms
  Total time: 4.18s
  Cost: $0.0234
  Total pipeline cost: $0.0707
```

## Troubleshooting

### "ImportError: attempted relative import beyond top-level package"

This has been fixed in the latest version. Make sure you're running the updated `main.py`. If you still see this error:
```bash
# Make sure you're in the rag_pipeline directory
cd "C:\Users\6122504\Documents\BU External Research\BU-External-Research\rag_pipeline"
python main.py
```

### "ModuleNotFoundError: No module named 'rag_pipeline'"

Make sure you're running from the correct directory:
```bash
cd "C:\Users\6122504\Documents\BU External Research\BU-External-Research\rag_pipeline"
python main.py
```

### "Missing required environment variables"

Check your `.env` file exists and contains all required variables:
```bash
type .env
```

### "Failed to connect to OpenSearch"

1. Verify OpenSearch endpoint is correct
2. Check AWS credentials have permissions
3. Verify network access policy allows your IP
4. Check data access policy grants permissions to your IAM user

### "OSError: [WinError 1114] DLL initialization failed"

You need to install Visual C++ Redistributable and restart:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Pipeline is slow

Normal timing:
- Document loading: 1-3 minutes
- Embedding generation: 2-5 minutes (depends on document count)
- Per query: 3-5 seconds

If slower, check:
- Network connection to OpenAI and AWS
- OpenSearch collection is in same region
- Not running other heavy processes

## Cost Estimates

Typical costs per run:
- Initial indexing (500 chunks): ~$0.50
- Query refinement: ~$0.001
- Each query: ~$0.02-0.05
- Total for testing: ~$1-2

## Next Steps

Once the pipeline is running:

1. **Try different queries** to test retrieval quality
2. **Adjust settings** in `config/settings.py`
3. **Monitor costs** in the output
4. **Review job memory** in generated JSON files
5. **Customize workflows** for your use case

## Support

For issues or questions:
1. Check the main [README.md](README.md)
2. Review error messages carefully
3. Check logs in console output
4. Contact the project team

Happy querying! 🚀
