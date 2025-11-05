"""
OpenAI Embeddings Wrapper for text-embedding-3-large
3072-dimensional embeddings for semantic search
"""
import numpy as np
from typing import List, Union, Optional
from datetime import datetime
import openai

from ..config.settings import EmbeddingConfig


class OpenAIEmbeddings:
    """
    Wrapper for OpenAI text-embedding-3-large model
    Generates 3072-dimensional embeddings as specified in architecture
    """

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize OpenAI embeddings

        Args:
            config: Embedding configuration (uses default if not provided)
        """
        self.config = config or EmbeddingConfig()

        if not self.config.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key in config."
            )

        # Set API key
        openai.api_key = self.config.api_key
        self.client = openai.OpenAI(api_key=self.config.api_key)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] OpenAI Embeddings initialized: {self.config.model}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            3072-dimensional embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.config.model,
                input=text,
                dimensions=self.config.dimensions
            )
            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")

    def embed_texts(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches

        Args:
            texts: List of input texts
            batch_size: Number of texts to embed per API call (max 100)

        Returns:
            List of 3072-dimensional embedding vectors
        """
        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = self.client.embeddings.create(
                    model=self.config.model,
                    input=batch,
                    dimensions=self.config.dimensions
                )

                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                # Progress logging
                if (i + batch_size) % 500 == 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Embedded {min(i + batch_size, len(texts))}/{len(texts)} texts")

            except Exception as e:
                raise Exception(f"Batch embedding failed at index {i}: {str(e)}")

        return all_embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query (alias for embed_text)

        Args:
            query: Search query

        Returns:
            3072-dimensional embedding vector
        """
        return self.embed_text(query)

    def calculate_cosine_similarity(
        self,
        vector_a: Union[List[float], np.ndarray],
        vector_b: Union[List[float], np.ndarray]
    ) -> float:
        """
        Calculate cosine similarity between two vectors (as per architecture)

        Args:
            vector_a: First embedding vector (3072-d)
            vector_b: Second embedding vector (3072-d)

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        # Convert to numpy arrays
        a = np.array(vector_a) if not isinstance(vector_a, np.ndarray) else vector_a
        b = np.array(vector_b) if not isinstance(vector_b, np.ndarray) else vector_b

        # Calculate dot product
        dot_product = np.dot(a, b)

        # Calculate magnitudes
        magnitude_a = np.linalg.norm(a)
        magnitude_b = np.linalg.norm(b)

        # Cosine similarity
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        cosine_sim = dot_product / (magnitude_a * magnitude_b)

        return float(cosine_sim)

    def calculate_similarity_percentage(
        self,
        vector_a: Union[List[float], np.ndarray],
        vector_b: Union[List[float], np.ndarray]
    ) -> float:
        """
        Calculate similarity as percentage (0-100) as per architecture spec

        Args:
            vector_a: First embedding vector
            vector_b: Second embedding vector

        Returns:
            Similarity percentage (0.0 to 100.0)
        """
        cosine_sim = self.calculate_cosine_similarity(vector_a, vector_b)
        return cosine_sim * 100

    def meets_threshold(
        self,
        vector_a: Union[List[float], np.ndarray],
        vector_b: Union[List[float], np.ndarray],
        threshold: float = 0.75
    ) -> bool:
        """
        Check if similarity meets the 75% threshold (architecture requirement)

        Args:
            vector_a: First embedding vector
            vector_b: Second embedding vector
            threshold: Similarity threshold (default 0.75 = 75%)

        Returns:
            True if similarity >= threshold
        """
        similarity = self.calculate_cosine_similarity(vector_a, vector_b)
        return similarity >= threshold

    def calculate_cost(self, num_tokens: int) -> float:
        """
        Calculate embedding API cost

        Args:
            num_tokens: Number of tokens to embed

        Returns:
            Cost in USD
        """
        # text-embedding-3-large pricing: $0.13 per 1M tokens
        cost_per_million = 0.13
        return (num_tokens / 1_000_000) * cost_per_million

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4


class EmbeddingCache:
    """
    Simple in-memory cache for embeddings to avoid redundant API calls
    """

    def __init__(self, max_size: int = 10000):
        """
        Initialize embedding cache

        Args:
            max_size: Maximum number of cached embeddings
        """
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        if text in self.cache:
            self.hits += 1
            return self.cache[text]
        self.misses += 1
        return None

    def put(self, text: str, embedding: List[float]):
        """Store embedding in cache"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            first_key = next(iter(self.cache))
            del self.cache[first_key]

        self.cache[text] = embedding

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%"
        }


class CachedOpenAIEmbeddings(OpenAIEmbeddings):
    """
    OpenAI Embeddings with caching support
    """

    def __init__(self, config: Optional[EmbeddingConfig] = None, cache_size: int = 10000):
        """
        Initialize with caching

        Args:
            config: Embedding configuration
            cache_size: Maximum cache size
        """
        super().__init__(config)
        self.cache = EmbeddingCache(max_size=cache_size)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding with caching"""
        # Check cache first
        cached_embedding = self.cache.get(text)
        if cached_embedding is not None:
            return cached_embedding

        # Generate new embedding
        embedding = super().embed_text(text)

        # Store in cache
        self.cache.put(text, embedding)

        return embedding

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return self.cache.get_stats()


# Convenience function
def get_embeddings(
    config: Optional[EmbeddingConfig] = None,
    use_cache: bool = True
) -> Union[OpenAIEmbeddings, CachedOpenAIEmbeddings]:
    """
    Factory function to create embeddings instance

    Args:
        config: Optional embedding configuration
        use_cache: Whether to use caching (recommended)

    Returns:
        Embeddings instance
    """
    if use_cache:
        return CachedOpenAIEmbeddings(config)
    else:
        return OpenAIEmbeddings(config)
