"""
Thomson Reuters OpenAI Embeddings Wrapper
Uses TR AI Platform authentication for OpenAI embeddings
Supports text-embedding-3-large (3072 dimensions)
"""
import numpy as np
from typing import List, Union, Optional
from datetime import datetime
from openai import AzureOpenAI
import requests
import json

from ..config.settings import TROpenAIConfig


class TROpenAIEmbeddings:
    """
    Thomson Reuters OpenAI Embeddings Wrapper
    Uses TR AI Platform authentication
    Generates 3072-dimensional embeddings with text-embedding-3-large
    """

    def __init__(self, config: Optional[TROpenAIConfig] = None):
        """
        Initialize TR OpenAI embeddings

        Args:
            config: TR OpenAI configuration (uses default if not provided)
        """
        self.config = config or TROpenAIConfig()
        self.client = None
        self.credentials = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Thomson Reuters AI Platform for OpenAI"""
        payload = {
            "workspace_id": self.config.workspace_id,
            "model_name": self.config.model_name
        }

        try:
            resp = requests.post(
                self.config.token_url,
                json=payload
            )
            credentials = json.loads(resp.content)

            if "openai_key" in credentials and "openai_endpoint" in credentials:
                self.credentials = credentials

                # Extract credentials
                openai_api_key = credentials["openai_key"]
                openai_deployment_id = credentials["azure_deployment"]
                openai_api_version = credentials["openai_api_version"]
                token = credentials["token"]
                llm_profile_key = openai_deployment_id.split("/")[0]

                # Build headers
                headers = {
                    "Authorization": f"Bearer {token}",
                    "api-key": openai_api_key,
                    "Content-Type": "application/json",
                    "x-tr-chat-profile-name": "ai-platforms-chatprofile-prod",
                    "x-tr-userid": self.config.workspace_id,
                    "x-tr-llm-profile-key": llm_profile_key,
                    "x-tr-user-sensitivity": "true",
                    "x-tr-sessionid": openai_deployment_id,
                    "x-tr-asset-id": self.config.asset_id,
                    "x-tr-authorization": self.config.base_url
                }

                # Initialize AzureOpenAI client
                self.client = AzureOpenAI(
                    azure_endpoint=self.config.base_url,
                    api_key=openai_api_key,
                    api_version=openai_api_version,
                    azure_deployment=openai_deployment_id,
                    default_headers=headers
                )

                print(f"[{datetime.now().strftime('%H:%M:%S')}] TR OpenAI Embeddings authenticated successfully")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Using model: {self.config.embedding_model}")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Dimensions: {self.config.dimensions}")

            else:
                raise Exception(f"Failed to get OpenAI credentials: {credentials}")

        except Exception as e:
            raise Exception(f"TR OpenAI authentication failed: {str(e)}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            3072-dimensional embedding vector
        """
        if not self.client:
            raise Exception("Client not authenticated. Call _authenticate() first.")

        try:
            response = self.client.embeddings.create(
                model=self.config.embedding_model,
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
            batch_size: Number of texts to embed per API call

        Returns:
            List of 3072-dimensional embedding vectors
        """
        if not self.client:
            raise Exception("Client not authenticated.")

        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = self.client.embeddings.create(
                    model=self.config.embedding_model,
                    input=batch,
                    dimensions=self.config.dimensions
                )

                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                # Progress logging
                if (i + batch_size) % 500 == 0 or (i + batch_size) >= len(texts):
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
        Calculate cosine similarity between two vectors

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
        Check if similarity meets the 75% threshold

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


class CachedTROpenAIEmbeddings(TROpenAIEmbeddings):
    """
    TR OpenAI Embeddings with caching support
    """

    def __init__(self, config: Optional[TROpenAIConfig] = None, cache_size: int = 10000):
        """
        Initialize with caching

        Args:
            config: TR OpenAI configuration
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
def get_tr_embeddings(
    config: Optional[TROpenAIConfig] = None,
    use_cache: bool = True
) -> Union[TROpenAIEmbeddings, CachedTROpenAIEmbeddings]:
    """
    Factory function to create TR embeddings instance

    Args:
        config: Optional TR OpenAI configuration
        use_cache: Whether to use caching (recommended)

    Returns:
        TR Embeddings instance
    """
    if use_cache:
        return CachedTROpenAIEmbeddings(config)
    else:
        return TROpenAIEmbeddings(config)
