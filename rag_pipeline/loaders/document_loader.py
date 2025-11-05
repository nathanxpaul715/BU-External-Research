"""
Multi-Format Document Loader (Agent F-03)
Implements metadata-aware chunking as per RAG Architecture
Supports DOCX, CSV, XLSX with 800 token chunks and 150 token overlap
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import tiktoken

# Document parsers
from docx import Document as DocxDocument
import pandas as pd

from ..config.settings import ChunkingConfig


@dataclass
class DocumentChunk:
    """
    Document chunk with metadata
    Matches architecture specification in section 7.4
    """
    text: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for vector store"""
        return {
            "text": self.text,
            "metadata": self.metadata
        }


class MetadataAwareChunker:
    """
    Agent F-03: Metadata-Aware Chunking
    Implements algorithm from architecture document section 7.4
    """

    def __init__(self, config: Optional[ChunkingConfig] = None):
        """
        Initialize chunker

        Args:
            config: Chunking configuration (uses default if not provided)
        """
        self.config = config or ChunkingConfig()

        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))

    def split_text_by_tokens(
        self,
        text: str,
        chunk_size: int = 800,
        overlap: int = 150
    ) -> List[str]:
        """
        Split text into chunks by token count

        Args:
            text: Input text
            chunk_size: Maximum tokens per chunk
            overlap: Token overlap between chunks

        Returns:
            List of text chunks
        """
        if not text.strip():
            return []

        # Tokenize
        tokens = self.tokenizer.encode(text)

        if len(tokens) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(tokens):
            # Get chunk
            end = start + chunk_size
            chunk_tokens = tokens[start:end]

            # Decode back to text
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)

            # Move start position with overlap
            start = end - overlap

            # Prevent infinite loop
            if start >= len(tokens):
                break

        return chunks

    def is_heading(self, paragraph_text: str) -> bool:
        """
        Detect if paragraph is a heading

        Args:
            paragraph_text: Paragraph text

        Returns:
            True if paragraph appears to be a heading
        """
        text = paragraph_text.strip()

        # Check for numbered headings (1., 1.1, etc.)
        if re.match(r'^\d+\.(\d+\.)*\s+.+', text):
            return True

        # Check for ALL CAPS (common heading style)
        if text.isupper() and len(text) > 3:
            return True

        # Check for short text ending without punctuation (likely heading)
        if len(text) < 100 and not text.endswith(('.', '!', '?')):
            return True

        return False

    def extract_section_number(self, heading_text: str) -> str:
        """
        Extract section number from heading

        Args:
            heading_text: Heading text

        Returns:
            Section number or "Unknown"
        """
        match = re.match(r'^(\d+\.(\d+\.)*)', heading_text.strip())
        if match:
            return match.group(1).rstrip('.')
        return "Unknown"

    def chunk_document(
        self,
        paragraphs: List[Dict[str, Any]],
        source_file: str
    ) -> List[DocumentChunk]:
        """
        Implement metadata-aware chunking algorithm from architecture

        Args:
            paragraphs: List of paragraph dicts with 'text' and optional metadata
            source_file: Source file name

        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        current_section = "Unknown"
        current_heading = "Unknown"

        for para_idx, para in enumerate(paragraphs):
            para_text = para.get('text', '')

            if not para_text.strip():
                continue

            # Detect section headings
            if self.is_heading(para_text):
                current_heading = para_text.strip()
                current_section = self.extract_section_number(para_text)

            # Split text into token-sized chunks
            text_chunks = self.split_text_by_tokens(
                para_text,
                chunk_size=self.config.chunk_size,
                overlap=self.config.chunk_overlap
            )

            # Add metadata to each chunk
            for chunk_idx, chunk_text in enumerate(text_chunks):
                metadata = {
                    "source_file": source_file,
                    "section": current_section if self.config.preserve_metadata else "Unknown",
                    "heading": current_heading if self.config.include_section_headers else "Unknown",
                    "chunk_index": len(chunks),
                    "created_at": datetime.now().isoformat(),
                    "token_count": self.count_tokens(chunk_text)
                }

                # Add page number if available
                if 'page_number' in para and self.config.include_page_numbers:
                    metadata["page_number"] = para['page_number']

                chunk = DocumentChunk(
                    text=chunk_text,
                    metadata=metadata
                )
                chunks.append(chunk)

        return chunks


class DOCXLoader:
    """Load and process DOCX files"""

    def __init__(self, chunker: MetadataAwareChunker):
        self.chunker = chunker

    def load(self, file_path: str) -> List[DocumentChunk]:
        """
        Load DOCX file and extract chunks

        Args:
            file_path: Path to DOCX file

        Returns:
            List of DocumentChunk objects
        """
        try:
            doc = DocxDocument(file_path)
            source_file = os.path.basename(file_path)

            # Extract paragraphs with metadata
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append({
                        'text': para.text,
                        # Note: python-docx doesn't easily provide page numbers
                        # Page number extraction would require more complex parsing
                    })

            # Chunk with metadata
            chunks = self.chunker.chunk_document(paragraphs, source_file)

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded {len(chunks)} chunks from {source_file}")
            return chunks

        except Exception as e:
            raise Exception(f"Failed to load DOCX file {file_path}: {str(e)}")


class CSVLoader:
    """Load and process CSV files"""

    def __init__(self, chunker: MetadataAwareChunker):
        self.chunker = chunker

    def load(self, file_path: str, text_column: Optional[str] = None) -> List[DocumentChunk]:
        """
        Load CSV file and extract chunks

        Args:
            file_path: Path to CSV file
            text_column: Name of column containing main text (auto-detect if None)

        Returns:
            List of DocumentChunk objects
        """
        try:
            df = pd.read_csv(file_path)
            source_file = os.path.basename(file_path)

            # Auto-detect text column if not specified
            if text_column is None:
                # Look for common text column names
                for col in ['description', 'text', 'content', 'summary', 'details']:
                    if col in df.columns.str.lower():
                        text_column = df.columns[df.columns.str.lower() == col][0]
                        break

                # If still None, use first string column with long text
                if text_column is None:
                    for col in df.columns:
                        if df[col].dtype == 'object':
                            avg_length = df[col].str.len().mean()
                            if avg_length > 50:  # Arbitrary threshold
                                text_column = col
                                break

            if text_column is None:
                raise ValueError(f"Could not auto-detect text column in {source_file}")

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Using column '{text_column}' for text content")

            # Convert rows to paragraphs
            paragraphs = []
            for idx, row in df.iterrows():
                # Combine all columns into text
                text_parts = [f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])]
                text = "\n".join(text_parts)

                paragraphs.append({
                    'text': text,
                    'row_index': idx
                })

            # Chunk with metadata
            chunks = self.chunker.chunk_document(paragraphs, source_file)

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded {len(chunks)} chunks from {source_file}")
            return chunks

        except Exception as e:
            raise Exception(f"Failed to load CSV file {file_path}: {str(e)}")


class XLSXLoader:
    """Load and process XLSX files"""

    def __init__(self, chunker: MetadataAwareChunker):
        self.chunker = chunker

    def load(self, file_path: str, sheet_name: Optional[str] = None) -> List[DocumentChunk]:
        """
        Load XLSX file and extract chunks

        Args:
            file_path: Path to XLSX file
            sheet_name: Name of sheet to load (loads all if None)

        Returns:
            List of DocumentChunk objects
        """
        try:
            source_file = os.path.basename(file_path)

            # Load sheet(s)
            if sheet_name:
                df_dict = {sheet_name: pd.read_excel(file_path, sheet_name=sheet_name)}
            else:
                df_dict = pd.read_excel(file_path, sheet_name=None)

            all_chunks = []

            for sheet, df in df_dict.items():
                # Convert rows to paragraphs
                paragraphs = []
                for idx, row in df.iterrows():
                    # Combine all columns into text
                    text_parts = [f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])]
                    text = f"[Sheet: {sheet}]\n" + "\n".join(text_parts)

                    paragraphs.append({
                        'text': text,
                        'sheet': sheet,
                        'row_index': idx
                    })

                # Chunk with metadata
                chunks = self.chunker.chunk_document(paragraphs, f"{source_file}:{sheet}")
                all_chunks.extend(chunks)

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded {len(all_chunks)} chunks from {source_file}")
            return all_chunks

        except Exception as e:
            raise Exception(f"Failed to load XLSX file {file_path}: {str(e)}")


class MultiFormatDocumentLoader:
    """
    Unified document loader for multiple formats
    Agent F-03 implementation
    """

    def __init__(self, config: Optional[ChunkingConfig] = None):
        """
        Initialize document loader

        Args:
            config: Chunking configuration
        """
        self.config = config or ChunkingConfig()
        self.chunker = MetadataAwareChunker(self.config)

        # Initialize format-specific loaders
        self.docx_loader = DOCXLoader(self.chunker)
        self.csv_loader = CSVLoader(self.chunker)
        self.xlsx_loader = XLSXLoader(self.chunker)

    def load_document(self, file_path: str) -> List[DocumentChunk]:
        """
        Load a single document

        Args:
            file_path: Path to document

        Returns:
            List of DocumentChunk objects
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.docx':
            return self.docx_loader.load(file_path)
        elif file_ext == '.csv':
            return self.csv_loader.load(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return self.xlsx_loader.load(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def load_directory(self, directory_path: str) -> List[DocumentChunk]:
        """
        Load all supported documents from directory

        Args:
            directory_path: Path to directory

        Returns:
            List of DocumentChunk objects from all files
        """
        supported_extensions = ['.docx', '.csv', '.xlsx', '.xls']
        all_chunks = []

        directory = Path(directory_path)

        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    chunks = self.load_document(str(file_path))
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Warning: Failed to load {file_path.name}: {str(e)}")

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Total: Loaded {len(all_chunks)} chunks from {directory_path}")
        return all_chunks

    def get_statistics(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Get statistics about loaded chunks

        Args:
            chunks: List of document chunks

        Returns:
            Statistics dictionary
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_tokens": 0,
                "avg_tokens_per_chunk": 0,
                "files": []
            }

        total_tokens = sum(c.metadata.get('token_count', 0) for c in chunks)
        files = list(set(c.metadata.get('source_file', 'Unknown') for c in chunks))

        return {
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "avg_tokens_per_chunk": total_tokens // len(chunks) if chunks else 0,
            "files": files,
            "num_files": len(files)
        }


# Convenience function
def load_documents(
    path: str,
    config: Optional[ChunkingConfig] = None
) -> List[DocumentChunk]:
    """
    Load documents from file or directory

    Args:
        path: Path to file or directory
        config: Optional chunking configuration

    Returns:
        List of DocumentChunk objects
    """
    loader = MultiFormatDocumentLoader(config)

    if Path(path).is_dir():
        return loader.load_directory(path)
    else:
        return loader.load_document(path)
