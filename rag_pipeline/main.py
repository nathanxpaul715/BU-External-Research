"""
Main Execution Script for RAG Pipeline
Orchestrates document loading, indexing, and query processing
Based on RAG Architecture Document specifications
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to enable package imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from rag_pipeline.config.settings import RAGPipelineConfig, get_config
from rag_pipeline.llm.claude_wrapper import ClaudeLLM
from rag_pipeline.embeddings.openai_embeddings import CachedOpenAIEmbeddings
from rag_pipeline.embeddings.tr_openai_embeddings import CachedTROpenAIEmbeddings
from rag_pipeline.loaders.document_loader import MultiFormatDocumentLoader
from rag_pipeline.vectorstore.opensearch_store import OpenSearchVectorStore
from rag_pipeline.agents.rag_agents import MultiStageRetriever
from rag_pipeline.memory.job_memory import create_job_memory
from rag_pipeline.workflows.agentic_rag import SimpleRAGWorkflow


class RAGPipeline:
    """
    Complete RAG Pipeline Orchestrator
    Manages end-to-end workflow from document loading to query answering
    """

    def __init__(self, config: RAGPipelineConfig = None):
        """
        Initialize RAG pipeline

        Args:
            config: Pipeline configuration
        """
        self.config = config or get_config()

        # Components (initialized in setup)
        self.llm = None
        self.embeddings = None
        self.vector_store = None
        self.retriever = None
        self.workflow = None
        self.job_memory = None

        # Job tracking
        self.job_id = f"job-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.total_cost = 0

    def setup(self):
        """Initialize all pipeline components"""
        print(f"\n{'='*70}")
        print(f"RAG PIPELINE INITIALIZATION")
        print(f"Job ID: {self.job_id}")
        print(f"{'='*70}\n")

        # 1. Initialize Claude LLM
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 1. Initializing Claude LLM...")
        self.llm = ClaudeLLM(self.config.claude)

        # 2. Initialize Embeddings
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 2. Initializing Embeddings...")
        if self.config.use_tr_openai:
            print(f"   Using Thomson Reuters OpenAI embeddings")
            self.embeddings = CachedTROpenAIEmbeddings(self.config.tr_openai)
        else:
            print(f"   Using Direct OpenAI embeddings")
            self.embeddings = CachedOpenAIEmbeddings(self.config.embedding)

        # 3. Initialize Vector Store
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 3. Initializing OpenSearch Vector Store...")
        self.vector_store = OpenSearchVectorStore(
            config=self.config.opensearch,
            job_id=self.job_id
        )
        self.vector_store.create_index(dimension=self.config.embedding.dimensions)

        # 4. Initialize Job Memory
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 4. Initializing Job Memory...")
        self.job_memory = create_job_memory(
            job_id=self.job_id,
            config=self.config.job_memory
        )

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✓ All components initialized\n")

    def load_and_index_documents(self, input_path: str = None):
        """
        Load documents and index them in vector store

        Args:
            input_path: Path to documents (uses config default if None)
        """
        input_path = input_path or self.config.input_data_path

        print(f"\n{'='*70}")
        print(f"DOCUMENT LOADING AND INDEXING")
        print(f"{'='*70}\n")

        # 1. Load documents
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading documents from: {input_path}")
        loader = MultiFormatDocumentLoader(self.config.chunking)

        if Path(input_path).is_dir():
            chunks = loader.load_directory(input_path)
        else:
            chunks = loader.load_document(input_path)

        # Get statistics
        stats = loader.get_statistics(chunks)
        print(f"\n  Total chunks: {stats['total_chunks']}")
        print(f"  Total tokens: {stats['total_tokens']:,}")
        print(f"  Avg tokens/chunk: {stats['avg_tokens_per_chunk']}")
        print(f"  Files processed: {stats['num_files']}")

        if not chunks:
            raise Exception("No documents loaded. Check your input path.")

        # 2. Generate embeddings
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Generating embeddings...")
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embeddings.embed_texts(texts, batch_size=100)

        # Calculate embedding cost
        total_tokens = sum(self.embeddings.estimate_tokens(text) for text in texts)
        embedding_cost = self.embeddings.calculate_cost(total_tokens)
        self.total_cost += embedding_cost
        print(f"  Embeddings generated: {len(embeddings)}")
        print(f"  Embedding cost: ${embedding_cost:.4f}")

        # 3. Index in vector store
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Indexing in OpenSearch...")
        self.vector_store.add_documents(
            chunks=chunks,
            embeddings=embeddings,
            stage=0,
            batch_size=100
        )

        # Update job memory
        self.job_memory.complete_stage(
            stage=0,
            key_findings=[
                f"Indexed {len(chunks)} chunks from {stats['num_files']} files",
                f"Total tokens: {stats['total_tokens']:,}",
                f"Files: {', '.join(stats['files'][:3])}" + ("..." if len(stats['files']) > 3 else "")
            ],
            coverage={
                "chunks_indexed": len(chunks),
                "files_processed": stats['num_files']
            },
            quality_score=95.0,
            cost=embedding_cost
        )

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✓ Indexing complete\n")

        # Show index stats
        index_stats = self.vector_store.get_index_stats()
        print(f"  Index name: {index_stats['index_name']}")
        print(f"  Document count: {index_stats['document_count']}")

    def initialize_retrieval(self):
        """Initialize retriever and workflow"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Initializing retrieval pipeline...")

        # Initialize multi-stage retriever
        self.retriever = MultiStageRetriever(
            vector_store=self.vector_store,
            embeddings=self.embeddings,
            config=self.config.retrieval
        )

        # Initialize workflow
        self.workflow = SimpleRAGWorkflow(
            llm=self.llm,
            retriever=self.retriever,
            job_memory=self.job_memory,
            config=self.config
        )

        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Retrieval pipeline ready\n")

    def query(self, question: str, refine_query: bool = True) -> dict:
        """
        Execute RAG query

        Args:
            question: User question
            refine_query: Whether to refine query before retrieval

        Returns:
            Query result dictionary
        """
        if not self.workflow:
            raise Exception("Workflow not initialized. Call initialize_retrieval() first.")

        result = self.workflow.query(question, refine_query=refine_query)

        # Update cost tracking
        self.total_cost += result.get('cost', 0)

        # Update job memory
        self.job_memory.update_current_stage(
            stage=1,
            status="query_processed",
            queries_processed=self.job_memory.memory.current_stage.get('queries_processed', 0) + 1
        )

        return result

    def run_interactive_mode(self):
        """Run interactive query mode"""
        print(f"\n{'='*70}")
        print(f"INTERACTIVE QUERY MODE")
        print(f"Type your questions (or 'quit' to exit)")
        print(f"{'='*70}\n")

        while True:
            try:
                question = input("\nYour question: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nExiting...")
                    break

                if not question:
                    continue

                # Execute query
                result = self.query(question)

                # Display result
                print(f"\n{'='*70}")
                print(f"ANSWER:")
                print(f"{'='*70}")
                print(result['answer'])
                print(f"\n{'='*70}")
                print(f"METADATA:")
                print(f"  Sources: {len(result['sources'])} files")
                print(f"  Chunks: {result['num_chunks']}")
                print(f"  Retrieval time: {result['retrieval_time_ms']:.0f}ms")
                print(f"  Total time: {result['total_time_s']:.2f}s")
                print(f"  Cost: ${result['cost']:.4f}")
                print(f"  Total pipeline cost: ${self.total_cost:.4f}")
                print(f"{'='*70}")

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError processing query: {str(e)}")

    def run_example_queries(self):
        """Run example queries from architecture document"""
        example_queries = [
            "What are the main AI use cases mentioned in the documents?",
            "What is the current state of AI implementation in the marketing function?",
            "What gaps exist between internal capabilities and external best practices?",
            "What are the key activities and roles in the marketing function?"
        ]

        print(f"\n{'='*70}")
        print(f"RUNNING EXAMPLE QUERIES")
        print(f"{'='*70}\n")

        results = []

        for i, question in enumerate(example_queries, 1):
            print(f"\n[Query {i}/{len(example_queries)}]")

            result = self.query(question)

            print(f"\nQuestion: {question}")
            print(f"\nAnswer:\n{result['answer'][:500]}...")  # First 500 chars
            print(f"\nSources: {', '.join(result['sources'])}")
            print(f"Cost: ${result['cost']:.4f}")
            print(f"\n{'-'*70}")

            results.append(result)

        return results

    def cleanup(self):
        """Cleanup resources"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Cleaning up...")

        # Save job memory
        memory_file = f"job_memory_{self.job_id}.json"
        self.job_memory.save_to_file(memory_file)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Final cost: ${self.total_cost:.4f}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Cleanup complete\n")


def main():
    """Main execution function"""

    # Get configuration
    config = get_config()

    # Check environment variables based on configuration
    required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'OPENSEARCH_HOST']

    # Add embedding-specific requirements
    if config.use_tr_openai:
        # Using Thomson Reuters OpenAI - need workspace and asset IDs
        required_env_vars.extend(['TR_WORKSPACE_ID', 'TR_ASSET_ID'])
    else:
        # Using direct OpenAI - need API key
        required_env_vars.append('OPENAI_API_KEY')

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables:")
        if config.use_tr_openai:
            print("  Thomson Reuters OpenAI Embeddings:")
            print("    - TR_WORKSPACE_ID: Your TR workspace ID")
            print("    - TR_ASSET_ID: Your TR asset ID")
        else:
            print("  Direct OpenAI Embeddings:")
            print("    - OPENAI_API_KEY: Your OpenAI API key")
        print("  OpenSearch:")
        print("    - AWS_ACCESS_KEY_ID: AWS access key for OpenSearch")
        print("    - AWS_SECRET_ACCESS_KEY: AWS secret key for OpenSearch")
        print("    - OPENSEARCH_HOST: OpenSearch Serverless endpoint")
        print("\nNote: To switch between TR OpenAI and Direct OpenAI, set use_tr_openai in config/settings.py")
        return

    try:
        # Initialize pipeline
        pipeline = RAGPipeline()

        # Setup components
        pipeline.setup()

        # Load and index documents
        pipeline.load_and_index_documents()

        # Initialize retrieval
        pipeline.initialize_retrieval()

        # Run example queries
        pipeline.run_example_queries()

        # Interactive mode
        pipeline.run_interactive_mode()

        # Cleanup
        pipeline.cleanup()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
