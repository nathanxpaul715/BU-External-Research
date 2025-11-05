# RAG Tool Usage Guide

## Overview

The RAG (Retrieval-Augmented Generation) Tool provides agents with access to the Thomson Reuters External Research knowledge base through a FAISS-powered vector store and Claude 4.5 Sonnet for intelligent summarization.

## Architecture

```
User Query → Agent → RAG Tool → FAISS Vector Store → Claude 4.5 → Response
                         ↓
                  [TR External Research
                   Knowledge Base]
```

### Components

1. **FAISS Vector Store** (`vectorstore.py`): Stores document embeddings for fast similarity search
2. **Embedding Pipeline** (`embedding.py`): Chunks and embeds documents using Sentence Transformers
3. **Document Loader** (`data_loader.py`): Loads various document formats (PDF, DOCX, TXT, etc.)
4. **RAG Search** (`search.py`): Core RAG logic with Claude integration
5. **RAG Tool** (`rag_tool.py`): Agent-friendly interface

## Installation

```bash
# Navigate to project directory
cd "C:\Users\6122504\Documents\BU External Research\BU-External-Research"

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Simple Function Call

```python
from src.rag_tool import search_tr_knowledge_base

# Search and get AI summary
result = search_tr_knowledge_base(
    query="What are the gap areas in TR's External Research?",
    top_k=5,
    summarize=True
)
print(result)
```

### 2. Using the Tool Class

```python
from src.rag_tool import RAGTool

# Initialize tool
tool = RAGTool()

# Get summarized response
summary = tool.search_knowledge_base(
    query="What are TR's research capabilities?",
    top_k=5,
    summarize=True
)

# Get raw context chunks
context = tool.get_relevant_context(
    query="strategic initiatives",
    top_k=3
)
```

### 3. Singleton Pattern (Recommended for Agents)

```python
from src.rag_tool import get_rag_tool

# Get singleton instance (creates only once)
tool = get_rag_tool()
result = tool.search_knowledge_base("your query here")
```

## Integration with Agent Frameworks

### Anthropic Claude API (Function Calling)

```python
import anthropic
from src.rag_tool import search_tr_knowledge_base, ANTHROPIC_TOOL_DEFINITION

client = anthropic.Anthropic(api_key="your_api_key")

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    tools=[ANTHROPIC_TOOL_DEFINITION],  # Add RAG tool
    messages=[
        {"role": "user", "content": "What are TR's research gaps?"}
    ]
)

# Handle tool calls
if message.stop_reason == "tool_use":
    tool_use = message.content[0]
    result = search_tr_knowledge_base(**tool_use.input)
    # Send result back to Claude...
```

### LangChain Integration

```python
from src.rag_tool import get_langchain_tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic

# Get the tool
rag_tool = get_langchain_tool()

# Create agent with the tool
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")
tools = [rag_tool]
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Use the agent
result = agent_executor.invoke({"input": "What are TR's research gaps?"})
```

### Custom Agent

```python
from src.rag_tool import get_rag_tool

class MyAgent:
    def __init__(self):
        self.rag = get_rag_tool()

    def answer_question(self, question: str):
        # Get context from RAG
        context = self.rag.get_relevant_context(question, top_k=3)

        # Process with your agent logic
        # ...

        return answer
```

## API Reference

### `search_tr_knowledge_base(query, top_k=5, summarize=True)`

Main function interface for searching the knowledge base.

**Parameters:**
- `query` (str): Search query about TR External Research
- `top_k` (int): Number of relevant documents to consider (default: 5)
- `summarize` (bool): Whether to get AI summary or raw text (default: True)

**Returns:**
- `str`: AI-generated summary or raw document excerpts

**Example:**
```python
result = search_tr_knowledge_base(
    "What are the main research capabilities?",
    top_k=3,
    summarize=True
)
```

### `RAGTool` Class

#### `__init__(persist_dir, embedding_model, llm_model, workspace_id)`

Initialize the RAG tool.

**Parameters:**
- `persist_dir` (str): Directory where FAISS index is stored (default: "faiss_store")
- `embedding_model` (str): Model for embeddings (default: "all-MiniLM-L6-v2")
- `llm_model` (str): Claude model (default: "claude-sonnet-4-5-20250929")
- `workspace_id` (str): TR workspace ID (default: "ExternalResei8Dz")

#### `search_knowledge_base(query, top_k, summarize)`

Search and optionally summarize results.

#### `get_relevant_context(query, top_k)`

Get raw document chunks without summarization.

**Returns:**
- `List[Dict]`: List of dictionaries with 'text', 'distance', and 'index' keys

**Example:**
```python
tool = RAGTool()
chunks = tool.get_relevant_context("research gaps", top_k=3)

for chunk in chunks:
    print(f"Distance: {chunk['distance']:.4f}")
    print(f"Text: {chunk['text'][:200]}...")
```

## Tool Definitions

### Anthropic Claude Function Definition

Use `ANTHROPIC_TOOL_DEFINITION` for Claude function calling:

```python
from src.rag_tool import ANTHROPIC_TOOL_DEFINITION

tools = [ANTHROPIC_TOOL_DEFINITION]
```

Schema:
```json
{
  "name": "search_tr_knowledge_base",
  "description": "Search the Thomson Reuters External Research knowledge base...",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "top_k": {"type": "integer", "default": 5},
      "summarize": {"type": "boolean", "default": true}
    },
    "required": ["query"]
  }
}
```

## Examples

See `examples/agent_with_rag_tool.py` for complete examples:

1. **Anthropic Claude Agent**: Function calling with Claude
2. **Simple Usage**: Direct function calls
3. **LangChain Agent**: Integration with LangChain
4. **Custom Agent**: Building your own agent

Run examples:
```bash
cd "C:\Users\6122504\Documents\BU External Research\BU-External-Research"
python examples/agent_with_rag_tool.py
```

## Configuration

### Environment Variables

Create a `.env` file if needed:
```bash
# Optional: Override default settings
FAISS_PERSIST_DIR=faiss_store
EMBEDDING_MODEL=all-MiniLM-L6-v2
TR_WORKSPACE_ID=ExternalResei8Dz
```

### Custom Configuration

```python
tool = RAGTool(
    persist_dir="custom_faiss_store",
    embedding_model="all-mpnet-base-v2",  # More accurate, slower
    llm_model="claude-sonnet-4-5-20250929",
    workspace_id="your_workspace_id"
)
```

## Best Practices

1. **Use Singleton Pattern**: Use `get_rag_tool()` to avoid loading the model multiple times
2. **Adjust top_k**: Use 3-5 for focused answers, 5-10 for comprehensive context
3. **Raw vs Summary**: Use `summarize=False` when you need exact quotes or want to process text yourself
4. **Error Handling**: Always wrap RAG calls in try-except blocks
5. **Query Quality**: Be specific in queries for better results

## Troubleshooting

### "No relevant documents found"

- Check if FAISS index exists in `persist_dir`
- Verify documents were loaded and indexed
- Try different query phrasing

### API Key Errors

- Ensure you're on TR network
- Verify workspace_id is correct
- Check TR authentication endpoint is accessible

### Memory Issues

- Reduce `top_k` value
- Use `summarize=True` to get condensed responses
- Consider batch processing for multiple queries

## Advanced Usage

### Multi-Agent System

```python
from src.rag_tool import get_rag_tool

class ResearchAgent:
    def __init__(self):
        self.rag = get_rag_tool()

    def research(self, topic):
        return self.rag.search_knowledge_base(topic, top_k=5)

class AnalysisAgent:
    def __init__(self):
        self.rag = get_rag_tool()

    def analyze(self, topic):
        # Get raw context for analysis
        context = self.rag.get_relevant_context(topic, top_k=3)
        # Perform custom analysis
        return analysis_result

# Both agents share the same RAG instance
research_agent = ResearchAgent()
analysis_agent = AnalysisAgent()
```

### Streaming Responses

For large documents, consider implementing streaming:

```python
def stream_rag_response(query, chunk_size=3):
    tool = get_rag_tool()

    # Get all relevant chunks
    all_chunks = tool.get_relevant_context(query, top_k=10)

    # Stream in batches
    for i in range(0, len(all_chunks), chunk_size):
        batch = all_chunks[i:i+chunk_size]
        yield "\n\n".join([c['text'] for c in batch])
```

## Support

For issues or questions:
1. Check this guide
2. Review examples in `examples/agent_with_rag_tool.py`
3. Check source code comments in `src/rag_tool.py`

## License

Internal TR use only.
