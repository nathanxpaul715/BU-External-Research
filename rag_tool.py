"""
RAG Tool for Agent Integration
This module provides a tool interface for agents to access the TR External Research RAG system.
"""

import os
from typing import Dict, List, Any, Optional
from src.search import RAGSearch


class RAGTool:
    """
    A tool that provides agents with access to the TR External Research knowledge base
    through a FAISS-powered RAG system with Claude 4.5 Sonnet.
    """

    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_model: str = "claude-sonnet-4-5-20250929",
        workspace_id: str = "ExternalResei8Dz"
    ):
        """
        Initialize the RAG tool.

        Args:
            persist_dir: Directory where FAISS index is stored
            embedding_model: Model used for embeddings
            llm_model: Claude model for summarization
            workspace_id: TR workspace ID for authentication
        """
        self.rag_search = RAGSearch(
            persist_dir=persist_dir,
            embedding_model=embedding_model,
            llm_model=llm_model,
            workspace_id=workspace_id
        )
        print(f"[INFO] RAG Tool initialized successfully")

    def search_knowledge_base(
        self,
        query: str,
        top_k: int = 5,
        summarize: bool = True
    ) -> str:
        """
        Search the TR External Research knowledge base and optionally summarize results.

        Args:
            query: The search query
            top_k: Number of top results to retrieve (default: 5)
            summarize: Whether to summarize results using Claude (default: True)

        Returns:
            If summarize=True: AI-generated summary of relevant documents
            If summarize=False: Raw text from top matching documents
        """
        try:
            if summarize:
                # Get AI-powered summary using Claude
                return self.rag_search.search_and_summarize(query, top_k=top_k)
            else:
                # Return raw search results
                results = self.rag_search.vectorstore.query(query, top_k=top_k)
                texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
                return "\n\n---\n\n".join(texts) if texts else "No relevant documents found."
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"

    def get_relevant_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Get relevant document chunks without summarization.
        Useful when agents need raw context for their own processing.

        Args:
            query: The search query
            top_k: Number of top results to retrieve (default: 3)

        Returns:
            List of dictionaries containing document chunks and metadata
        """
        try:
            results = self.rag_search.vectorstore.query(query, top_k=top_k)
            return [
                {
                    "text": r["metadata"].get("text", ""),
                    "distance": float(r["distance"]),
                    "index": int(r["index"])
                }
                for r in results if r["metadata"]
            ]
        except Exception as e:
            print(f"[ERROR] Failed to get relevant context: {e}")
            return []


# Singleton instance for easy access
_rag_tool_instance = None

def get_rag_tool() -> RAGTool:
    """
    Get or create a singleton instance of the RAG tool.
    This ensures only one RAG search instance is created.
    """
    global _rag_tool_instance
    if _rag_tool_instance is None:
        _rag_tool_instance = RAGTool()
    return _rag_tool_instance


# Simple function interface for agents
def search_tr_knowledge_base(query: str, top_k: int = 5, summarize: bool = True) -> str:
    """
    Search the TR External Research knowledge base.

    This is the main function that agents should use to access the RAG system.

    Args:
        query: Your search query about TR External Research
        top_k: Number of relevant documents to consider (default: 5)
        summarize: Whether to get an AI summary (True) or raw text (False)

    Returns:
        Either an AI-generated summary or raw document excerpts

    Example:
        >>> search_tr_knowledge_base("What are the gap areas in TR's External Research?")
        "Based on the documents, the main gap areas include..."
    """
    tool = get_rag_tool()
    return tool.search_knowledge_base(query, top_k=top_k, summarize=summarize)


# Tool definition for Anthropic Claude API (function calling)
ANTHROPIC_TOOL_DEFINITION = {
    "name": "search_tr_knowledge_base",
    "description": "Search the Thomson Reuters External Research knowledge base to find information about research offerings, capabilities, gap areas, and strategic initiatives. This tool uses a vector database (FAISS) with Claude 4.5 Sonnet to provide accurate, context-aware answers about TR's External Research.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query. Be specific about what information you're looking for (e.g., 'gap areas in TR research', 'current research capabilities', 'strategic initiatives')"
            },
            "top_k": {
                "type": "integer",
                "description": "Number of relevant documents to retrieve. Default is 5. Increase for broader context.",
                "default": 5
            },
            "summarize": {
                "type": "boolean",
                "description": "Whether to return an AI summary (true) or raw document text (false). Default is true.",
                "default": True
            }
        },
        "required": ["query"]
    }
}


# Tool definition for LangChain
def get_langchain_tool():
    """
    Get a LangChain-compatible tool definition.

    Usage with LangChain:
        from langchain.agents import Tool
        rag_tool = get_langchain_tool()
        # Add to your agent's tools list
    """
    try:
        from langchain.tools import Tool

        return Tool(
            name="search_tr_knowledge_base",
            func=search_tr_knowledge_base,
            description=(
                "Search the Thomson Reuters External Research knowledge base. "
                "Use this to find information about research offerings, capabilities, "
                "gap areas, and strategic initiatives. Input should be a search query string."
            )
        )
    except ImportError:
        print("[WARNING] LangChain not installed. Install with: pip install langchain")
        return None


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("RAG Tool Test")
    print("=" * 80)

    # Test 1: Basic search with summary
    print("\n[TEST 1] Search with summary:")
    query1 = "What are the gap areas in TR's External Research?"
    result1 = search_tr_knowledge_base(query1, top_k=3)
    print(f"Query: {query1}")
    print(f"Result: {result1}\n")

    # Test 2: Get raw context
    print("\n[TEST 2] Get relevant context (no summary):")
    query2 = "What research capabilities does TR have?"
    result2 = search_tr_knowledge_base(query2, top_k=3, summarize=False)
    print(f"Query: {query2}")
    print(f"Result (first 500 chars): {result2[:500]}...\n")

    # Test 3: Using the tool class directly
    print("\n[TEST 3] Using RAGTool class directly:")
    tool = get_rag_tool()
    context = tool.get_relevant_context("strategic initiatives", top_k=2)
    print(f"Retrieved {len(context)} relevant chunks")
    for i, chunk in enumerate(context, 1):
        print(f"  Chunk {i}: {chunk['text'][:100]}... (distance: {chunk['distance']:.4f})")

    print("\n" + "=" * 80)
    print("Tool definition for Anthropic Claude API:")
    print("=" * 80)
    import json
    print(json.dumps(ANTHROPIC_TOOL_DEFINITION, indent=2))
