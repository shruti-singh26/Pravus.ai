import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Button,
  useTheme,
  styled,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  ArrowBack as ArrowBackIcon,
  Language as LanguageIcon,
  Check as CheckIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation } from 'react-router-dom';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#202123' : '#ffffff',
  borderBottom: `1px solid ${theme.palette.mode === 'dark' ? '#2f2f2f' : '#e0e0e0'}`,
  boxShadow: 'none',
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  zIndex: theme.zIndex.appBar
}));

const StyledToolbar = styled(Toolbar)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: theme.spacing(0, 2),
  [theme.breakpoints.up('sm')]: {
    padding: theme.spacing(0, 3),
  }
}));

const HeaderActions = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  [theme.breakpoints.up('sm')]: {
    gap: theme.spacing(2),
  }
}));

const Logo = styled(Typography)(({ theme }) => ({
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)'
    : 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  fontWeight: 700,
  letterSpacing: '0.5px',
  cursor: 'pointer',
}));

interface HeaderProps {
  mode: 'light' | 'dark';
  toggleColorMode: () => void;
  onBackClick?: () => void;
  hideLanguageSelector?: boolean;
}

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'es', label: 'Español' },
  { code: 'hi', label: 'हिंदी' },
  { code: 'pl', label: 'Polski' }
];

const Header: React.FC<HeaderProps> = ({
  mode,
  toggleColorMode,
  onBackClick,
  hideLanguageSelector = false
}) => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [languageMenu, setLanguageMenu] = useState<null | HTMLElement>(null);

  const showBackButton = location.pathname !== '/';

  const handleBack = () => {
    if (onBackClick) {
      onBackClick();
    } else {
      // Smart back navigation based on current path
      if (location.pathname.startsWith('/chat/')) {
        // From chat, don't use navigate(-1) as it's unreliable
        // Let the ChatInterface handle its own back navigation
        navigate(-1);
      } else if (location.pathname.startsWith('/category/')) {
        // From category pages, go back to home
        navigate('/');
      } else {
        // Default behavior
        navigate(-1);
      }
    }
  };

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleLanguageMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setLanguageMenu(event.currentTarget);
  };

  const handleLanguageMenuClose = () => {
    setLanguageMenu(null);
  };

  const handleLanguageSelect = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
    handleLanguageMenuClose();
  };

  return (
    <StyledAppBar>
      <StyledToolbar>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {showBackButton && (
            <Tooltip title={t('navigation.back')}>
              <IconButton
                edge="start"
                color="inherit"
                onClick={handleBack}
                sx={{ mr: 2 }}
              >
                <ArrowBackIcon sx={{ color: theme.palette.mode === 'dark' ? 'white' : '#2565AE' }}/>
              </IconButton>
            </Tooltip>
          )}
          <Logo variant="h5" onClick={handleLogoClick}>
            Pravus.AI
          </Logo>
        </Box>

        <HeaderActions>
          {!hideLanguageSelector && (
            <>
              <Button
                startIcon={<LanguageIcon />}
                onClick={handleLanguageMenuOpen}
                sx={{
                  textTransform: 'none',
                  display: { xs: 'none', sm: 'flex' },
                  color: theme.palette.mode === 'dark' ? 'white' : '#2565AE'
                }}
              >
                {t('language')}
              </Button>
              
              <Menu
                anchorEl={languageMenu}
                open={Boolean(languageMenu)}
                onClose={handleLanguageMenuClose}
                PaperProps={{
                  sx: {
                    mt: 1.5,
                    minWidth: 180,
                    backgroundColor: theme.palette.mode === 'dark' ? '#2f2f2f' : '#ffffff',
                  }
                }}
              >
                {LANGUAGES.map((language) => (
                  <MenuItem
                    key={language.code}
                    onClick={() => handleLanguageSelect(language.code)}
                    sx={{
                      py: 1,
                      px: 2,
                    }}
                  >
                    <ListItemText>{language.label}</ListItemText>
                    {i18n.language === language.code && (
                      <ListItemIcon sx={{ minWidth: 'auto', ml: 1 }}>
                        <CheckIcon  />
                      </ListItemIcon>
                    )}
                  </MenuItem>
                ))}
              </Menu>
            </>
          )}
          
          <Tooltip title={mode === 'dark' ? t('lightMode') : t('darkMode')}>
            <IconButton onClick={toggleColorMode} color="inherit">
              {mode === 'dark' ? <LightModeIcon sx={{ color: 'white' }} /> : <DarkModeIcon sx={{ color: '#2565AE' }} />}
            </IconButton>
          </Tooltip>
        </HeaderActions>
      </StyledToolbar>
    </StyledAppBar>
  );
};

export default Header; 