import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  styled,
  Card,
  Button,
  CircularProgress,
  Snackbar,
  Alert,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ManualMetadata } from '../services/api';
import * as apiService from '../services/api';
import { Download as DownloadIcon } from '@mui/icons-material';
import { getFiles, getBrands, getModels, downloadFile } from '../services/api';

const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  marginTop: '24px',
  minHeight: '100vh',
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)'
    : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
  scrollBehavior: 'smooth',
}));

const ManualCard = styled(Card)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: '20px',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)'
    : 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(10px)',
  border: `1px solid ${theme.palette.mode === 'dark' 
    ? 'rgba(255, 255, 255, 0.1)' 
    : 'rgba(255, 255, 255, 0.2)'}`,
  boxShadow: theme.palette.mode === 'dark'
    ? '0 8px 32px rgba(0, 0, 0, 0.3)'
    : '0 8px 32px rgba(0, 0, 0, 0.1)',
  overflow: 'hidden',
  position: 'relative',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '2px',
    background: theme.palette.mode === 'dark'
      ? 'linear-gradient(90deg, #2196F3 30%, #21CBF3 90%)'
      : 'linear-gradient(90deg, #2196F3 30%, #21CBF3 90%)',
    opacity: 0,
    transition: 'opacity 0.3s ease',
  },
  '&:hover': {
    transform: 'translateY(-8px) scale(1.02)',
    boxShadow: theme.palette.mode === 'dark'
      ? '0 20px 40px rgba(33, 150, 243, 0.3)'
      : '0 20px 40px rgba(33, 203, 243, 0.2)',
    '&::before': {
      opacity: 1,
    },
  },
}));

const LoadingContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '50vh',
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)'
    : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
  borderRadius: '20px',
  margin: theme.spacing(2),
  '& .MuiCircularProgress-root': {
    color: theme.palette.mode === 'dark' 
      ? '#21CBF3' 
      : '#2196F3',
  },
}));

const ManualScreen: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { categoryId } = useParams<{ categoryId: string }>();
  const [manuals, setManuals] = useState<ManualMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Get the selected language from location state or i18n
  const selectedLanguage = location.state?.selectedLanguage || i18n.language;

  useEffect(() => {
    const loadManualsFromAPI = async () => {
      try {
        setLoading(true);
        
        // Fetch all uploaded files from the API
        const files = await apiService.getFiles();
        console.log('Fetched files from API:', files);
        console.log('Current categoryId:', categoryId);
        console.log('Current language:', selectedLanguage);
        
        // Filter files based on category and language
        let filteredManuals: ManualMetadata[] = [];
        
        if (categoryId === 'home_appliances') {
          console.log('Filtering for home_appliances...');
          console.log('All files from API:', files);
          
          // Filter for home appliances - be more inclusive
          filteredManuals = files
            .filter(file => {
              const productType = file.product_type?.toLowerCase() || '';
              console.log(`File: ${file.name}, product_type: "${file.product_type}", productType: "${productType}"`);
              
              // Check multiple criteria for home appliances
              const matches = productType.includes('washing') || 
                     productType.includes('dryer') || 
                     productType.includes('home appliance') ||
                     productType.includes('appliance') ||
                     productType.includes('machine') ||
                     // If no product_type field, include it (backend hasn't been restarted)
                     !file.product_type;
                     
              console.log(`File ${file.name} matches home_appliances: ${matches}`);
              return matches;
            })
            .map(file => ({
              brand: file.brand || 'Unknown',
              model: file.model || 'Unknown', 
              product_type: file.product_type || 'Home Appliance',
              year: file.year?.toString() || '2023',
              language: file.language || 'en',
              file_id: file.file_id,
              filename: file.name
            }));
          
          console.log('Filtered manuals for home_appliances:', filteredManuals);
          
          // If no matches found, show demo data
          if (filteredManuals.length === 0) {
            console.log('No real manuals found, showing demo data for home_appliances...');
            filteredManuals = [
              {
                brand: 'Samsung',
                model: 'WA50F9A8DSP',
                product_type: 'Washing Machine',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'LG',
                model: 'DLEX3900W',
                product_type: 'Dryer',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'Whirlpool',
                model: 'WTW8127LC',
                product_type: 'Washing Machine',
                year: '2023',
                language: 'en',
                isDemoData: true
              }
            ];
          }
        } else if (categoryId === 'kitchen_appliances') {
          // Filter for kitchen appliances
          filteredManuals = files
            .filter(file => {
              const productType = file.product_type?.toLowerCase() || '';
              return productType.includes('kitchen') || 
                     productType.includes('oven') || 
                     productType.includes('microwave') ||
                     productType.includes('dishwasher') ||
                     productType.includes('refrigerator');
            })
            .map(file => ({
              brand: file.brand || 'Unknown',
              model: file.model || 'Unknown',
              product_type: file.product_type || 'Kitchen Appliance',
              year: file.year?.toString() || '2023',
              language: file.language || 'en',
              file_id: file.file_id,
              filename: file.name
            }));
          
          // If no matches found, show demo data
          if (filteredManuals.length === 0) {
            filteredManuals = [
              {
                brand: 'Samsung',
                model: 'RF23M8070SR',
                product_type: 'Refrigerator',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'KitchenAid',
                model: 'KODE507ESS',
                product_type: 'Oven',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'Bosch',
                model: 'SHPM65Z55N',
                product_type: 'Dishwasher',
                year: '2023',
                language: 'en',
                isDemoData: true
              }
            ];
          }
        } else if (categoryId === 'tv_video') {
          // Filter for TV and video devices
          filteredManuals = files
            .filter(file => {
              const productType = file.product_type?.toLowerCase() || '';
              return productType.includes('tv') || 
                     productType.includes('television') || 
                     productType.includes('video');
            })
            .map(file => ({
              brand: file.brand || 'Unknown',
              model: file.model || 'Unknown',
              product_type: file.product_type || 'Television',
              year: file.year?.toString() || '2023',
              language: file.language || 'en',
              file_id: file.file_id,
              filename: file.name
            }));
          
          // If no matches found, show demo data
          if (filteredManuals.length === 0) {
            filteredManuals = [
              {
                brand: 'Samsung',
                model: 'QN65Q70AAFXZA',
                product_type: 'Smart TV',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'LG',
                model: 'OLED55C1PUB',
                product_type: 'OLED TV',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'Sony',
                model: 'XBR65X90J',
                product_type: 'Smart TV',
                year: '2023',
                language: 'en',
                isDemoData: true
              }
            ];
          }
        } else if (categoryId === 'audio') {
          // Filter for audio devices
          filteredManuals = files
            .filter(file => {
              const productType = file.product_type?.toLowerCase() || '';
              return productType.includes('audio') || 
                     productType.includes('speaker') || 
                     productType.includes('sound');
            })
            .map(file => ({
              brand: file.brand || 'Unknown',
              model: file.model || 'Unknown',
              product_type: file.product_type || 'Audio System',
              year: file.year?.toString() || '2023',
              language: file.language || 'en',
              file_id: file.file_id,
              filename: file.name
            }));
          
          // If no matches found, show demo data
          if (filteredManuals.length === 0) {
            filteredManuals = [
              {
                brand: 'Sonos',
                model: 'Arc',
                product_type: 'Soundbar',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'Bose',
                model: 'SoundLink Revolve',
                product_type: 'Bluetooth Speaker',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'JBL',
                model: 'Charge 5',
                product_type: 'Portable Speaker',
                year: '2023',
                language: 'en',
                isDemoData: true
              }
            ];
          }
        } else if (categoryId === 'climate') {
          // Filter for climate control devices
          filteredManuals = files
            .filter(file => {
              const productType = file.product_type?.toLowerCase() || '';
              return productType.includes('air conditioner') || 
                     productType.includes('climate') || 
                     productType.includes('hvac') ||
                     productType.includes('heating') ||
                     productType.includes('cooling');
            })
            .map(file => ({
              brand: file.brand || 'Unknown',
              model: file.model || 'Unknown',
              product_type: file.product_type || 'Air Conditioner',
              year: file.year?.toString() || '2023',
              language: file.language || 'en',
              file_id: file.file_id,
              filename: file.name
            }));
          
          // If no matches found, show demo data
          if (filteredManuals.length === 0) {
            filteredManuals = [
              {
                brand: 'Daikin',
                model: 'DX18TC',
                product_type: 'Air Conditioner',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'Carrier',
                model: '24ACC636A003',
                product_type: 'Central AC',
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'Nest',
                model: 'T3017US',
                product_type: 'Smart Thermostat',
                year: '2023',
                language: 'en',
                isDemoData: true
              }
            ];
          }
        } else {
          // For other categories, show all electronics or create demo data
          filteredManuals = files
            .filter(file => {
              const productType = file.product_type?.toLowerCase() || '';
              return productType.includes('electronic') || 
                     productType.includes(categoryId?.replace(/_/g, ' ') || '');
            })
            .map(file => ({
              brand: file.brand || 'Unknown',
              model: file.model || 'Unknown',
              product_type: file.product_type || categoryId?.replace(/_/g, ' ') || 'Electronics',
              year: file.year?.toString() || '2023',
              language: file.language || 'en',
              file_id: file.file_id,
              filename: file.name
            }));
          
          // If no files match, create demo data based on category
          if (filteredManuals.length === 0) {
            const categoryName = categoryId?.replace(/_/g, ' ') || 'Electronics';
            filteredManuals = [
              {
                brand: 'Samsung',
                model: 'Demo-Model-1',
                product_type: categoryName,
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'LG',
                model: 'Demo-Model-2',
                product_type: categoryName,
                year: '2023',
                language: 'en',
                isDemoData: true
              },
              {
                brand: 'Sony',
                model: 'Demo-Model-3',
                product_type: categoryName,
                year: '2023',
                language: 'en',
                isDemoData: true
              }
            ];
          }
        }

        // Sort the manuals
        filteredManuals.sort((a, b) => {
          const modelA = a.model || '';
          const modelB = b.model || '';
          const typeA = a.product_type || '';
          const typeB = b.product_type || '';
          
          if (typeA === typeB) {
            return modelA.localeCompare(modelB);
          }
          return typeA.localeCompare(typeB);
        });
        
        console.log(`Final filtered manuals for category ${categoryId}:`, filteredManuals);

        // Update the language of demo data to match selected language
        filteredManuals = filteredManuals.map(manual => ({
          ...manual,
          language: manual.isDemoData ? selectedLanguage : (manual.language || selectedLanguage)
        }));

        setManuals(filteredManuals);
        
      } catch (error) {
        console.error('Failed to load manuals from API:', error);
        setError('Failed to load manuals. Please try again.');
        setManuals([]); // Set empty array on error
      } finally {
        setLoading(false);
      }
    };

    loadManualsFromAPI();
  }, [categoryId, selectedLanguage]); // Add selectedLanguage to dependencies

  const handleManualSelect = async (manual: ManualMetadata) => {
    try {
      console.log('=== handleManualSelect called ===');
      console.log('Manual data:', manual);
      console.log('Manual has file_id:', !!manual.file_id);
      console.log('Manual is demo data:', !!manual.isDemoData);
      console.log('Selected language:', selectedLanguage);
      
      // Check if this is demo data
      if (manual.isDemoData) {
        console.log('Demo data selected - showing message...');
        setError(`This is demo data for ${manual.brand} ${manual.model}. Real device manuals are available through our comprehensive database.`);
        return;
      }
      
      // Handle real uploaded files with file_id
      if (manual.file_id) {
        console.log('Navigating to chat for uploaded file...');
        // Use the selected language for navigation
        console.log('Using language:', selectedLanguage);
        console.log('Navigation path:', `/chat/${selectedLanguage}`);
        
        // Navigate to chat interface with the selected language
        navigate(`/chat/${selectedLanguage}`, {
          state: {
            manual: {
              ...manual,
              brand: manual.brand || 'Unknown',
              model: manual.model || 'Unknown',
              language: selectedLanguage, // Set the selected language
              cached: true
            },
            categoryId: categoryId
          }
        });
        return;
      }
      
      // If no file_id and not demo data, show error
      setError('This manual is currently unavailable. Please contact support for assistance.');

    } catch (error) {
      console.error('Error selecting manual:', error);
      setError('Failed to process manual selection.');
    }
  };

  const handleCloseError = () => {
    setError(null);
  };

  if (loading) {
    return (
      <LoadingContainer>
        <CircularProgress />
      </LoadingContainer>
    );
  }

  return (
    <PageContainer>
      <Container maxWidth="lg">
        <Box sx={{ 
          textAlign: 'center', 
          mb: 4,
          p: 3,
          borderRadius: '20px',
          background: theme => theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.03)'
            : 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(10px)',
        }}>
          <Typography 
            variant="h3" 
            gutterBottom
            sx={{
              background: theme => theme.palette.mode === 'dark'
                ? 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)'
                : 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 'bold',
              mb: 2,
            }}
          >
            {t(`categories.${categoryId}`)}
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: theme => theme.palette.mode === 'dark' ? '#b0b0b0' : '#666666',
              fontWeight: 300,
            }}
          >
            {t(`categories.${categoryId}_desc`)}
          </Typography>
        </Box>

        {manuals.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {t('manualScreen.noManuals.title')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('manualScreen.noManuals.subtitle')}
            </Typography>
          </Box>
        ) : (
          <Box 
            sx={{ 
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(auto-fit, minmax(300px, 1fr))',
                md: 'repeat(auto-fit, minmax(280px, 1fr))',
                lg: 'repeat(auto-fit, minmax(300px, 1fr))'
              },
              gap: { xs: 2, sm: 3, md: 4 },
              mt: 4,
              mb: 4,
              px: { xs: 1, sm: 2 },
            }}
          >
            {manuals.map((manual, index) => (
              <ManualCard key={`${manual.file_id || index}`}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography variant="h6" gutterBottom>
                    {manual.brand} {manual.model}
                  </Typography>
                  {manual.isDemoData && (
                    <Chip 
                      label={t('manualScreen.details.demo')}
                      size="small" 
                      sx={{ 
                        backgroundColor: '#FF9800',
                        color: 'white',
                        fontWeight: 500,
                        mt: 1
                      }} 
                    />
                  )}
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {manual.product_type}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {t('manualScreen.details.year')}: {manual.year}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {t('manualScreen.details.language')}: {manual.language?.toUpperCase()}
                </Typography>
                {manual.isDemoData && (
                  <Typography 
                    variant="caption" 
                    color="text.secondary" 
                    sx={{ mt: 1, display: 'block' }}
                  >
                    {t('manualScreen.details.demoText')}
                  </Typography>
                )}
                <Box sx={{ flexGrow: 1 }} />
                
                {/* Action buttons container */}
                <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                  {/* Main Chat Button */}
                  <Button
                    variant="contained"
                    fullWidth
                    sx={{ 
                      borderRadius: '15px',
                      height: '48px',
                      background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                      color: '#ffffff',
                      fontWeight: 'bold',
                      fontSize: '1rem',
                      textTransform: 'none',
                      boxShadow: '0 4px 15px rgba(33, 150, 243, 0.4)',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #1976d2 30%, #1e88e5 90%)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 25px rgba(33, 150, 243, 0.6)',
                      },
                    }}
                    onClick={() => handleManualSelect(manual)}
                  >
                    {manual.isDemoData ? t('productDetails.demoButton') : t('productDetails.chatButton')}
                  </Button>
                  
                  {/* Download PDF Button */}
                  <Tooltip title={manual.isDemoData ? "Demo data - no PDF available" : "Download PDF Manual"}>
                    <span>
                      <IconButton
                        disabled={manual.isDemoData}
                        sx={{
                          width: '48px',
                          height: '48px',
                          borderRadius: '15px',
                          background: 'linear-gradient(45deg, #9C27B0 30%, #BA68C8 90%)',
                          color: '#ffffff',
                          boxShadow: '0 4px 15px rgba(156, 39, 176, 0.4)',
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          '&:hover': {
                            background: 'linear-gradient(45deg, #7B1FA2 30%, #9C27B0 90%)',
                            transform: manual.isDemoData ? 'none' : 'translateY(-2px)',
                            boxShadow: manual.isDemoData 
                              ? '0 4px 15px rgba(156, 39, 176, 0.4)'
                              : '0 8px 25px rgba(156, 39, 176, 0.6)',
                          },
                          '&.Mui-disabled': {
                            background: 'linear-gradient(45deg, #9E9E9E 30%, #BDBDBD 90%)',
                            color: 'rgba(255, 255, 255, 0.5)',
                          },
                        }}
                        onClick={() => {
                          if (!manual.isDemoData) {
                            // Download uploaded file using the centralized API function
                            const handleDownload = async () => {
                              try {
                                const filename = manual.filename || manual.model || 'manual';
                                const blob = await downloadFile(filename);
                                
                                // Create download link
                                const url = window.URL.createObjectURL(blob);
                                const link = document.createElement('a');
                                link.href = url;
                                link.download = filename.endsWith('.pdf') ? filename : `${filename}.pdf`;
                                document.body.appendChild(link);
                                link.click();
                                
                                // Cleanup
                                window.URL.revokeObjectURL(url);
                                document.body.removeChild(link);
                                
                              } catch (error) {
                                console.error('Download error:', error);
                                setError(error instanceof Error ? error.message : 'Failed to download file. Please try again.');
                              }
                            };
                            
                            handleDownload();
                          }
                        }}
                      >
                        <DownloadIcon />
                      </IconButton>
                    </span>
                  </Tooltip>
                </Box>
              </ManualCard>
            ))}
          </Box>
        )}
      </Container>
      
      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={handleCloseError}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseError} 
          severity="error" 
          sx={{ 
            width: '100%',
            borderRadius: '15px',
            backdropFilter: 'blur(10px)',
            background: theme => theme.palette.mode === 'dark' 
              ? 'rgba(244, 67, 54, 0.15)' 
              : 'rgba(244, 67, 54, 0.1)',
            border: '1px solid rgba(244, 67, 54, 0.3)',
            color: theme => theme.palette.mode === 'dark' ? '#ff6b6b' : '#d32f2f',
            '& .MuiAlert-icon': {
              color: theme => theme.palette.mode === 'dark' ? '#ff6b6b' : '#d32f2f',
            },
          }}
        >
          {error}
        </Alert>
      </Snackbar>
    </PageContainer>
  );
};

export default ManualScreen; 