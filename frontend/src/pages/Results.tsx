import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Paper,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Share as ShareIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
  Description as FileIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from 'react-query';
import { toast } from 'react-toastify';
import { saveAs } from 'file-saver';

// Services and hooks
import { getJob, downloadJobResults } from '../services/api';
import useWebSocket from '../hooks/useWebSocket';

const Results: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});

  // Fetch job data
  const { data: job, isLoading, error, refetch } = useQuery(
    ['job', jobId],
    () => getJob(jobId!),
    {
      enabled: !!jobId,
      refetchInterval: (data) => {
        // Stop polling when job is completed or failed
        return data?.status === 'running' || data?.status === 'pending' ? 2000 : false;
      },
    }
  );

  // Real-time updates via WebSocket
  useWebSocket(jobId!, {
    onUpdate: (update) => {
      console.log('Real-time job update:', update);
      refetch(); // Refresh the job data
    }
  });

  // Download mutation
  const downloadMutation = useMutation(downloadJobResults, {
    onSuccess: (blob) => {
      const filename = job?.workflow_type === 'stage2_automation'
        ? `${jobId}-enriched-use-cases.xlsx`
        : `${jobId}-results.xlsx`;
      saveAs(blob, filename);
      toast.success('File downloaded successfully');
    },
    onError: (error: any) => {
      toast.error(`Download failed: ${error.message}`);
    },
  });

  const handleDownload = () => {
    if (jobId) {
      downloadMutation.mutate(jobId);
    }
  };

  const handleShare = async () => {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      toast.success('Results URL copied to clipboard');
    } catch (error) {
      toast.error('Failed to copy URL');
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckIcon color="success" />;
      case 'running': return <CircularProgress size={20} color="primary" />;
      case 'failed': return <ErrorIcon color="error" />;
      case 'cancelled': return <WarningIcon color="warning" />;
      default: return <InfoIcon color="info" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'failed': return 'error';
      case 'cancelled': return 'warning';
      case 'pending': return 'info';
      default: return 'default';
    }
  };

  const getWorkflowSteps = (workflowType: string) => {
    switch (workflowType) {
      case 'stage2_automation':
        return [
          { name: 'Data Ingestion', description: 'Loading and parsing input documents' },
          { name: 'Web Research', description: 'Competitive analysis and market research' },
          { name: 'Use Case Enrichment', description: 'AI-powered content enhancement' },
          { name: 'Quality Assurance', description: 'Validation and quality checks' },
          { name: 'Output Formatting', description: 'Excel file generation and formatting' }
        ];
      case 'rag_query':
        return [
          { name: 'Document Loading', description: 'Loading and chunking documents' },
          { name: 'Vector Indexing', description: 'Creating searchable vector index' },
          { name: 'Pipeline Ready', description: 'System ready for queries' }
        ];
      default:
        return [];
    }
  };

  const formatDuration = (start: string, end?: string) => {
    const startTime = new Date(start);
    const endTime = end ? new Date(end) : new Date();
    const diffMs = endTime.getTime() - startTime.getTime();
    const minutes = Math.floor(diffMs / 60000);
    const seconds = Math.floor((diffMs % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !job) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          Failed to load job results. Job may not exist or may have been deleted.
          <Button onClick={() => navigate('/jobs')} sx={{ ml: 2 }}>
            Back to Jobs
          </Button>
        </Alert>
      </Container>
    );
  }

  const steps = getWorkflowSteps(job.workflow_type);

  return (
    <Container maxWidth="lg">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            Job Results
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={() => refetch()}
              disabled={isLoading}
            >
              Refresh
            </Button>
            <Button
              variant="outlined"
              startIcon={<ShareIcon />}
              onClick={handleShare}
            >
              Share
            </Button>
            {job.status === 'completed' && (
              <Button
                variant="contained"
                startIcon={downloadMutation.isLoading ? <CircularProgress size={20} /> : <DownloadIcon />}
                onClick={handleDownload}
                disabled={downloadMutation.isLoading}
              >
                Download Results
              </Button>
            )}
          </Box>
        </Box>
        <Typography variant="body1" color="text.secondary">
          {job.workflow_type === 'stage2_automation' ? 'Stage 2 Marketing Automation' : 'RAG Pipeline Setup'}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Job Status Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {getStatusIcon(job.status)}
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Job Status
                </Typography>
              </Box>

              <Chip
                label={job.status.toUpperCase()}
                color={getStatusColor(job.status) as any}
                size="medium"
                sx={{ mb: 2, fontWeight: 'bold' }}
              />

              {job.status === 'running' && (
                <Box sx={{ mb: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={job.progress * 100}
                    sx={{ mb: 1, height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {Math.round(job.progress * 100)}% Complete
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {job.current_step}
                  </Typography>
                </Box>
              )}

              <List dense>
                <ListItem>
                  <ListItemIcon><ScheduleIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary="Duration"
                    secondary={formatDuration(job.created_at, job.updated_at)}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><FileIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary="Input Files"
                    secondary={`${job.files.length} file(s)`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><AssessmentIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary="Steps"
                    secondary={`${job.completed_steps}/${job.total_steps} completed`}
                  />
                </ListItem>
              </List>

              <Button
                fullWidth
                variant="outlined"
                onClick={() => setShowDetailsDialog(true)}
                sx={{ mt: 2 }}
              >
                View Job Details
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Progress Steps */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Processing Steps
              </Typography>

              {steps.map((step, index) => {
                const isCompleted = index < job.completed_steps;
                const isCurrent = index === job.completed_steps && job.status === 'running';
                const isPending = index > job.completed_steps;

                return (
                  <Accordion
                    key={index}
                    expanded={expandedSections[`step-${index}`] || false}
                    onChange={() => toggleSection(`step-${index}`)}
                    disabled={isPending}
                  >
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                        {isCompleted && <CheckIcon color="success" />}
                        {isCurrent && <CircularProgress size={20} color="primary" />}
                        {isPending && <InfoIcon color="disabled" />}

                        <Typography
                          variant="body1"
                          sx={{
                            fontWeight: isCurrent ? 'bold' : 'normal',
                            color: isCompleted ? 'success.main' : isCurrent ? 'primary.main' : 'text.secondary'
                          }}
                        >
                          {index + 1}. {step.name}
                        </Typography>

                        {isCurrent && (
                          <Chip label="Current" color="primary" size="small" />
                        )}
                        {isCompleted && (
                          <Chip label="Completed" color="success" size="small" />
                        )}
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="text.secondary">
                        {step.description}
                      </Typography>
                      {isCurrent && job.current_step && (
                        <Alert severity="info" sx={{ mt: 2 }}>
                          {job.current_step}
                        </Alert>
                      )}
                    </AccordionDetails>
                  </Accordion>
                );
              })}
            </CardContent>
          </Card>
        </Grid>

        {/* Results Section */}
        {job.status === 'completed' && job.results && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Results Summary
                </Typography>

                <Grid container spacing={3}>
                  {Object.entries(job.results).map(([key, value]) => {
                    const displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    return (
                      <Grid item xs={12} sm={6} md={3} key={key}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="h4" color="primary">
                            {typeof value === 'number' ? value : String(value)}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {displayKey}
                          </Typography>
                        </Paper>
                      </Grid>
                    );
                  })}
                </Grid>

                {job.workflow_type === 'stage2_automation' && (
                  <Alert severity="success" sx={{ mt: 3 }}>
                    <Typography variant="body1">
                      Your use cases have been successfully enriched! The output Excel file contains
                      detailed descriptions, business outcomes, industry alignment, implementation
                      considerations, and success metrics.
                    </Typography>
                  </Alert>
                )}

                {job.workflow_type === 'rag_query' && (
                  <Alert severity="success" sx={{ mt: 3 }}>
                    <Typography variant="body1">
                      Your documents have been successfully indexed! You can now use the RAG Query
                      interface to search through your knowledge base.
                    </Typography>
                    <Button
                      variant="contained"
                      onClick={() => navigate('/query')}
                      sx={{ mt: 2 }}
                    >
                      Start Querying
                    </Button>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Error Section */}
        {job.status === 'failed' && job.error_message && (
          <Grid item xs={12}>
            <Alert severity="error">
              <Typography variant="h6" gutterBottom>
                Job Failed
              </Typography>
              <Typography variant="body2">
                {job.error_message}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/upload')}
                  sx={{ mr: 2 }}
                >
                  Try Again
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/jobs')}
                >
                  View All Jobs
                </Button>
              </Box>
            </Alert>
          </Grid>
        )}
      </Grid>

      {/* Job Details Dialog */}
      <Dialog
        open={showDetailsDialog}
        onClose={() => setShowDetailsDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Job Details</DialogTitle>
        <DialogContent>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell><strong>Job ID</strong></TableCell>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{job.job_id}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell><strong>Workflow Type</strong></TableCell>
                  <TableCell>{job.workflow_type}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell><strong>Status</strong></TableCell>
                  <TableCell>
                    <Chip label={job.status} color={getStatusColor(job.status) as any} size="small" />
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell><strong>Created</strong></TableCell>
                  <TableCell>{new Date(job.created_at).toLocaleString()}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell><strong>Updated</strong></TableCell>
                  <TableCell>{new Date(job.updated_at).toLocaleString()}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell><strong>Progress</strong></TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <LinearProgress
                        variant="determinate"
                        value={job.progress * 100}
                        sx={{ width: 100, mr: 2 }}
                      />
                      {Math.round(job.progress * 100)}%
                    </Box>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell><strong>Input Files</strong></TableCell>
                  <TableCell>
                    {job.files.map((filename, index) => (
                      <Chip key={index} label={filename} size="small" sx={{ mr: 1, mb: 1 }} />
                    ))}
                  </TableCell>
                </TableRow>
                {Object.entries(job.parameters || {}).length > 0 && (
                  <TableRow>
                    <TableCell><strong>Parameters</strong></TableCell>
                    <TableCell>
                      <pre>{JSON.stringify(job.parameters, null, 2)}</pre>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDetailsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Results;