import axios from 'axios';

// API base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error.response?.data || error);
  }
);

// Types
export interface UploadedFile {
  filename: string;
  size: number;
  path: string;
}

export interface JobRequest {
  workflow_type: 'stage2_automation' | 'rag_query';
  files: string[];
  parameters?: Record<string, any>;
}

export interface JobStatus {
  job_id: string;
  workflow_type: string;
  files: string[];
  parameters: Record<string, any>;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  current_step?: string;
  total_steps: number;
  completed_steps: number;
  created_at: string;
  updated_at: string;
  error_message?: string;
  results?: Record<string, any>;
}

export interface RAGQuery {
  query: string;
  max_results?: number;
  include_sources?: boolean;
}

export interface RAGResponse {
  answer: string;
  sources: Array<{
    document: string;
    page?: number;
    relevance_score: number;
    snippet: string;
  }>;
  query_id: string;
  processing_time: number;
}

// API Functions

// Health check
export const getSystemHealth = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

// File upload
export const uploadFiles = async (files: File[]): Promise<{ uploaded_files: UploadedFile[]; count: number }> => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 1 minute for file uploads
  });

  return response.data;
};

// Job management
export const createJob = async (jobRequest: JobRequest): Promise<{ job_id: string; status: string }> => {
  const response = await api.post('/api/jobs', jobRequest);
  return response.data;
};

export const getJob = async (jobId: string): Promise<JobStatus> => {
  const response = await api.get(`/api/jobs/${jobId}`);
  return response.data;
};

export const getJobs = async (): Promise<{ jobs: JobStatus[] }> => {
  const response = await api.get('/api/jobs');
  return response.data;
};

export const cancelJob = async (jobId: string): Promise<{ message: string }> => {
  const response = await api.delete(`/api/jobs/${jobId}`);
  return response.data;
};

export const getJobResults = async (jobId: string): Promise<Record<string, any>> => {
  const response = await api.get(`/api/jobs/${jobId}/results`);
  return response.data;
};

export const downloadJobResults = async (jobId: string): Promise<Blob> => {
  const response = await api.get(`/api/jobs/${jobId}/download`, {
    responseType: 'blob',
  });
  return response.data;
};

// RAG queries
export const submitRAGQuery = async (query: RAGQuery): Promise<RAGResponse> => {
  const response = await api.post('/api/rag/query', query, {
    timeout: 60000, // 1 minute for RAG queries
  });
  return response.data;
};

// WebSocket connection helper
export const createWebSocketConnection = (jobId: string): WebSocket => {
  const wsUrl = API_BASE_URL.replace('http', 'ws') + `/ws/${jobId}`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log(`WebSocket connected for job ${jobId}`);
  };

  ws.onclose = () => {
    console.log(`WebSocket disconnected for job ${jobId}`);
  };

  ws.onerror = (error) => {
    console.error(`WebSocket error for job ${jobId}:`, error);
  };

  return ws;
};

// Utility functions
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const getStatusColor = (status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
  switch (status) {
    case 'completed': return 'success';
    case 'running': return 'primary';
    case 'failed': return 'error';
    case 'cancelled': return 'warning';
    case 'pending': return 'info';
    default: return 'default';
  }
};

export const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString();
};

export const calculateProgress = (completedSteps: number, totalSteps: number): number => {
  if (totalSteps === 0) return 0;
  return Math.round((completedSteps / totalSteps) * 100);
};

// Error handling helper
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return Array.isArray(error.response.data.detail)
      ? error.response.data.detail[0].msg
      : error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export default api;