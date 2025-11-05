"""
Celery configuration for background task processing

This module sets up Celery for handling long-running tasks like:
- Stage 2 Marketing Automation (5-agent pipeline)
- RAG pipeline processing
- Document indexing and embedding generation
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import your existing modules
try:
    from Automation.Business_Units.Marketing.Stage2.orchestrator import Stage2Orchestrator
    from rag_pipeline.main import RAGPipeline
    from rag_pipeline.config.settings import RAGConfig
except ImportError as e:
    logging.warning(f"Could not import some modules: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'bu_research',
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=['backend.celery_app']
)

# Celery settings
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_routes={
        'backend.celery_app.process_stage2_automation': {'queue': 'automation'},
        'backend.celery_app.process_rag_pipeline': {'queue': 'rag'},
        'backend.celery_app.process_rag_query': {'queue': 'queries'},
    },
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Progress callback for job updates
def update_progress(job_id: str, progress: float, status: str, current_step: str = None):
    """Update job progress in Redis/Database"""
    # In production, this would update a database or Redis
    # For now, we'll log the progress
    logger.info(f"Job {job_id}: {progress:.1%} - {status} - {current_step}")

    # You can also use Celery's result backend to store progress
    celery_app.backend.set(
        f"job_progress_{job_id}",
        {
            "progress": progress,
            "status": status,
            "current_step": current_step,
            "updated_at": datetime.now().isoformat()
        }
    )

@celery_app.task(bind=True)
def process_stage2_automation(self, job_id: str, files: list, parameters: dict):
    """
    Process Stage 2 Marketing Automation Pipeline

    Args:
        job_id: Unique job identifier
        files: List of uploaded file paths
        parameters: Job configuration parameters
    """
    try:
        logger.info(f"Starting Stage 2 automation for job {job_id}")

        # Update progress: Job started
        update_progress(job_id, 0.0, "running", "Initializing automation pipeline...")

        # Initialize orchestrator
        orchestrator = Stage2Orchestrator()

        # Step 1: Data Ingestion
        update_progress(job_id, 0.1, "running", "Agent 1: Data Ingestion")

        # Find required files
        use_cases_file = None
        bu_intelligence_file = None
        function_updates_file = None

        for file_path in files:
            if "use_cases" in file_path.lower():
                use_cases_file = file_path
            elif "bu_intelligence" in file_path.lower() or file_path.endswith('.docx'):
                bu_intelligence_file = file_path
            elif "function_updates" in file_path.lower():
                function_updates_file = file_path

        if not use_cases_file or not bu_intelligence_file:
            raise ValueError("Required files missing: Use cases CSV and BU intelligence DOCX")

        # Execute Agent 1: Data Ingestion
        context_data = orchestrator.run_agent1(
            bu_intelligence_path=bu_intelligence_file,
            use_cases_path=use_cases_file,
            function_updates_path=function_updates_file
        )

        # Step 2: Web Research
        update_progress(job_id, 0.25, "running", "Agent 2: Web Research")

        research_data = orchestrator.run_agent2(context_data)

        # Step 3: Use Case Enrichment
        update_progress(job_id, 0.4, "running", "Agent 3: Use Case Enrichment")

        enriched_data = orchestrator.run_agent3(context_data, research_data)

        # Step 4: Quality Assurance
        update_progress(job_id, 0.7, "running", "Agent 4: Quality Assurance")

        qa_results = orchestrator.run_agent4(enriched_data)

        # Step 5: Output Formatting
        update_progress(job_id, 0.9, "running", "Agent 5: Output Formatting")

        output_file = orchestrator.run_agent5(qa_results)

        # Complete
        update_progress(job_id, 1.0, "completed", "All agents completed successfully")

        return {
            "status": "completed",
            "output_file": output_file,
            "enriched_use_cases": len(enriched_data.get("use_cases", [])),
            "processing_time": "Completed",
            "agents_executed": 5,
            "quality_score": qa_results.get("quality_score", 0.0)
        }

    except Exception as e:
        error_msg = f"Stage 2 automation failed: {str(e)}"
        logger.error(f"Job {job_id} failed: {error_msg}")
        logger.error(traceback.format_exc())

        update_progress(job_id, 0.0, "failed", f"Error: {error_msg}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60, exc=e)

        raise e

@celery_app.task(bind=True)
def process_rag_pipeline(self, job_id: str, files: list, parameters: dict):
    """
    Process RAG Pipeline Setup

    Args:
        job_id: Unique job identifier
        files: List of document files to index
        parameters: RAG configuration parameters
    """
    try:
        logger.info(f"Starting RAG pipeline setup for job {job_id}")

        update_progress(job_id, 0.0, "running", "Initializing RAG pipeline...")

        # Initialize RAG pipeline with config
        config = RAGConfig()
        rag_pipeline = RAGPipeline(config)

        # Step 1: Document Loading
        update_progress(job_id, 0.2, "running", "Loading and chunking documents...")

        documents = []
        for file_path in files:
            docs = rag_pipeline.load_documents(file_path)
            documents.extend(docs)

        logger.info(f"Loaded {len(documents)} document chunks")

        # Step 2: Generate Embeddings
        update_progress(job_id, 0.5, "running", "Generating embeddings...")

        embeddings = rag_pipeline.generate_embeddings(documents)

        # Step 3: Create Vector Index
        update_progress(job_id, 0.8, "running", "Creating vector index...")

        index_info = rag_pipeline.create_vector_index(documents, embeddings)

        # Complete
        update_progress(job_id, 1.0, "completed", "RAG pipeline ready for queries")

        return {
            "status": "completed",
            "documents_indexed": len(documents),
            "vector_dimensions": config.embedding_config.dimension,
            "index_name": index_info.get("index_name"),
            "ready_for_queries": True
        }

    except Exception as e:
        error_msg = f"RAG pipeline setup failed: {str(e)}"
        logger.error(f"Job {job_id} failed: {error_msg}")
        logger.error(traceback.format_exc())

        update_progress(job_id, 0.0, "failed", f"Error: {error_msg}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60, exc=e)

        raise e

@celery_app.task(bind=True)
def process_rag_query(self, query_id: str, query: str, parameters: dict):
    """
    Process single RAG query

    Args:
        query_id: Unique query identifier
        query: User query text
        parameters: Query configuration
    """
    try:
        logger.info(f"Processing RAG query {query_id}: {query}")

        # Initialize RAG pipeline
        config = RAGConfig()
        rag_pipeline = RAGPipeline(config)

        # Process query through RAG pipeline
        result = rag_pipeline.query(
            query=query,
            max_results=parameters.get("max_results", 10),
            include_sources=parameters.get("include_sources", True)
        )

        return {
            "query_id": query_id,
            "query": query,
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "processing_time": result.get("processing_time", 0.0),
            "tokens_used": result.get("tokens_used", 0)
        }

    except Exception as e:
        error_msg = f"RAG query failed: {str(e)}"
        logger.error(f"Query {query_id} failed: {error_msg}")
        logger.error(traceback.format_exc())

        raise e

# Celery signal handlers
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handler called before task execution"""
    logger.info(f"Task {task.name} [{task_id}] started")

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None,
                        retval=None, state=None, **kwds):
    """Handler called after task execution"""
    logger.info(f"Task {task.name} [{task_id}] finished with state: {state}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None,
                        traceback=None, einfo=None, **kwds):
    """Handler called on task failure"""
    logger.error(f"Task {sender.name} [{task_id}] failed: {exception}")
    logger.error(f"Traceback: {traceback}")

# Utility function to get job progress
def get_job_progress(job_id: str):
    """Get current job progress from backend"""
    try:
        progress_data = celery_app.backend.get(f"job_progress_{job_id}")
        return progress_data
    except Exception as e:
        logger.error(f"Error getting progress for job {job_id}: {e}")
        return None

if __name__ == '__main__':
    celery_app.start()