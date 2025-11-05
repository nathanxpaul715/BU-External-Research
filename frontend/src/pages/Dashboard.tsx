import React from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  LinearProgress,
  Chip
} from '@mui/material';
import {
  Upload as UploadIcon,
  AutoAwesome as AIIcon,
  Search as SearchIcon,
  Assessment as ChartIcon,
  TrendingUp as TrendingIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// API functions
import { getJobs, getSystemHealth } from '../services/api';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // Fetch recent jobs
  const { data: jobs, isLoading: jobsLoading } = useQuery('recent-jobs', getJobs);
  const { data: health } = useQuery('system-health', getSystemHealth);

  // Mock data for charts
  const activityData = [
    { name: 'Stage 2 Automation', completed: 8, failed: 1 },
    { name: 'RAG Queries', completed: 24, failed: 2 },
    { name: 'Document Processing', completed: 12, failed: 0 },
  ];

  const workflowData = [
    { name: 'Stage 2 Marketing', value: 60, color: '#8884d8' },
    { name: 'RAG Pipeline', value: 35, color: '#82ca9d' },
    { name: 'Other', value: 5, color: '#ffc658' },
  ];

  const recentJobs = jobs?.jobs?.slice(0, 5) || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckIcon color="success" />;
      case 'running': return <SpeedIcon color="primary" />;
      case 'failed': return <CheckIcon color="error" />;
      default: return <SpeedIcon color="disabled" />;
    }
  };

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Monitor your AI research pipelines and business intelligence workflows
        </Typography>
      </Box>

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', cursor: 'pointer', '&:hover': { transform: 'scale(1.02)' } }} onClick={() => navigate('/upload')}>
            <CardContent sx={{ textAlign: 'center', p: 3 }}>
              <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 2, width: 56, height: 56 }}>
                <UploadIcon fontSize="large" />
              </Avatar>
              <Typography variant="h6" gutterBottom>
                Upload Files
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload documents for processing
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', cursor: 'pointer', '&:hover': { transform: 'scale(1.02)' } }} onClick={() => navigate('/jobs')}>
            <CardContent sx={{ textAlign: 'center', p: 3 }}>
              <Avatar sx={{ bgcolor: 'secondary.main', mx: 'auto', mb: 2, width: 56, height: 56 }}>
                <AIIcon fontSize="large" />
              </Avatar>
              <Typography variant="h6" gutterBottom>
                Start Automation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Launch Stage 2 workflows
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', cursor: 'pointer', '&:hover': { transform: 'scale(1.02)' } }} onClick={() => navigate('/query')}>
            <CardContent sx={{ textAlign: 'center', p: 3 }}>
              <Avatar sx={{ bgcolor: 'info.main', mx: 'auto', mb: 2, width: 56, height: 56 }}>
                <SearchIcon fontSize="large" />
              </Avatar>
              <Typography variant="h6" gutterBottom>
                RAG Query
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Search knowledge base
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center', p: 3 }}>
              <Avatar sx={{ bgcolor: 'success.main', mx: 'auto', mb: 2, width: 56, height: 56 }}>
                <ChartIcon fontSize="large" />
              </Avatar>
              <Typography variant="h6" gutterBottom>
                System Health
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {health?.status === 'healthy' ? 'All systems operational' : 'Checking...'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Activity Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Box sx={{ height: 300, mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={activityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="completed" fill="#4caf50" name="Completed" />
                    <Bar dataKey="failed" fill="#f44336" name="Failed" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflow Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Workflow Distribution
              </Typography>
              <Box sx={{ height: 300, mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={workflowData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {workflowData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Jobs */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Recent Jobs
                </Typography>
                <Button variant="outlined" size="small" onClick={() => navigate('/jobs')}>
                  View All
                </Button>
              </Box>

              {jobsLoading ? (
                <LinearProgress />
              ) : recentJobs.length > 0 ? (
                <List dense>
                  {recentJobs.map((job, index) => (
                    <React.Fragment key={job.job_id}>
                      <ListItem>
                        <ListItemAvatar>
                          {getStatusIcon(job.status)}
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="body2">
                                {job.workflow_type === 'stage2_automation' ? 'Stage 2 Marketing' : 'RAG Pipeline'}
                              </Typography>
                              <Chip
                                label={job.status}
                                color={getStatusColor(job.status) as any}
                                size="small"
                                variant="outlined"
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                {new Date(job.created_at).toLocaleString()}
                              </Typography>
                              {job.status === 'running' && (
                                <LinearProgress
                                  variant="determinate"
                                  value={job.progress * 100}
                                  sx={{ mt: 1 }}
                                />
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < recentJobs.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  No recent jobs found
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Stats */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Statistics
              </Typography>

              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2">Total Jobs Processed</Typography>
                  <Typography variant="h6" color="primary">
                    {jobs?.jobs?.length || 0}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2">Success Rate</Typography>
                  <Typography variant="h6" color="success.main">
                    94%
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2">Avg Processing Time</Typography>
                  <Typography variant="h6">
                    12min
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">Documents Indexed</Typography>
                  <Typography variant="h6" color="info.main">
                    1,247
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;