"""
OpenSearch Serverless Vector Store
Implements vector store design from RAG Architecture section 7.2
Uses k-NN with HNSW algorithm and cosine similarity
"""
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3

from ..config.settings import OpenSearchConfig
from ..loaders.document_loader import DocumentChunk


class OpenSearchVectorStore:
    """
    OpenSearch Serverless Vector Store
    Implements architecture specification from section 7.2
    """

    def __init__(
        self,
        config: Optional[OpenSearchConfig] = None,
        job_id: Optional[str] = None
    ):
        """
        Initialize OpenSearch vector store

        Args:
            config: OpenSearch configuration
            job_id: Job ID for index isolation (creates job-specific index)
        """
        self.config = config or OpenSearchConfig()
        self.job_id = job_id or f"job-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.index_name = f"{self.config.index_prefix}_{self.job_id}"

        self.client = None
        self._connect()

    def _connect(self):
        """Establish connection to OpenSearch Serverless"""
        try:
            # Get AWS credentials
            credentials = boto3.Session(
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
                region_name=self.config.region
            ).get_credentials()

            # Create AWSV4 signer
            awsauth = AWSV4SignerAuth(credentials, self.config.region, self.config.service)

            # Initialize OpenSearch client
            self.client = OpenSearch(
                hosts=[{
                    'host': self.config.host,
                    'port': self.config.port
                }],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=30
            )

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Connected to OpenSearch Serverless")

        except Exception as e:
            raise Exception(f"Failed to connect to OpenSearch: {str(e)}")

    def create_index(self, dimension: int = 3072):
        """
        Create index with k-NN configuration from architecture (section 7.2)

        Args:
            dimension: Embedding dimension (3072 for text-embedding-3-large)
        """
        # Index configuration from architecture document
        index_body = {
            "settings": {
                "index": {
                    "knn": self.config.knn_enabled,
                    "knn.algo_param.ef_search": self.config.knn_ef_search,
                    "number_of_shards": self.config.number_of_shards,
                    "number_of_replicas": self.config.number_of_replicas
                }
            },
            "mappings": {
                "properties": {
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": dimension,
                        "method": {
                            "name": "hnsw",
                            "space_type": self.config.knn_space_type,
                            "engine": self.config.knn_engine,
                            "parameters": {
                                "ef_construction": self.config.knn_ef_construction,
                                "m": self.config.knn_m
                            }
                        }
                    },
                    "text": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "metadata": {
                        "properties": {
                            "job_id": {"type": "keyword"},
                            "stage": {"type": "integer"},
                            "section": {"type": "keyword"},
                            "source_file": {"type": "keyword"},
                            "chunk_index": {"type": "integer"},
                            "heading": {"type": "text"},
                            "page_number": {"type": "integer"},
                            "token_count": {"type": "integer"},
                            "created_at": {"type": "date"}
                        }
                    }
                }
            }
        }

        try:
            if not self.client.indices.exists(index=self.index_name):
                self.client.indices.create(index=self.index_name, body=index_body)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Created index: {self.index_name}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Index already exists: {self.index_name}")

        except Exception as e:
            raise Exception(f"Failed to create index: {str(e)}")

    def add_documents(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
        stage: int = 0,
        batch_size: int = 100
    ):
        """
        Add documents with embeddings to vector store

        Args:
            chunks: List of document chunks
            embeddings: List of embedding vectors
            stage: Processing stage number
            batch_size: Batch size for bulk indexing
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Indexing {len(chunks)} documents...")

        # Prepare documents in batches
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]

            # Build bulk request
            bulk_data = []
            for chunk, embedding in zip(batch_chunks, batch_embeddings):
                # Action
                bulk_data.append({
                    "index": {
                        "_index": self.index_name,
                        "_id": str(uuid.uuid4())
                    }
                })

                # Document
                doc = {
                    "text": chunk.text,
                    "embedding": embedding,
                    "metadata": {
                        **chunk.metadata,
                        "job_id": self.job_id,
                        "stage": stage
                    }
                }
                bulk_data.append(doc)

            # Execute bulk request
            try:
                response = self.client.bulk(body=bulk_data)

                if response.get('errors'):
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Warning: Some documents failed to index")

                # Progress
                indexed = min(i + batch_size, len(chunks))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Indexed {indexed}/{len(chunks)} documents")

            except Exception as e:
                raise Exception(f"Bulk indexing failed at batch {i}: {str(e)}")

        # Refresh index
        self.client.indices.refresh(index=self.index_name)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Indexing complete")

    def search(
        self,
        query_embedding: List[float],
        k: int = 50,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        k-NN semantic search

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of search results with text, metadata, and score
        """
        # Build k-NN query
        query = {
            "size": k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": k
                    }
                }
            }
        }

        # Add metadata filters if provided
        if filter_dict:
            query["query"] = {
                "bool": {
                    "must": [
                        {"knn": {"embedding": {"vector": query_embedding, "k": k}}}
                    ],
                    "filter": [
                        {"term": {f"metadata.{key}": value}}
                        for key, value in filter_dict.items()
                    ]
                }
            }

        try:
            response = self.client.search(index=self.index_name, body=query)

            # Parse results
            results = []
            for hit in response['hits']['hits']:
                result = {
                    "id": hit['_id'],
                    "text": hit['_source']['text'],
                    "metadata": hit['_source']['metadata'],
                    "score": hit['_score'],
                    "similarity": hit['_score']  # Cosine similarity for consistency
                }
                results.append(result)

            return results

        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")

    def hybrid_search(
        self,
        query_embedding: List[float],
        query_text: str,
        k: int = 50,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and keyword matching (BM25)
        Implements Reciprocal Rank Fusion from architecture section 7.8

        Args:
            query_embedding: Query embedding vector
            query_text: Query text for keyword search
            k: Number of results
            vector_weight: Weight for vector search (0-1)
            keyword_weight: Weight for keyword search (0-1)

        Returns:
            List of search results ranked by RRF
        """
        # Vector search
        vector_results = self.search(query_embedding, k=k)

        # Keyword search (BM25)
        keyword_query = {
            "size": k,
            "query": {
                "match": {
                    "text": {
                        "query": query_text,
                        "operator": "or"
                    }
                }
            }
        }

        try:
            keyword_response = self.client.search(index=self.index_name, body=keyword_query)
            keyword_results = [
                {
                    "id": hit['_id'],
                    "text": hit['_source']['text'],
                    "metadata": hit['_source']['metadata'],
                    "score": hit['_score']
                }
                for hit in keyword_response['hits']['hits']
            ]

            # Apply Reciprocal Rank Fusion (RRF)
            rrf_constant = 61  # Standard RRF constant
            rrf_scores = {}

            # Score from vector search
            for rank, result in enumerate(vector_results):
                doc_id = result['id']
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 / (rank + rrf_constant))

            # Score from keyword search
            for rank, result in enumerate(keyword_results):
                doc_id = result['id']
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 / (rank + rrf_constant))

            # Combine all unique documents
            all_docs = {r['id']: r for r in vector_results}
            all_docs.update({r['id']: r for r in keyword_results})

            # Sort by RRF score
            ranked_results = sorted(
                all_docs.values(),
                key=lambda d: rrf_scores.get(d['id'], 0),
                reverse=True
            )

            # Add RRF scores
            for result in ranked_results:
                result['rrf_score'] = rrf_scores.get(result['id'], 0)

            return ranked_results[:k]

        except Exception as e:
            raise Exception(f"Hybrid search failed: {str(e)}")

    def delete_index(self):
        """Delete the job-specific index"""
        try:
            if self.client.indices.exists(index=self.index_name):
                self.client.indices.delete(index=self.index_name)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Deleted index: {self.index_name}")
        except Exception as e:
            raise Exception(f"Failed to delete index: {str(e)}")

    def get_document_count(self) -> int:
        """Get total document count in index"""
        try:
            response = self.client.count(index=self.index_name)
            return response['count']
        except Exception as e:
            return 0

    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            stats = self.client.indices.stats(index=self.index_name)
            return {
                "document_count": self.get_document_count(),
                "index_size": stats['indices'][self.index_name]['total']['store']['size_in_bytes'],
                "index_name": self.index_name,
                "job_id": self.job_id
            }
        except Exception as e:
            return {"error": str(e)}


# Convenience function
def create_vector_store(
    config: Optional[OpenSearchConfig] = None,
    job_id: Optional[str] = None
) -> OpenSearchVectorStore:
    """
    Factory function to create vector store

    Args:
        config: Optional OpenSearch configuration
        job_id: Optional job ID

    Returns:
        Initialized OpenSearchVectorStore instance
    """
    store = OpenSearchVectorStore(config, job_id)
    store.create_index()
    return store
