"""
FastAPI Backend for BU External Research System

This backend provides REST API endpoints for:
1. File upload and management
2. Job scheduling and monitoring
3. RAG query processing
4. Results retrieval and download
5. Real-time progress updates via WebSocket
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import os
import uuid
import shutil
from datetime import datetime
import logging
from pathlib import Path

# Import your existing modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Import existing automation and RAG components
try:
    from Automation.Business_Units.Marketing.Stage2.orchestrator import Stage2Orchestrator
    from rag_pipeline.main import RAGPipeline
    from rag_pipeline.config.settings import RAGConfig
except ImportError as e:
    logging.warning(f"Could not import some modules: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BU External Research API",
    description="Backend API for AI-powered business intelligence research and enrichment",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
TEMP_DIR = Path("temp")

for dir_path in [UPLOAD_DIR, RESULTS_DIR, TEMP_DIR]:
    dir_path.mkdir(exist_ok=True)

# In-memory storage for jobs (in production, use Redis/Database)
jobs_store: Dict[str, Dict] = {}
active_connections: Dict[str, WebSocket] = {}

# Pydantic models for API requests/responses
class JobRequest(BaseModel):
    workflow_type: str  # "stage2_automation" or "rag_query"
    files: List[str]    # List of uploaded file names
    parameters: Dict[str, Any] = {}

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: float  # 0.0 to 1.0
    current_step: Optional[str] = None
    total_steps: int = 0
    completed_steps: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    results: Optional[Dict[str, Any]] = None

class RAGQuery(BaseModel):
    query: str
    max_results: int = 10
    include_sources: bool = True

class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    query_id: str
    processing_time: float

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_job_update(self, job_id: str, update: Dict):
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_text(json.dumps(update))
            except Exception as e:
                logger.error(f"Error sending update to {job_id}: {e}")
                self.disconnect(job_id)

manager = ConnectionManager()

# Utility functions
def create_job_id() -> str:
    return str(uuid.uuid4())

def update_job_status(job_id: str, status: str, progress: float = None,
                     current_step: str = None, error_message: str = None,
                     completed_steps: int = None, results: Dict = None):
    """Update job status and notify WebSocket clients"""
    if job_id not in jobs_store:
        return

    job = jobs_store[job_id]
    job["status"] = status
    job["updated_at"] = datetime.now()

    if progress is not None:
        job["progress"] = progress
    if current_step is not None:
        job["current_step"] = current_step
    if error_message is not None:
        job["error_message"] = error_message
    if completed_steps is not None:
        job["completed_steps"] = completed_steps
    if results is not None:
        job["results"] = results

    # Send WebSocket update
    update = {
        "job_id": job_id,
        "status": status,
        "progress": job.get("progress", 0.0),
        "current_step": current_step,
        "completed_steps": job.get("completed_steps", 0),
        "total_steps": job.get("total_steps", 0)
    }

    asyncio.create_task(manager.send_job_update(job_id, update))

# API Endpoints

@app.get("/")
async def root():
    return {"message": "BU External Research API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload multiple files for processing"""
    uploaded_files = []

    for file in files:
        if not file.filename:
            continue

        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.csv', '.xlsx', '.txt', '.json'}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
            )

        # Save file
        file_path = UPLOAD_DIR / file.filename
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            uploaded_files.append({
                "filename": file.filename,
                "size": file_path.stat().st_size,
                "path": str(file_path)
            })

        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save {file.filename}")

    return {"uploaded_files": uploaded_files, "count": len(uploaded_files)}

@app.post("/api/jobs")
async def create_job(job_request: JobRequest):
    """Create a new processing job"""
    job_id = create_job_id()

    # Validate workflow type
    if job_request.workflow_type not in ["stage2_automation", "rag_query"]:
        raise HTTPException(status_code=400, detail="Invalid workflow_type")

    # Validate uploaded files exist
    for filename in job_request.files:
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    # Create job entry
    total_steps = 5 if job_request.workflow_type == "stage2_automation" else 3

    jobs_store[job_id] = {
        "job_id": job_id,
        "workflow_type": job_request.workflow_type,
        "files": job_request.files,
        "parameters": job_request.parameters,
        "status": "pending",
        "progress": 0.0,
        "current_step": "Initializing...",
        "total_steps": total_steps,
        "completed_steps": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "error_message": None,
        "results": None
    }

    # Start background processing
    asyncio.create_task(process_job(job_id))

    return {"job_id": job_id, "status": "created"}

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and progress"""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs_store[job_id]

@app.get("/api/jobs")
async def list_jobs():
    """List all jobs"""
    return {"jobs": list(jobs_store.values())}

@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_store[job_id]
    if job["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")

    update_job_status(job_id, "cancelled")
    return {"message": "Job cancelled"}

@app.get("/api/jobs/{job_id}/results")
async def get_job_results(job_id: str):
    """Get job results"""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_store[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    return job.get("results", {})

@app.get("/api/jobs/{job_id}/download")
async def download_results(job_id: str):
    """Download job result files"""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_store[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    results = job.get("results", {})
    if "output_file" not in results:
        raise HTTPException(status_code=404, detail="No output file available")

    file_path = Path(results["output_file"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type='application/octet-stream'
    )

@app.post("/api/rag/query")
async def rag_query(query_request: RAGQuery):
    """Process RAG query"""
    query_id = create_job_id()

    try:
        # Initialize RAG pipeline (simplified for demo)
        start_time = datetime.now()

        # This would use your actual RAG pipeline
        # rag_pipeline = RAGPipeline(RAGConfig())
        # response = await rag_pipeline.query(query_request.query)

        # Mock response for now
        response = {
            "answer": f"This is a mock response to: {query_request.query}",
            "sources": [
                {
                    "document": "Sample Document 1",
                    "page": 1,
                    "relevance_score": 0.95,
                    "snippet": "Sample relevant text snippet..."
                }
            ]
        }

        processing_time = (datetime.now() - start_time).total_seconds()

        return RAGResponse(
            answer=response["answer"],
            sources=response.get("sources", []),
            query_id=query_id,
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Error processing RAG query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job updates"""
    await manager.connect(websocket, job_id)
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(job_id)

# Background processing function
async def process_job(job_id: str):
    """Process job in background"""
    try:
        job = jobs_store[job_id]
        workflow_type = job["workflow_type"]

        update_job_status(job_id, "running", 0.1, "Starting job...")

        if workflow_type == "stage2_automation":
            await process_stage2_automation(job_id)
        elif workflow_type == "rag_query":
            await process_rag_job(job_id)

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        update_job_status(job_id, "failed", error_message=str(e))

async def process_stage2_automation(job_id: str):
    """Process Stage 2 Marketing Automation"""
    job = jobs_store[job_id]

    try:
        # Step 1: Data Ingestion
        update_job_status(job_id, "running", 0.2, "Agent 1: Data Ingestion", completed_steps=1)
        await asyncio.sleep(2)  # Simulate processing time

        # Step 2: Web Research
        update_job_status(job_id, "running", 0.4, "Agent 2: Web Research", completed_steps=2)
        await asyncio.sleep(3)

        # Step 3: Use Case Enrichment
        update_job_status(job_id, "running", 0.6, "Agent 3: Use Case Enrichment", completed_steps=3)
        await asyncio.sleep(5)

        # Step 4: Quality Assurance
        update_job_status(job_id, "running", 0.8, "Agent 4: Quality Assurance", completed_steps=4)
        await asyncio.sleep(2)

        # Step 5: Output Formatting
        update_job_status(job_id, "running", 0.9, "Agent 5: Output Formatting", completed_steps=5)
        await asyncio.sleep(1)

        # Complete with results
        results = {
            "output_file": "data/Business Units/Marketing/Stage 2/2b-MKTG-Existing Use Cases Enriched.xlsx",
            "enriched_use_cases": 15,
            "processing_time": "12 minutes",
            "quality_score": 0.92
        }

        update_job_status(job_id, "completed", 1.0, "Job completed successfully",
                         completed_steps=5, results=results)

    except Exception as e:
        update_job_status(job_id, "failed", error_message=str(e))

async def process_rag_job(job_id: str):
    """Process RAG pipeline job"""
    try:
        # Step 1: Document Loading
        update_job_status(job_id, "running", 0.3, "Loading documents...", completed_steps=1)
        await asyncio.sleep(2)

        # Step 2: Vector Indexing
        update_job_status(job_id, "running", 0.7, "Creating vector index...", completed_steps=2)
        await asyncio.sleep(3)

        # Step 3: Ready for queries
        results = {
            "documents_indexed": 25,
            "vector_dimensions": 3072,
            "index_status": "ready"
        }

        update_job_status(job_id, "completed", 1.0, "RAG pipeline ready",
                         completed_steps=3, results=results)

    except Exception as e:
        update_job_status(job_id, "failed", error_message=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)