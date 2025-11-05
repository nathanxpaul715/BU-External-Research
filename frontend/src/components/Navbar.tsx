import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Upload as UploadIcon,
  Work as WorkIcon,
  Search as SearchIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: <DashboardIcon /> },
    { path: '/upload', label: 'Upload Files', icon: <UploadIcon /> },
    { path: '/jobs', label: 'Job Manager', icon: <WorkIcon /> },
    { path: '/query', label: 'RAG Query', icon: <SearchIcon /> },
  ];

  return (
    <AppBar position="static" sx={{ mb: 0 }}>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <AssessmentIcon sx={{ mr: 2 }} />
          <Typography
            variant="h6"
            component="div"
            sx={{ mr: 4, fontWeight: 700 }}
          >
            BU External Research
          </Typography>

          <Box sx={{ display: 'flex', gap: 1 }}>
            {menuItems.map((item) => (
              <Tooltip key={item.path} title={item.label}>
                <Button
                  color="inherit"
                  startIcon={item.icon}
                  onClick={() => navigate(item.path)}
                  sx={{
                    backgroundColor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
                    '&:hover': {
                      backgroundColor: 'rgba(255,255,255,0.1)',
                    },
                  }}
                >
                  {item.label}
                </Button>
              </Tooltip>
            ))}
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            AI-Powered Business Intelligence
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;