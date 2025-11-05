"""
Centralized RAG Tools
Provides RAG functionality for all agents without cluttering the agents directory
"""
import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add project root to path to import from src/
PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT))

from src.vectorstore import FaissVectorStore
from langchain_community.document_loaders import Docx2txtLoader


class RAGService:
    """Centralized RAG Service for semantic retrieval"""

    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        """Ensure only one RAG Service instance exists (singleton pattern)"""
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, persist_dir: str = None, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize RAG Service (only once due to singleton)"""
        if self._initialized:
            return

        if persist_dir is None:
            stage2_dir = Path(__file__).parent.parent
            persist_dir = str(stage2_dir / "rag_cache")

        self.persist_dir = persist_dir
        self.embedding_model = embedding_model
        self.vector_store = None
        self.is_initialized = False
        self._initialized = True

        print(f"[RAG Tools] Initialized with persist_dir: {persist_dir}")

    def build_vector_store(
        self,
        bu_intelligence_path: str,
        optional_files: Optional[Dict[str, str]] = None,
        force_rebuild: bool = False
    ) -> bool:
        """Build or load FAISS vector store"""
        try:
            # Check if vector store already exists
            if not force_rebuild and os.path.exists(os.path.join(self.persist_dir, "faiss.index")):
                print(f"[RAG Tools] Loading existing vector store from cache")
                self.vector_store = FaissVectorStore(
                    persist_dir=self.persist_dir,
                    embedding_model=self.embedding_model,
                    chunk_size=1000,
                    chunk_overlap=200
                )
                self.vector_store.load()
                self.is_initialized = True
                print(f"[RAG Tools] ✓ Vector store loaded")
                return True

            print(f"[RAG Tools] Building new vector store...")
            documents = []

            # Load BU Intelligence
            if os.path.exists(bu_intelligence_path):
                print(f"[RAG Tools] Loading BU Intelligence: {os.path.basename(bu_intelligence_path)}")
                loader = Docx2txtLoader(bu_intelligence_path)
                bu_docs = loader.load()
                documents.extend(bu_docs)
                print(f"[RAG Tools] ✓ Loaded {len(bu_docs)} sections")
            else:
                print(f"[RAG Tools] ✗ BU Intelligence file not found")
                return False

            # Load optional files
            if optional_files:
                for file_type, file_path in optional_files.items():
                    if file_path and os.path.exists(file_path):
                        try:
                            loader = Docx2txtLoader(file_path)
                            optional_docs = loader.load()
                            documents.extend(optional_docs)
                            print(f"[RAG Tools] ✓ Loaded {len(optional_docs)} sections from {file_type}")
                        except Exception as e:
                            print(f"[RAG Tools] ⚠ Failed to load {file_type}: {e}")

            if not documents:
                print(f"[RAG Tools] ✗ No documents loaded")
                return False

            # Build vector store
            self.vector_store = FaissVectorStore(
                persist_dir=self.persist_dir,
                embedding_model=self.embedding_model,
                chunk_size=1000,
                chunk_overlap=200
            )

            print(f"[RAG Tools] Building vector store from {len(documents)} documents...")
            self.vector_store.build_from_documents(documents)

            self.is_initialized = True
            print(f"[RAG Tools] ✓ Vector store built successfully")
            return True

        except Exception as e:
            print(f"[RAG Tools] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_context(self, query: str, top_k: int = 5) -> str:
        """Get relevant context for a query (unified method for all agents)"""
        if not self.is_initialized or self.vector_store is None:
            return ""

        try:
            results = self.vector_store.query(query, top_k=top_k)

            # Format results
            context_parts = []
            for idx, result in enumerate(results, 1):
                text = result['metadata']['text'] if result['metadata'] else ""
                if text:
                    context_parts.append(text.strip())

            return "\n\n".join(context_parts)

        except Exception as e:
            print(f"[RAG Tools] ✗ Error retrieving context: {e}")
            return ""


# Global RAG service instance
_rag_service = None


def initialize_rag(bu_intelligence_path: str, optional_files: Dict[str, str] = None, force_rebuild: bool = False) -> bool:
    """Initialize global RAG service (call once at startup)"""
    global _rag_service

    _rag_service = RAGService()
    return _rag_service.build_vector_store(bu_intelligence_path, optional_files, force_rebuild)


def get_rag_context_for_use_case(use_case: Dict[str, Any], context_type: str = "enrichment") -> str:
    """
    Get RAG context for a use case

    Args:
        use_case: Use case dictionary
        context_type: "research" (5 chunks) or "enrichment" (8 chunks)

    Returns:
        Relevant context string or empty string if RAG unavailable
    """
    global _rag_service

    if _rag_service is None or not _rag_service.is_initialized:
        return ""

    # Build query from use case
    query = f"{use_case.get('original_name', '')} {use_case.get('original_description', '')}"

    # Determine top_k based on context type
    top_k = 5 if context_type == "research" else 8

    return _rag_service.get_context(query, top_k=top_k)


def is_rag_available() -> bool:
    """Check if RAG service is available and initialized"""
    global _rag_service
    return _rag_service is not None and _rag_service.is_initialized
