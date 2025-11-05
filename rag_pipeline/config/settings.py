"""
RAG Pipeline Configuration Settings
Based on RAG Architecture Document specifications
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ClaudeConfig:
    """Claude API Configuration for Thomson Reuters"""
    workspace_id: str = "ExternalResei8Dz"
    token_url: str = "https://aiplatform.gcs.int.thomsonreuters.com/v1/anthropic/token"
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class EmbeddingConfig:
    """Embedding Configuration - text-embedding-3-large (Direct OpenAI)"""
    model: str = "text-embedding-3-large"
    dimensions: int = 3072
    api_key: Optional[str] = None  # Will be set from environment

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")


@dataclass
class TROpenAIConfig:
    """Thomson Reuters OpenAI Configuration"""
    workspace_id: str = "Workspace_ID"  # Set your workspace ID
    asset_id: str = "Asset_ID"  # Set your asset ID
    token_url: str = "https://aiplatform.gcs.int.thomsonreuters.com/v1/openai/token"
    base_url: str = "https://eais2-use.int.thomsonreuters.com"
    model_name: str = "gpt-4.1"
    embedding_model: str = "text-embedding-3-large"
    dimensions: int = 3072

    def __post_init__(self):
        # Override from environment if available
        if os.getenv("TR_WORKSPACE_ID"):
            self.workspace_id = os.getenv("TR_WORKSPACE_ID")
        if os.getenv("TR_ASSET_ID"):
            self.asset_id = os.getenv("TR_ASSET_ID")


@dataclass
class ChunkingConfig:
    """Chunking Strategy Configuration"""
    chunk_size: int = 800  # tokens
    chunk_overlap: int = 150  # tokens

    # Metadata preservation
    preserve_metadata: bool = True
    include_section_headers: bool = True
    include_page_numbers: bool = True


@dataclass
class OpenSearchConfig:
    """OpenSearch Serverless Configuration"""
    # Connection settings
    host: Optional[str] = None
    port: int = 443
    region: str = "us-east-1"

    # Authentication
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    service: str = "aoss"  # Amazon OpenSearch Serverless

    # Index settings
    index_prefix: str = "rag_job"

    # k-NN settings (from architecture document)
    knn_enabled: bool = True
    knn_ef_search: int = 512
    knn_ef_construction: int = 512
    knn_m: int = 16
    knn_space_type: str = "cosinesimilarity"
    knn_engine: str = "nmslib"

    # Index configuration
    number_of_shards: int = 2
    number_of_replicas: int = 1

    def __post_init__(self):
        if not self.host:
            self.host = os.getenv("OPENSEARCH_HOST")
        if not self.aws_access_key_id:
            self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        if not self.aws_secret_access_key:
            self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")


@dataclass
class RetrievalConfig:
    """Multi-Stage Retrieval Configuration"""
    # Stage 1: Broad Recall
    stage1_top_k: int = 50

    # Stage 2: Relevance Filtering
    similarity_threshold: float = 0.75  # 75% threshold from architecture

    # Stage 3: Reranking
    stage3_top_k: int = 15
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"

    # Stage 4: Context Assembly
    max_context_tokens: int = 15000
    enable_deduplication: bool = True
    enable_chunk_merging: bool = True
    enable_source_attribution: bool = True


@dataclass
class JobMemoryConfig:
    """Job Memory System Configuration"""
    max_memory_tokens: int = 2000
    enable_compression: bool = True
    compression_ratio: float = 0.5  # Target 50% compression

    # Memory retention
    retain_key_findings: bool = True
    retain_quality_scores: bool = True
    retain_cost_tracking: bool = True


@dataclass
class RAGPipelineConfig:
    """Complete RAG Pipeline Configuration"""
    claude: ClaudeConfig = None
    embedding: EmbeddingConfig = None
    tr_openai: TROpenAIConfig = None  # Thomson Reuters OpenAI
    chunking: ChunkingConfig = None
    opensearch: OpenSearchConfig = None
    retrieval: RetrievalConfig = None
    job_memory: JobMemoryConfig = None

    # Embedding provider selection
    use_tr_openai: bool = True  # True = TR OpenAI, False = Direct OpenAI

    # Data paths
    input_data_path: str = r"C:\Users\6122504\Documents\BU External Research\BU-External-Research\data\RAGInput"

    # Cost tracking
    enable_cost_tracking: bool = True
    budget_limit: float = 200.0  # USD

    # Quality settings
    enable_quality_monitoring: bool = True
    min_quality_score: float = 85.0

    def __post_init__(self):
        if not self.claude:
            self.claude = ClaudeConfig()
        if not self.embedding:
            self.embedding = EmbeddingConfig()
        if not self.tr_openai:
            self.tr_openai = TROpenAIConfig()
        if not self.chunking:
            self.chunking = ChunkingConfig()
        if not self.opensearch:
            self.opensearch = OpenSearchConfig()
        if not self.retrieval:
            self.retrieval = RetrievalConfig()
        if not self.job_memory:
            self.job_memory = JobMemoryConfig()


# Singleton configuration instance
config = RAGPipelineConfig()


def get_config() -> RAGPipelineConfig:
    """Get the global configuration instance"""
    return config


def update_config(**kwargs) -> RAGPipelineConfig:
    """Update configuration with custom values"""
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config
