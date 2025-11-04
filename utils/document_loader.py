"""
Document Loader Utility for Multiple File Types
Supports: PDF, Excel (.xlsx, .xls), Word Documents (.docx), CSV
"""
import os
from typing import List, Dict
from pathlib import Path

# Document loaders from langchain
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredExcelLoader,
    Docx2txtLoader,
    CSVLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class MultiFormatDocumentLoader:
    """Loads and processes documents from multiple file formats"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document loader

        Args:
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def load_pdf(self, file_path: str) -> List[Document]:
        """Load and split PDF documents"""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def load_excel(self, file_path: str) -> List[Document]:
        """Load and split Excel documents"""
        loader = UnstructuredExcelLoader(file_path, mode="elements")
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def load_docx(self, file_path: str) -> List[Document]:
        """Load and split Word documents"""
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def load_csv(self, file_path: str) -> List[Document]:
        """Load and split CSV documents"""
        loader = CSVLoader(file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a document based on its file extension

        Args:
            file_path: Path to the document

        Returns:
            List of Document objects with chunked text
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = file_path.suffix.lower()

        try:
            if extension == '.pdf':
                return self.load_pdf(str(file_path))
            elif extension in ['.xlsx', '.xls']:
                return self.load_excel(str(file_path))
            elif extension == '.docx':
                return self.load_docx(str(file_path))
            elif extension == '.csv':
                return self.load_csv(str(file_path))
            else:
                raise ValueError(f"Unsupported file format: {extension}")
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            return []

    def load_directory(self, directory_path: str) -> List[Document]:
        """
        Load all supported documents from a directory

        Args:
            directory_path: Path to directory containing documents

        Returns:
            List of all loaded and chunked documents
        """
        directory = Path(directory_path)
        all_documents = []

        supported_extensions = ['.pdf', '.xlsx', '.xls', '.docx', '.csv']

        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                print(f"Loading: {file_path.name}")
                docs = self.load_document(str(file_path))
                all_documents.extend(docs)
                print(f"  Loaded {len(docs)} chunks from {file_path.name}")

        return all_documents

    def get_document_stats(self, documents: List[Document]) -> Dict:
        """Get statistics about loaded documents"""
        total_chars = sum(len(doc.page_content) for doc in documents)

        return {
            "total_documents": len(documents),
            "total_characters": total_chars,
            "avg_chunk_size": total_chars // len(documents) if documents else 0,
        }