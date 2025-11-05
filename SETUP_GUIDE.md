# BU External Research - Complete Setup Guide

## Quick Start (Recommended)

### Option 1: Windows Batch Scripts
1. **Start Backend**: Double-click `start_backend.bat`
2. **Start Celery** (optional): Double-click `start_celery.bat`
3. **Start Frontend**: Double-click `start_frontend.bat`

### Option 2: Docker (Full Stack)
```bash
# Clone and setup
git clone <repository-url>
cd BU-External-Research

# Set environment variables
copy .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

## Detailed Setup Instructions

### Prerequisites

#### Required Software
- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))

#### Optional (for full functionality)
- **Redis** ([Download](https://redis.io/download) or use Docker)
- **Docker & Docker Compose** ([Download](https://docs.docker.com/desktop/))

#### API Keys Required
- **Anthropic API Key** (for Claude AI)
- **OpenAI API Key** (optional, for embeddings)
- **Thomson Reuters Credentials** (if using TR services)

### Environment Setup

#### 1. Clone Repository
```bash
git clone <repository-url>
cd BU-External-Research
```

#### 2. Environment Variables
Create `.env` file in root directory:
```bash
# AI Service API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Thomson Reuters (if applicable)
TR_WORKSPACE_ID=your_workspace_id
TR_ASSET_ID=your_asset_id

# Database (optional - for production)
DATABASE_URL=postgresql://user:password@localhost:5432/bu_research

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Application Settings
ENVIRONMENT=development
DEBUG=true
```

### Backend Setup

#### Automatic Setup (Windows)
```bash
# Run the batch script
start_backend.bat
```

#### Manual Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
# OR on Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set Python path
set PYTHONPATH=%cd%\..
# OR on Linux/Mac:
export PYTHONPATH=$(pwd)/..

# Start FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Verify Backend
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status": "healthy", "timestamp": "2024-..."}
```

### Celery Setup (Background Tasks)

#### Install Redis
```bash
# Option 1: Docker (Recommended)
docker run -d -p 6379:6379 --name redis redis:alpine

# Option 2: Windows (using Chocolatey)
choco install redis-64

# Option 3: Linux/Mac
# Follow Redis installation guide for your OS
```

#### Start Celery Worker
```bash
# Automatic (Windows)
start_celery.bat

# Manual
cd backend
celery -A celery_app worker --loglevel=info --pool=solo
```

### Frontend Setup

#### Automatic Setup (Windows)
```bash
# Run the batch script
start_frontend.bat
```

#### Manual Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set environment variables
set REACT_APP_API_URL=http://localhost:8000
# OR create .env.local file:
echo REACT_APP_API_URL=http://localhost:8000 > .env.local

# Start development server
npm start
```

#### Verify Frontend
- Open browser to `http://localhost:3000`
- You should see the BU External Research dashboard

### Docker Setup (Alternative)

#### Full Stack with Docker Compose
```bash
# Create environment file
cp .env.example .env

# Edit .env with your API keys
notepad .env  # Windows
# nano .env   # Linux/Mac

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Individual Services
```bash
# Backend only
docker-compose up -d backend redis

# Frontend only
docker-compose up -d frontend

# Celery worker only
docker-compose up -d celery-worker
```

## Configuration

### Backend Configuration

#### API Keys
Update your environment variables:
```bash
# Required for Claude AI functionality
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional for OpenAI embeddings
OPENAI_API_KEY=sk-...

# Thomson Reuters integration
TR_WORKSPACE_ID=ExternalResei8Dz
```

#### File Paths
The system expects these directories:
```
data/
├── Business Units/
│   └── Marketing/
│       ├── Input Files/          # Upload CSV, Excel files here
│       ├── Stage 1/             # BU Intelligence DOCX files
│       └── Stage 2/             # Output files appear here
├── RAGInput/                    # Documents for RAG indexing
└── Prompts, Templates & Inputs/ # Reusable templates
```

### Frontend Configuration

#### API Endpoint
```bash
# Development (default)
REACT_APP_API_URL=http://localhost:8000

# Production
REACT_APP_API_URL=https://your-api-domain.com
```

#### Feature Flags
```bash
# Enable debug logging
REACT_APP_DEBUG=true

# Enable API request logging
REACT_APP_API_DEBUG=true
```

## Usage Guide

### 1. Upload Documents
1. Navigate to **Upload Files** page
2. Drag & drop or click to select files
3. Supported formats: PDF, DOCX, CSV, XLSX, TXT, JSON
4. Choose workflow type:
   - **Stage 2 Automation**: Requires Use Cases CSV + BU Intelligence DOCX
   - **RAG Pipeline**: Accepts any supported documents

### 2. Monitor Jobs
1. Go to **Job Manager** page
2. View real-time progress updates
3. Expand job details to see individual steps
4. Cancel running jobs if needed

### 3. Download Results
1. Wait for job completion (green status)
2. Click **Download Results** button
3. Files saved as Excel format for Stage 2 automation

### 4. Query Knowledge Base
1. Use **RAG Query** page after indexing documents
2. Enter natural language questions
3. View answers with source citations
4. Export or copy results

## Workflows

### Stage 2 Marketing Automation
**Purpose**: Enrich business use cases with AI-generated insights

**Required Files**:
- Use Cases CSV (with columns: Use Case Name, Description, etc.)
- BU Intelligence DOCX (business context document)
- Function Updates CSV (optional)

**Process**:
1. **Data Ingestion**: Load and parse input files
2. **Web Research**: Competitive analysis and market research
3. **Use Case Enrichment**: AI enhancement with 6 sections per use case
4. **Quality Assurance**: Validation and completeness checks
5. **Output Formatting**: Generate formatted Excel file

**Output**: Excel file with enriched use cases including:
- Detailed descriptions (4 sub-headings)
- Business outcomes (4 sub-headings)
- Industry alignment (4 sub-headings)
- Implementation considerations (4 sub-headings)
- Success metrics/KPIs (4 sub-headings)
- Information gaps & annotations (4 sub-headings)

### RAG Pipeline Setup
**Purpose**: Create searchable knowledge base from documents

**Accepted Files**: Any combination of PDF, DOCX, CSV, XLSX, TXT, JSON

**Process**:
1. **Document Loading**: Parse and chunk documents (800 tokens each)
2. **Vector Indexing**: Generate embeddings and create searchable index
3. **Pipeline Ready**: System ready for intelligent queries

**Usage**: After setup, use RAG Query interface to search knowledge base

## Troubleshooting

### Common Issues

#### 1. Backend Won't Start
```bash
# Check Python version
python --version
# Should be 3.9 or higher

# Check if port 8000 is in use
netstat -an | findstr :8000

# Kill process using port 8000 (if needed)
taskkill /f /im python.exe
```

#### 2. Frontend Won't Start
```bash
# Check Node.js version
node --version
# Should be 16 or higher

# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rmdir /s node_modules
npm install
```

#### 3. Celery Tasks Not Running
```bash
# Check if Redis is running
redis-cli ping
# Should return "PONG"

# Check Celery connection
python -c "import redis; r = redis.Redis(); print(r.ping())"
# Should print "True"

# Restart Redis if needed
docker restart redis
```

#### 4. File Upload Fails
- Check file size (max 50MB per file)
- Verify file format is supported
- Ensure backend `/api/upload` endpoint is accessible
- Check browser developer console for errors

#### 5. WebSocket Connection Issues
```bash
# Test WebSocket endpoint
# Install wscat: npm install -g wscat
wscat -c ws://localhost:8000/ws/test-job-id
```

#### 6. API Connection Errors
```bash
# Test backend API directly
curl -X GET http://localhost:8000/api/health

# Check CORS settings if accessing from different domain
# Verify API URL in frontend environment variables
```

### Debug Mode

#### Backend Debug
```bash
# Enable detailed logging
set PYTHONPATH=%cd%
set DEBUG=true
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

#### Frontend Debug
```bash
# Enable debug logging
set REACT_APP_DEBUG=true
set REACT_APP_API_DEBUG=true
npm start
```

### Log Files

#### Backend Logs
- Console output shows API requests and responses
- Celery worker logs show background task progress
- Check for Python traceback errors

#### Frontend Logs
- Browser developer console (F12)
- Network tab shows API request/response details
- React DevTools for component debugging

## Performance Optimization

### Backend Optimization
- **Batch Processing**: Configure batch sizes in job parameters
- **Caching**: Enable Redis caching for API responses
- **Database**: Use PostgreSQL for production job storage
- **File Storage**: Consider cloud storage for large files

### Frontend Optimization
- **Bundle Splitting**: Automatic code splitting by route
- **API Caching**: React Query handles intelligent caching
- **Image Optimization**: Lazy loading for large lists
- **WebSocket Efficiency**: Auto-disconnect inactive connections

## Security Considerations

### API Security
- **Input Validation**: All inputs validated on backend
- **File Type Restrictions**: Only allowed file extensions accepted
- **Size Limits**: Maximum file sizes enforced
- **Path Sanitization**: Secure file path handling

### Authentication (Future Enhancement)
The system currently runs without authentication. For production:
- Implement JWT token authentication
- Add user management system
- Configure role-based access control
- Enable audit logging

### Network Security
- **HTTPS**: Enable SSL/TLS in production
- **CORS**: Configure allowed origins
- **Rate Limiting**: Prevent API abuse
- **Firewall**: Restrict network access

## Deployment

### Development Deployment
```bash
# Backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm start
```

### Production Deployment

#### Docker Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale celery-worker=3
```

#### Traditional Deployment
```bash
# Backend (with gunicorn)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app

# Frontend (build and serve)
npm run build
npm install -g serve
serve -s build -l 3000
```

## Monitoring

### Health Checks
- **Backend**: `http://localhost:8000/api/health`
- **Frontend**: `http://localhost:3000` (should load dashboard)
- **Redis**: `redis-cli ping` (should return "PONG")
- **Celery**: Check worker logs for task processing

### Performance Monitoring
- Monitor API response times
- Track job completion rates
- Watch memory usage during large file processing
- Monitor WebSocket connection stability

## Support

### Getting Help
1. **Check Logs**: Review console output for error messages
2. **Test Components**: Verify each service individually
3. **Documentation**: Review this guide and component READMEs
4. **Issue Reporting**: Provide logs and reproduction steps

### Contact Information
- **Technical Issues**: Check troubleshooting section first
- **Feature Requests**: Submit through appropriate channels
- **Bug Reports**: Include environment details and logs

---

This setup guide provides comprehensive instructions for deploying the BU External Research system in both development and production environments.