import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  IconButton,
  Tooltip,
  Badge,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  ContentCopy as CopyIcon,
  History as HistoryIcon,
  Clear as ClearIcon,
  Settings as SettingsIcon,
  Source as SourceIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { useMutation } from 'react-query';
import { toast } from 'react-toastify';

// Services
import { submitRAGQuery, RAGQuery, RAGResponse } from '../services/api';

interface QueryResult {
  id: string;
  query: string;
  response: RAGResponse;
  timestamp: Date;
}

const RAGQueryPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [queryHistory, setQueryHistory] = useState<QueryResult[]>([]);
  const [currentResult, setCurrentResult] = useState<QueryResult | null>(null);
  const [maxResults, setMaxResults] = useState(10);
  const [includeSources, setIncludeSources] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  // RAG query mutation
  const queryMutation = useMutation(submitRAGQuery, {
    onSuccess: (response: RAGResponse) => {
      const result: QueryResult = {
        id: response.query_id,
        query: query,
        response: response,
        timestamp: new Date()
      };

      setCurrentResult(result);
      setQueryHistory(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 queries
      toast.success('Query processed successfully');
    },
    onError: (error: any) => {
      toast.error(`Query failed: ${error.message}`);
    },
  });

  const handleSubmitQuery = () => {
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }

    const queryRequest: RAGQuery = {
      query: query.trim(),
      max_results: maxResults,
      include_sources: includeSources
    };

    queryMutation.mutate(queryRequest);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && event.ctrlKey) {
      handleSubmitQuery();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const loadHistoryQuery = (historyResult: QueryResult) => {
    setQuery(historyResult.query);
    setCurrentResult(historyResult);
  };

  const clearHistory = () => {
    setQueryHistory([]);
    toast.info('Query history cleared');
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          RAG Knowledge Search
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Search through your indexed documents using advanced AI retrieval
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Query Input Section */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Search Query
                </Typography>
                <IconButton onClick={() => setShowSettings(!showSettings)}>
                  <SettingsIcon />
                </IconButton>
              </Box>

              {/* Settings Panel */}
              {showSettings && (
                <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Search Settings
                  </Typography>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={6}>
                      <TextField
                        label="Max Results"
                        type="number"
                        value={maxResults}
                        onChange={(e) => setMaxResults(parseInt(e.target.value) || 10)}
                        inputProps={{ min: 1, max: 50 }}
                        size="small"
                        fullWidth
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={includeSources}
                            onChange={(e) => setIncludeSources(e.target.checked)}
                          />
                        }
                        label="Include Sources"
                      />
                    </Grid>
                  </Grid>
                </Paper>
              )}

              <TextField
                fullWidth
                multiline
                rows={4}
                variant="outlined"
                placeholder="Enter your question about the indexed documents..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                sx={{ mb: 2 }}
                helperText="Press Ctrl+Enter to search, or use the search button"
              />

              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={queryMutation.isLoading ? <CircularProgress size={20} /> : <SearchIcon />}
                  onClick={handleSubmitQuery}
                  disabled={queryMutation.isLoading || !query.trim()}
                  size="large"
                >
                  {queryMutation.isLoading ? 'Searching...' : 'Search'}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ClearIcon />}
                  onClick={() => setQuery('')}
                  disabled={!query}
                >
                  Clear
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Current Result */}
          {currentResult && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Search Results
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Chip
                      icon={<SpeedIcon />}
                      label={`${currentResult.response.processing_time.toFixed(2)}s`}
                      size="small"
                      color="primary"
                    />
                    <Chip
                      icon={<SourceIcon />}
                      label={`${currentResult.response.sources.length} sources`}
                      size="small"
                      color="info"
                    />
                    <Tooltip title="Copy answer">
                      <IconButton
                        size="small"
                        onClick={() => copyToClipboard(currentResult.response.answer)}
                      >
                        <CopyIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>

                {/* Query */}
                <Paper sx={{ p: 2, mb: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    Query: {currentResult.query}
                  </Typography>
                </Paper>

                {/* Answer */}
                <Paper sx={{ p: 3, mb: 3, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
                    {currentResult.response.answer}
                  </Typography>
                </Paper>

                {/* Sources */}
                {currentResult.response.sources.length > 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                      <SourceIcon sx={{ mr: 1 }} />
                      Sources ({currentResult.response.sources.length})
                    </Typography>

                    {currentResult.response.sources.map((source, index) => (
                      <Accordion key={index} sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {source.document}
                            </Typography>
                            {source.page && (
                              <Chip label={`Page ${source.page}`} size="small" variant="outlined" />
                            )}
                            <Chip
                              label={`${(source.relevance_score * 100).toFixed(0)}%`}
                              size="small"
                              color={getRelevanceColor(source.relevance_score) as any}
                            />
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                            <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                              {source.snippet}
                            </Typography>
                          </Paper>
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Query History */}
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                  <HistoryIcon sx={{ mr: 1 }} />
                  Recent Queries
                  {queryHistory.length > 0 && (
                    <Badge badgeContent={queryHistory.length} color="primary" sx={{ ml: 1 }} />
                  )}
                </Typography>
                {queryHistory.length > 0 && (
                  <Button size="small" onClick={clearHistory} startIcon={<ClearIcon />}>
                    Clear
                  </Button>
                )}
              </Box>

              {queryHistory.length === 0 ? (
                <Alert severity="info">
                  Your query history will appear here
                </Alert>
              ) : (
                <List dense>
                  {queryHistory.map((historyItem, index) => (
                    <React.Fragment key={historyItem.id}>
                      <ListItem
                        button
                        onClick={() => loadHistoryQuery(historyItem)}
                        sx={{
                          borderRadius: 1,
                          mb: 1,
                          '&:hover': { bgcolor: 'action.hover' }
                        }}
                      >
                        <ListItemText
                          primary={
                            <Typography variant="body2" noWrap>
                              {historyItem.query}
                            </Typography>
                          }
                          secondary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="caption">
                                {historyItem.timestamp.toLocaleTimeString()}
                              </Typography>
                              <Chip
                                label={`${historyItem.response.sources.length} sources`}
                                size="small"
                                variant="outlined"
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < queryHistory.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>

          {/* Search Tips */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <AssessmentIcon sx={{ mr: 1 }} />
                Search Tips
              </Typography>

              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Be Specific"
                    secondary="Include specific terms, numbers, or concepts"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Ask Questions"
                    secondary="Use natural language questions"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Context Matters"
                    secondary="Provide context for better results"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Use Keywords"
                    secondary="Include domain-specific terminology"
                  />
                </ListItem>
              </List>

              <Alert severity="info" sx={{ mt: 2 }}>
                The system searches through all indexed documents and returns the most relevant information based on semantic similarity.
              </Alert>
            </CardContent>
          </Card>

          {/* Example Queries */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Example Queries
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {[
                  "What are the key marketing strategies mentioned?",
                  "How is AI being used in business processes?",
                  "What are the main competitive advantages?",
                  "Tell me about implementation challenges"
                ].map((example, index) => (
                  <Button
                    key={index}
                    variant="outlined"
                    size="small"
                    onClick={() => setQuery(example)}
                    sx={{ textAlign: 'left', justifyContent: 'flex-start' }}
                  >
                    {example}
                  </Button>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default RAGQueryPage;