import React, { useState, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Description as FileIcon,
  PlayArrow as StartIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

// API functions
import { uploadFiles, createJob } from '../services/api';

interface UploadedFile {
  filename: string;
  size: number;
  path: string;
}

const FileUpload: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [showJobDialog, setShowJobDialog] = useState(false);
  const [workflowType, setWorkflowType] = useState<'stage2_automation' | 'rag_query'>('stage2_automation');
  const [jobParameters, setJobParameters] = useState<Record<string, any>>({});

  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // Upload mutation
  const uploadMutation = useMutation(uploadFiles, {
    onSuccess: (data) => {
      setUploadedFiles(prev => [...prev, ...data.uploaded_files]);
      toast.success(`Uploaded ${data.count} file(s) successfully`);
      setIsUploading(false);
    },
    onError: (error: any) => {
      toast.error(`Upload failed: ${error.message}`);
      setIsUploading(false);
    },
  });

  // Job creation mutation
  const createJobMutation = useMutation(createJob, {
    onSuccess: (data) => {
      toast.success('Job created successfully!');
      queryClient.invalidateQueries('jobs');
      navigate(`/results/${data.job_id}`);
    },
    onError: (error: any) => {
      toast.error(`Job creation failed: ${error.message}`);
    },
  });

  // Dropzone configuration
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      toast.error('No valid files selected');
      return;
    }

    setIsUploading(true);
    uploadMutation.mutate(acceptedFiles);
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/plain': ['.txt'],
      'application/json': ['.json']
    },
    multiple: true,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const removeFile = (filename: string) => {
    setUploadedFiles(prev => prev.filter(f => f.filename !== filename));
    toast.info(`Removed ${filename}`);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    return <FileIcon color={ext === 'pdf' ? 'error' : ext === 'docx' ? 'primary' : 'info'} />;
  };

  const handleCreateJob = () => {
    if (uploadedFiles.length === 0) {
      toast.error('Please upload files first');
      return;
    }
    setShowJobDialog(true);
  };

  const handleStartJob = () => {
    const jobRequest = {
      workflow_type: workflowType,
      files: uploadedFiles.map(f => f.filename),
      parameters: jobParameters
    };

    createJobMutation.mutate(jobRequest);
    setShowJobDialog(false);
  };

  const getWorkflowDescription = (type: string) => {
    switch (type) {
      case 'stage2_automation':
        return 'Stage 2 Marketing Automation: 5-agent pipeline for enriching business use cases with detailed insights, competitive research, and implementation guidance.';
      case 'rag_query':
        return 'RAG Pipeline Setup: Index documents in vector database for intelligent knowledge retrieval and question answering.';
      default:
        return '';
    }
  };

  const getRequiredFiles = (type: string) => {
    switch (type) {
      case 'stage2_automation':
        return ['Use Cases CSV file', 'BU Intelligence DOCX file', 'Function Updates CSV (optional)'];
      case 'rag_query':
        return ['Any supported document format (PDF, DOCX, CSV, XLSX, TXT, JSON)'];
      default:
        return [];
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          File Upload & Job Creation
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload your documents and start AI processing workflows
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Upload Area */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upload Documents
              </Typography>

              {/* Dropzone */}
              <Box
                {...getRootProps()}
                sx={{
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 2,
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  mb: 3,
                  bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.hover',
                  }
                }}
              >
                <input {...getInputProps()} />
                <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop files here...' : 'Drag & drop files here'}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  or click to browse files
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Supported: PDF, DOCX, CSV, XLSX, TXT, JSON (max 50MB each)
                </Typography>
              </Box>

              {/* Upload Progress */}
              {isUploading && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    Uploading files...
                  </Typography>
                  <LinearProgress />
                </Box>
              )}

              {/* Uploaded Files List */}
              {uploadedFiles.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Uploaded Files ({uploadedFiles.length})
                  </Typography>
                  <List dense>
                    {uploadedFiles.map((file) => (
                      <ListItem key={file.filename} divider>
                        <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                          {getFileIcon(file.filename)}
                        </Box>
                        <ListItemText
                          primary={file.filename}
                          secondary={formatFileSize(file.size)}
                        />
                        <ListItemSecondaryAction>
                          <IconButton
                            edge="end"
                            onClick={() => removeFile(file.filename)}
                            size="small"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>

                  <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <Button
                      variant="contained"
                      startIcon={<StartIcon />}
                      onClick={handleCreateJob}
                      size="large"
                      disabled={createJobMutation.isLoading}
                    >
                      Create Processing Job
                    </Button>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Information Panel */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Workflow Information
              </Typography>

              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Choose the appropriate workflow based on your documents and processing goals.
                </Typography>
              </Alert>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Stage 2 Marketing Automation
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Enriches business use cases through a 5-agent pipeline including competitive research,
                  detailed descriptions, and implementation guidance.
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Required: Use Cases CSV, BU Intelligence DOCX
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  RAG Pipeline
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Creates a searchable knowledge base from your documents using advanced
                  vector embeddings and retrieval techniques.
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Accepts: Any supported document format
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Processing Features
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="Real-time Progress"
                      secondary="Monitor each step"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Quality Assurance"
                      secondary="Automated validation"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Multiple Formats"
                      secondary="Excel, CSV, JSON output"
                    />
                  </ListItem>
                </List>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Job Creation Dialog */}
      <Dialog
        open={showJobDialog}
        onClose={() => setShowJobDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create Processing Job</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <FormControl fullWidth>
              <InputLabel>Workflow Type</InputLabel>
              <Select
                value={workflowType}
                label="Workflow Type"
                onChange={(e) => setWorkflowType(e.target.value as any)}
              >
                <MenuItem value="stage2_automation">Stage 2 Marketing Automation</MenuItem>
                <MenuItem value="rag_query">RAG Pipeline Setup</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Alert severity="info" sx={{ mb: 2 }}>
            {getWorkflowDescription(workflowType)}
          </Alert>

          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Required Files:
            </Typography>
            {getRequiredFiles(workflowType).map((req, index) => (
              <Chip key={index} label={req} size="small" sx={{ mr: 1, mb: 1 }} />
            ))}
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Selected Files ({uploadedFiles.length}):
            </Typography>
            {uploadedFiles.map((file) => (
              <Chip key={file.filename} label={file.filename} size="small" sx={{ mr: 1, mb: 1 }} />
            ))}
          </Box>

          {workflowType === 'stage2_automation' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Batch Size (optional)"
                type="number"
                value={jobParameters.batch_size || ''}
                onChange={(e) => setJobParameters(prev => ({ ...prev, batch_size: parseInt(e.target.value) }))}
                helperText="Number of use cases to process at once (default: 5)"
                sx={{ mb: 2 }}
              />
            </Box>
          )}

          {workflowType === 'rag_query' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Max Results (optional)"
                type="number"
                value={jobParameters.max_results || ''}
                onChange={(e) => setJobParameters(prev => ({ ...prev, max_results: parseInt(e.target.value) }))}
                helperText="Maximum number of search results (default: 10)"
                sx={{ mb: 2 }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowJobDialog(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleStartJob}
            variant="contained"
            disabled={createJobMutation.isLoading}
          >
            Start Job
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FileUpload;