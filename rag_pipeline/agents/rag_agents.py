"""
RAG Agents Implementation
Implements multi-stage retrieval funnel from architecture section 7.6
Agents: R-03 (Search), R-04 (Filter), R-05 (Assembly), R-06 (Rerank)
"""
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from sentence_transformers import CrossEncoder

from ..config.settings import RetrievalConfig


@dataclass
class RetrievalResult:
    """
    Structure for retrieval results
    """
    id: str
    text: str
    metadata: Dict[str, Any]
    similarity: float
    rank: Optional[int] = None
    rerank_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata,
            "similarity": self.similarity,
            "rank": self.rank,
            "rerank_score": self.rerank_score
        }


class AgentR03_SemanticSearch:
    """
    Agent R-03: Semantic Search (Stage 1)
    Implements broad recall from architecture section 7.6
    """

    def __init__(self, vector_store, embeddings, config: Optional[RetrievalConfig] = None):
        """
        Initialize semantic search agent

        Args:
            vector_store: OpenSearch vector store instance
            embeddings: Embeddings model instance
            config: Retrieval configuration
        """
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.config = config or RetrievalConfig()

    def search(
        self,
        query: str,
        k: Optional[int] = None,
        use_hybrid: bool = False
    ) -> List[RetrievalResult]:
        """
        Stage 1: Broad Recall - Retrieve top-k candidates

        Args:
            query: Search query
            k: Number of results (default from config)
            use_hybrid: Use hybrid search (vector + keyword)

        Returns:
            List of retrieval results
        """
        k = k or self.config.stage1_top_k

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Agent R-03: Semantic Search")
        print(f"  Query: {query}")
        print(f"  Retrieving top-{k} candidates...")

        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Search
        if use_hybrid:
            results = self.vector_store.hybrid_search(
                query_embedding=query_embedding,
                query_text=query,
                k=k
            )
        else:
            results = self.vector_store.search(
                query_embedding=query_embedding,
                k=k
            )

        # Convert to RetrievalResult objects
        retrieval_results = []
        for result in results:
            retrieval_results.append(RetrievalResult(
                id=result['id'],
                text=result['text'],
                metadata=result['metadata'],
                similarity=result.get('similarity', result.get('score', 0.0))
            ))

        print(f"  Retrieved {len(retrieval_results)} candidates")
        print(f"  Similarity range: {min(r.similarity for r in retrieval_results):.2f} - {max(r.similarity for r in retrieval_results):.2f}")

        return retrieval_results


class AgentR04_RelevanceFiltering:
    """
    Agent R-04: Relevance Filtering (Stage 2)
    Applies 75% similarity threshold from architecture section 7.5
    """

    def __init__(self, config: Optional[RetrievalConfig] = None):
        """
        Initialize relevance filtering agent

        Args:
            config: Retrieval configuration
        """
        self.config = config or RetrievalConfig()

    def filter(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """
        Stage 2: Relevance Filtering - Apply 75% threshold

        Args:
            results: Results from semantic search

        Returns:
            Filtered results meeting threshold
        """
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Agent R-04: Relevance Filtering")
        print(f"  Threshold: {self.config.similarity_threshold * 100}%")
        print(f"  Input: {len(results)} candidates")

        # Filter by threshold
        filtered = [
            r for r in results
            if r.similarity >= self.config.similarity_threshold
        ]

        print(f"  Output: {len(filtered)} results (removed {len(results) - len(filtered)})")

        if filtered:
            print(f"  Similarity range: {min(r.similarity for r in filtered):.2f} - {max(r.similarity for r in filtered):.2f}")

        return filtered


class AgentR06_Reranking:
    """
    Agent R-06: Cross-Encoder Reranking (Stage 3)
    Implements high-precision reranking from architecture section 7.6
    """

    def __init__(self, config: Optional[RetrievalConfig] = None):
        """
        Initialize reranking agent

        Args:
            config: Retrieval configuration
        """
        self.config = config or RetrievalConfig()

        # Load cross-encoder model
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading reranker model: {self.config.reranker_model}")
        self.reranker = CrossEncoder(self.config.reranker_model)

    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Stage 3: Reranking - Use cross-encoder for precise ranking

        Args:
            query: Original query
            results: Filtered results from stage 2
            top_k: Number of top results to return (default from config)

        Returns:
            Reranked results
        """
        top_k = top_k or self.config.stage3_top_k

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Agent R-06: Cross-Encoder Reranking")
        print(f"  Input: {len(results)} candidates")
        print(f"  Reranking to top-{top_k}...")

        if not results:
            return []

        # Prepare pairs for cross-encoder
        pairs = [[query, r.text] for r in results]

        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs)

        # Add scores and sort
        for result, score in zip(results, rerank_scores):
            result.rerank_score = float(score)

        # Sort by rerank score
        reranked = sorted(results, key=lambda r: r.rerank_score, reverse=True)

        # Take top-k
        reranked = reranked[:top_k]

        # Add ranks
        for rank, result in enumerate(reranked, 1):
            result.rank = rank

        print(f"  Output: {len(reranked)} results")
        print(f"  Rerank score range: {min(r.rerank_score for r in reranked):.3f} - {max(r.rerank_score for r in reranked):.3f}")

        return reranked


class AgentR05_ContextAssembly:
    """
    Agent R-05: Context Assembly (Stage 4)
    Implements context assembly algorithm from architecture section 7.6
    """

    def __init__(self, config: Optional[RetrievalConfig] = None):
        """
        Initialize context assembly agent

        Args:
            config: Retrieval configuration
        """
        self.config = config or RetrievalConfig()

    def normalize_text(self, text: str, length: int = 100) -> str:
        """
        Normalize text for deduplication

        Args:
            text: Input text
            length: Signature length

        Returns:
            Normalized text signature
        """
        # Remove extra whitespace and lowercase
        normalized = ' '.join(text.lower().split())
        return normalized[:length]

    def is_adjacent(self, chunk1: RetrievalResult, chunk2: RetrievalResult) -> bool:
        """
        Check if two chunks are adjacent in source document

        Args:
            chunk1: First chunk
            chunk2: Second chunk

        Returns:
            True if chunks are adjacent
        """
        # Check same source file
        if chunk1.metadata.get('source_file') != chunk2.metadata.get('source_file'):
            return False

        # Check chunk indices
        idx1 = chunk1.metadata.get('chunk_index', -1)
        idx2 = chunk2.metadata.get('chunk_index', -1)

        if idx1 == -1 or idx2 == -1:
            return False

        # Adjacent if indices differ by 1
        return abs(idx1 - idx2) == 1

    def assemble_context(self, results: List[RetrievalResult]) -> Dict[str, Any]:
        """
        Stage 4: Context Assembly - Deduplicate, merge, and optimize

        Args:
            results: Reranked results from stage 3

        Returns:
            Assembled context with metadata
        """
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Agent R-05: Context Assembly")
        print(f"  Input: {len(results)} chunks")

        if not results:
            return {
                "context": "",
                "chunks": [],
                "total_tokens": 0,
                "sources": []
            }

        assembled = []
        seen_signatures = set()

        # 1. Deduplication
        for result in results:
            signature = self.normalize_text(result.text)

            if signature in seen_signatures:
                continue

            seen_signatures.add(signature)
            assembled.append(result)

        print(f"  After deduplication: {len(assembled)} chunks")

        # 2. Merge adjacent chunks (if enabled)
        if self.config.enable_chunk_merging:
            merged = []
            i = 0
            while i < len(assembled):
                current = assembled[i]

                # Check if next chunk is adjacent
                if i + 1 < len(assembled) and self.is_adjacent(current, assembled[i + 1]):
                    # Merge
                    next_chunk = assembled[i + 1]
                    current.text = current.text + "\n\n" + next_chunk.text
                    current.metadata["merged"] = True
                    i += 2  # Skip next
                else:
                    i += 1

                merged.append(current)

            assembled = merged
            print(f"  After merging: {len(assembled)} chunks")

        # 3. Sort by source and index
        assembled.sort(
            key=lambda c: (
                c.metadata.get('source_file', ''),
                c.metadata.get('chunk_index', 0)
            )
        )

        # 4. Add source attribution
        if self.config.enable_source_attribution:
            for chunk in assembled:
                source = chunk.metadata.get('source_file', 'Unknown')
                section = chunk.metadata.get('section', '')
                heading = chunk.metadata.get('heading', '')

                attribution = f"[Source: {source}"
                if section and section != "Unknown":
                    attribution += f", Section {section}"
                if heading and heading != "Unknown":
                    attribution += f" - {heading}"
                attribution += "]"

                chunk.metadata['attribution'] = attribution

        # 5. Token optimization
        total_tokens = sum(c.metadata.get('token_count', len(c.text) // 4) for c in assembled)

        if total_tokens > self.config.max_context_tokens:
            # Keep highest-ranked chunks until under budget
            trimmed = []
            current_tokens = 0

            for chunk in assembled:
                chunk_tokens = chunk.metadata.get('token_count', len(chunk.text) // 4)
                if current_tokens + chunk_tokens <= self.config.max_context_tokens:
                    trimmed.append(chunk)
                    current_tokens += chunk_tokens
                else:
                    break

            assembled = trimmed
            total_tokens = current_tokens
            print(f"  After token optimization: {len(assembled)} chunks, {total_tokens} tokens")

        # 6. Build final context
        context_parts = []
        sources = set()

        for chunk in assembled:
            if self.config.enable_source_attribution:
                context_parts.append(f"{chunk.metadata.get('attribution', '')}\n{chunk.text}")
            else:
                context_parts.append(chunk.text)

            sources.add(chunk.metadata.get('source_file', 'Unknown'))

        context = "\n\n---\n\n".join(context_parts)

        print(f"  Final context: {len(assembled)} chunks, {total_tokens} tokens")
        print(f"  Sources: {len(sources)} files")

        return {
            "context": context,
            "chunks": [c.to_dict() for c in assembled],
            "total_tokens": total_tokens,
            "sources": list(sources),
            "num_chunks": len(assembled)
        }


class MultiStageRetriever:
    """
    Complete multi-stage retrieval pipeline
    Orchestrates all 4 stages from architecture section 7.6
    """

    def __init__(
        self,
        vector_store,
        embeddings,
        config: Optional[RetrievalConfig] = None
    ):
        """
        Initialize multi-stage retriever

        Args:
            vector_store: OpenSearch vector store
            embeddings: Embeddings model
            config: Retrieval configuration
        """
        self.config = config or RetrievalConfig()

        # Initialize agents
        self.agent_r03 = AgentR03_SemanticSearch(vector_store, embeddings, config)
        self.agent_r04 = AgentR04_RelevanceFiltering(config)
        self.agent_r06 = AgentR06_Reranking(config)
        self.agent_r05 = AgentR05_ContextAssembly(config)

    def retrieve(
        self,
        query: str,
        use_hybrid: bool = False
    ) -> Dict[str, Any]:
        """
        Execute full multi-stage retrieval pipeline

        Args:
            query: User query
            use_hybrid: Use hybrid search (vector + keyword)

        Returns:
            Assembled context and metadata
        """
        start_time = datetime.now()

        print(f"\n{'='*70}")
        print(f"MULTI-STAGE RETRIEVAL PIPELINE")
        print(f"Query: {query}")
        print(f"{'='*70}")

        # Stage 1: Semantic Search (Broad Recall)
        stage1_results = self.agent_r03.search(query, use_hybrid=use_hybrid)

        # Stage 2: Relevance Filtering (75% threshold)
        stage2_results = self.agent_r04.filter(stage1_results)

        # Stage 3: Reranking (High Precision)
        stage3_results = self.agent_r06.rerank(query, stage2_results)

        # Stage 4: Context Assembly
        assembled = self.agent_r05.assemble_context(stage3_results)

        # Calculate timing
        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        print(f"\n{'='*70}")
        print(f"PIPELINE COMPLETE")
        print(f"  Total time: {elapsed:.0f}ms")
        print(f"  Token savings: {((1 - assembled['total_tokens'] / 150000) * 100):.1f}%")
        print(f"{'='*70}\n")

        # Add timing to result
        assembled['retrieval_time_ms'] = elapsed

        return assembled
