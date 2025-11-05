import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Collapse
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  MoreVert as MoreIcon,
  Cancel as CancelIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  PlayArrow as StartIcon,
  Pause as PauseIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

// Services and hooks
import { getJobs, cancelJob, downloadJobResults, JobStatus } from '../services/api';
import useWebSocket from '../hooks/useWebSocket';

interface JobDetailsProps {
  job: JobStatus;
  onRefresh: () => void;
}

const JobDetails: React.FC<JobDetailsProps> = ({ job, onRefresh }) => {
  const [expanded, setExpanded] = useState(false);

  // Real-time updates via WebSocket
  useWebSocket(job.job_id, {
    onUpdate: (update) => {
      console.log('Job update received:', update);
      onRefresh(); // Refresh the job data
    }
  });

  const getStepStatus = (stepIndex: number, completedSteps: number, currentStep: string, status: string) => {
    if (stepIndex < completedSteps) return 'completed';
    if (stepIndex === completedSteps && status === 'running') return 'current';
    return 'pending';
  };

  const getStepColor = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed': return 'success';
      case 'current': return 'primary';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  const getWorkflowSteps = (workflowType: string) => {
    switch (workflowType) {
      case 'stage2_automation':
        return [
          'Data Ingestion',
          'Web Research',
          'Use Case Enrichment',
          'Quality Assurance',
          'Output Formatting'
        ];
      case 'rag_query':
        return [
          'Document Loading',
          'Vector Indexing',
          'Pipeline Ready'
        ];
      default:
        return ['Processing...'];
    }
  };

  const steps = getWorkflowSteps(job.workflow_type);

  return (
    <Box sx={{ mt: 2 }}>
      <Button
        onClick={() => setExpanded(!expanded)}
        endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        size="small"
      >
        {expanded ? 'Hide Details' : 'Show Details'}
      </Button>

      <Collapse in={expanded}>
        <Box sx={{ mt: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
          {/* Job Info */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Job ID</Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{job.job_id}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Created</Typography>
              <Typography variant="body2">{new Date(job.created_at).toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Updated</Typography>
              <Typography variant="body2">{new Date(job.updated_at).toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Files</Typography>
              <Typography variant="body2">{job.files.length} file(s)</Typography>
            </Grid>
          </Grid>

          {/* Files */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="caption" color="text.secondary">Input Files:</Typography>
            <Box sx={{ mt: 1 }}>
              {job.files.map((filename, index) => (
                <Chip key={index} label={filename} size="small" sx={{ mr: 1, mb: 1 }} />
              ))}
            </Box>
          </Box>

          {/* Processing Steps */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Processing Steps ({job.completed_steps}/{job.total_steps}):
            </Typography>
            <Box sx={{ mt: 2 }}>
              {steps.map((stepName, index) => {
                const stepStatus = getStepStatus(index, job.completed_steps, job.current_step || '', job.status);
                return (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Chip
                      label={`${index + 1}. ${stepName}`}
                      color={getStepColor(stepStatus) as any}
                      size="small"
                      variant={stepStatus === 'current' ? 'filled' : 'outlined'}
                      sx={{ minWidth: 200, justifyContent: 'flex-start' }}
                    />
                    {stepStatus === 'current' && job.current_step && (
                      <Typography variant="caption" sx={{ ml: 2, color: 'primary.main' }}>
                        {job.current_step}
                      </Typography>
                    )}
                  </Box>
                );
              })}
            </Box>
          </Box>

          {/* Error Message */}
          {job.error_message && (
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="body2">{job.error_message}</Typography>
            </Alert>
          )}

          {/* Results Summary */}
          {job.results && job.status === 'completed' && (
            <Box>
              <Typography variant="caption" color="text.secondary">Results:</Typography>
              <Box sx={{ mt: 1, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                {Object.entries(job.results).map(([key, value]) => (
                  <Typography key={key} variant="body2">
                    <strong>{key.replace(/_/g, ' ')}:</strong> {String(value)}
                  </Typography>
                ))}
              </Box>
            </Box>
          )}
        </Box>
      </Collapse>
    </Box>
  );
};

const JobManager: React.FC = () => {
  const [selectedJob, setSelectedJob] = useState<JobStatus | null>(null);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);

  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch jobs
  const { data: jobsData, isLoading, refetch } = useQuery(
    'jobs',
    getJobs,
    {
      refetchInterval: 5000, // Refresh every 5 seconds
      refetchIntervalInBackground: true
    }
  );

  // Cancel job mutation
  const cancelJobMutation = useMutation(cancelJob, {
    onSuccess: () => {
      toast.success('Job cancelled successfully');
      queryClient.invalidateQueries('jobs');
      setShowCancelDialog(false);
      setSelectedJob(null);
    },
    onError: (error: any) => {
      toast.error(`Failed to cancel job: ${error.message}`);
    },
  });

  // Download results mutation
  const downloadMutation = useMutation(downloadJobResults, {
    onSuccess: (blob, jobId) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `job-${jobId}-results.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Results downloaded successfully');
    },
    onError: (error: any) => {
      toast.error(`Download failed: ${error.message}`);
    },
  });

  const jobs = jobsData?.jobs || [];

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, job: JobStatus) => {
    setMenuAnchor(event.currentTarget);
    setSelectedJob(job);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedJob(null);
  };

  const handleCancelJob = () => {
    if (selectedJob) {
      setShowCancelDialog(true);
    }
    handleMenuClose();
  };

  const handleDownloadResults = () => {
    if (selectedJob) {
      downloadMutation.mutate(selectedJob.job_id);
    }
    handleMenuClose();
  };

  const handleViewResults = () => {
    if (selectedJob) {
      navigate(`/results/${selectedJob.job_id}`);
    }
    handleMenuClose();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <StartIcon color="primary" />;
      case 'completed': return <DownloadIcon color="success" />;
      case 'failed': return <CancelIcon color="error" />;
      case 'cancelled': return <PauseIcon color="warning" />;
      default: return <StartIcon color="disabled" />;
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

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            Job Manager
          </Typography>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => refetch()}
            disabled={isLoading}
          >
            Refresh
          </Button>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Monitor and manage your AI processing jobs
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="primary">
                {jobs.filter(j => j.status === 'running').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Running Jobs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="success.main">
                {jobs.filter(j => j.status === 'completed').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="error.main">
                {jobs.filter(j => j.status === 'failed').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Failed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography variant="h4">
                {jobs.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Jobs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Jobs Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Job History
          </Typography>

          {isLoading ? (
            <LinearProgress sx={{ mb: 2 }} />
          ) : jobs.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No jobs found
              </Typography>
              <Button
                variant="contained"
                onClick={() => navigate('/upload')}
                sx={{ mt: 2 }}
              >
                Create Your First Job
              </Button>
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Status</TableCell>
                    <TableCell>Workflow</TableCell>
                    <TableCell>Progress</TableCell>
                    <TableCell>Current Step</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.map((job) => (
                    <React.Fragment key={job.job_id}>
                      <TableRow hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {getStatusIcon(job.status)}
                            <Chip
                              label={job.status}
                              color={getStatusColor(job.status) as any}
                              size="small"
                              sx={{ ml: 1 }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {job.workflow_type === 'stage2_automation' ? 'Stage 2 Marketing' : 'RAG Pipeline'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {job.files.length} file(s)
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ width: '100%' }}>
                            <LinearProgress
                              variant="determinate"
                              value={job.progress * 100}
                              sx={{ mb: 1 }}
                            />
                            <Typography variant="caption">
                              {Math.round(job.progress * 100)}% ({job.completed_steps}/{job.total_steps})
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {job.current_step || 'Waiting...'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(job.created_at).toLocaleDateString()}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(job.created_at).toLocaleTimeString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="More actions">
                            <IconButton onClick={(e) => handleMenuOpen(e, job)}>
                              <MoreIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell colSpan={6} sx={{ py: 0, borderBottom: 'none' }}>
                          <JobDetails job={job} onRefresh={refetch} />
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Action Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleViewResults} disabled={!selectedJob || selectedJob.status !== 'completed'}>
          <ListItemIcon><ViewIcon fontSize="small" /></ListItemIcon>
          <ListItemText>View Results</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleDownloadResults} disabled={!selectedJob || selectedJob.status !== 'completed'}>
          <ListItemIcon><DownloadIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Download Results</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={handleCancelJob}
          disabled={!selectedJob || !['pending', 'running'].includes(selectedJob.status)}
        >
          <ListItemIcon><CancelIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Cancel Job</ListItemText>
        </MenuItem>
      </Menu>

      {/* Cancel Confirmation Dialog */}
      <Dialog open={showCancelDialog} onClose={() => setShowCancelDialog(false)}>
        <DialogTitle>Cancel Job</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to cancel this job? This action cannot be undone.
          </Typography>
          {selectedJob && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="body2">
                <strong>Job ID:</strong> {selectedJob.job_id}
              </Typography>
              <Typography variant="body2">
                <strong>Workflow:</strong> {selectedJob.workflow_type}
              </Typography>
              <Typography variant="body2">
                <strong>Progress:</strong> {Math.round(selectedJob.progress * 100)}%
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCancelDialog(false)}>
            Keep Running
          </Button>
          <Button
            onClick={() => selectedJob && cancelJobMutation.mutate(selectedJob.job_id)}
            color="error"
            disabled={cancelJobMutation.isLoading}
          >
            Cancel Job
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default JobManager;