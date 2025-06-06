import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, styled } from '@mui/material';

// Components
import Header from './components/Header';
import ProductSearch from './components/ProductSearch';
import ChatInterface from './components/ChatInterface';
import ManualScreen from './components/ManualScreen';
import AdminPage from './components/AdminPage';

const RootContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  minHeight: '100vh',
  width: '100%',
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)'
    : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
  position: 'relative',
  overflow: 'hidden',
}));

const MainContent = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  width: '100%',
  marginTop: '64px',
  overflowX: 'hidden',
  overflowY: 'auto',
  WebkitOverflowScrolling: 'touch',
  scrollBehavior: 'smooth',
  position: 'relative',
  // Hide scrollbar completely
  '&::-webkit-scrollbar': {
    display: 'none',
  },
  // Firefox
  scrollbarWidth: 'none',
  msOverflowStyle: 'none',
}));

const App: React.FC = () => {
  const [mode, setMode] = useState<'light' | 'dark'>('light');

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: {
            main: mode === 'dark' ? '#667eea' : '#764ba2',
            light: mode === 'dark' ? '#8b94ea' : '#9867c5',
            dark: mode === 'dark' ? '#4c63d2' : '#5a3984',
            contrastText: '#FFFFFF',
          },
          secondary: {
            main: mode === 'dark' ? '#f093fb' : '#4facfe',
            light: mode === 'dark' ? '#f5b7fc' : '#7cc5fe',
            dark: mode === 'dark' ? '#e668f8' : '#2782fe',
          },
          background: {
            default: mode === 'dark' ? '#0a0a0a' : '#f5f7fa',
            paper: mode === 'dark' ? 'rgba(255, 255, 255, 0.03)' : 'rgba(255, 255, 255, 0.95)',
          },
          text: {
            primary: mode === 'dark' ? '#ffffff' : '#1a1a1a',
            secondary: mode === 'dark' ? '#b0b0b0' : '#666666',
          },
          error: {
            main: '#EF4444',
          },
          warning: {
            main: '#F59E0B',
          },
          info: {
            main: '#3B82F6',
          },
          success: {
            main: '#10B981',
          },
        },
        typography: {
          fontFamily: '"Inter", "Segoe UI", "Roboto", "Arial", sans-serif',
          h1: {
            fontWeight: 700,
          },
          h2: {
            fontWeight: 700,
          },
          h3: {
            fontWeight: 600,
          },
          h4: {
            fontWeight: 600,
          },
          h5: {
            fontWeight: 600,
          },
          h6: {
            fontWeight: 600,
          },
        },
        shape: {
          borderRadius: 20,
        },
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: 'none',
                borderRadius: 15,
                fontWeight: 600,
                padding: '12px 24px',
                boxShadow: 'none',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: mode === 'dark' 
                    ? '0 8px 25px rgba(102, 126, 234, 0.4)'
                    : '0 8px 25px rgba(118, 75, 162, 0.4)',
                },
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 20,
                border: mode === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(255, 255, 255, 0.2)',
                backdropFilter: 'blur(10px)',
                background: mode === 'dark' 
                  ? 'linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)'
                  : 'rgba(255, 255, 255, 0.95)',
                boxShadow: mode === 'dark'
                  ? '0 8px 32px rgba(0, 0, 0, 0.3)'
                  : '0 8px 32px rgba(0, 0, 0, 0.1)',
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
                borderRadius: 20,
                backdropFilter: 'blur(10px)',
              },
            },
          },
          MuiDialog: {
            styleOverrides: {
              paper: {
                borderRadius: 25,
                background: mode === 'dark' 
                  ? 'rgba(26, 26, 46, 0.95)'
                  : 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(20px)',
              },
            },
          },
          MuiTextField: {
            styleOverrides: {
              root: {
                '& .MuiOutlinedInput-root': {
                  borderRadius: 15,
                  '& fieldset': {
                    borderColor: mode === 'dark' 
                      ? 'rgba(255, 255, 255, 0.1)' 
                      : 'rgba(0, 0, 0, 0.1)',
                  },
                  '&:hover fieldset': {
                    borderColor: mode === 'dark' ? '#667eea' : '#764ba2',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: mode === 'dark' ? '#667eea' : '#764ba2',
                  },
                },
              },
            },
          },
        },
      }),
    [mode]
  );

  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <RootContainer>
          <Header
            mode={mode}
            toggleColorMode={toggleColorMode}
          />
          <MainContent>
            <Box className="page-transition">
              <Routes>
                <Route path="/" element={<ProductSearch />} />
                <Route path="/chat/:language" element={<ChatInterface mode={mode} toggleColorMode={toggleColorMode} />} />
                <Route path="/category/:categoryId" element={<ManualScreen />} />
                <Route path="/admin" element={<AdminPage />} />
              </Routes>
            </Box>
          </MainContent>
        </RootContainer>
      </Router>
    </ThemeProvider>
  );
};

export default App;
