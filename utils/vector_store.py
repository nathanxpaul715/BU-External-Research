"""
Vector Store Setup for RAG System
Handles embeddings and vector storage using FAISS
"""
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import os


class VectorStoreManager:
    """Manages vector store for document embeddings"""

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        persist_directory: Optional[str] = None
    ):
        """
        Initialize vector store manager

        Args:
            embedding_model: HuggingFace model for embeddings
            persist_directory: Directory to save/load vector store
        """
        self.embedding_model = embedding_model
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store = None

    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        Create a new vector store from documents

        Args:
            documents: List of Document objects to embed

        Returns:
            FAISS vector store
        """
        if not documents:
            raise ValueError("No documents provided to create vector store")

        print(f"Creating vector store with {len(documents)} documents...")
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )

        if self.persist_directory:
            self.save_vector_store()

        return self.vector_store

    def save_vector_store(self):
        """Save vector store to disk"""
        if self.vector_store is None:
            raise ValueError("No vector store to save")

        if not self.persist_directory:
            raise ValueError("No persist directory specified")

        os.makedirs(self.persist_directory, exist_ok=True)
        self.vector_store.save_local(self.persist_directory)
        print(f"Vector store saved to {self.persist_directory}")

    def load_vector_store(self) -> FAISS:
        """Load vector store from disk"""
        if not self.persist_directory:
            raise ValueError("No persist directory specified")

        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(f"Vector store not found at {self.persist_directory}")

        self.vector_store = FAISS.load_local(
            self.persist_directory,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        print(f"Vector store loaded from {self.persist_directory}")
        return self.vector_store

    def add_documents(self, documents: List[Document]):
        """Add new documents to existing vector store"""
        if self.vector_store is None:
            raise ValueError("No vector store initialized. Create one first.")

        self.vector_store.add_documents(documents)

        if self.persist_directory:
            self.save_vector_store()

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """
        Search for similar documents

        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score (optional)

        Returns:
            List of relevant documents
        """
        if self.vector_store is None:
            raise ValueError("No vector store initialized")

        if score_threshold:
            docs = self.vector_store.similarity_search_with_score(query, k=k)
            return [doc for doc, score in docs if score >= score_threshold]
        else:
            return self.vector_store.similarity_search(query, k=k)

    def get_retriever(self, k: int = 4):
        """Get a retriever interface for the vector store"""
        if self.vector_store is None:
            raise ValueError("No vector store initialized")

        return self.vector_store.as_retriever(
            search_kwargs={"k": k}
        )
