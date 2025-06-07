import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  MenuItem,
  Alert,
  CircularProgress,
  Paper,
  Chip,
  LinearProgress,
  styled,
  useTheme,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  Tooltip,
  Snackbar
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  AdminPanelSettings as AdminIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Storage as StorageIcon
} from '@mui/icons-material';
import { uploadFile, FileUploadResponse, getFiles, deleteFile, FileData, downloadFile } from '../services/api';
import { useTranslation } from 'react-i18next';

const StyledCard = styled(Card)(({ theme }) => ({
  maxWidth: 1200,
  margin: '0 auto',
  marginTop: theme.spacing(4),
  marginBottom: theme.spacing(4),
  borderRadius: 25,
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(145deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%)'
    : 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(20px)',
  border: theme.palette.mode === 'dark' 
    ? '1px solid rgba(255, 255, 255, 0.1)' 
    : '1px solid rgba(255, 255, 255, 0.2)',
  boxShadow: theme.palette.mode === 'dark'
    ? '0 20px 40px rgba(0, 0, 0, 0.4)'
    : '0 20px 40px rgba(0, 0, 0, 0.1)',
}));

const UploadArea = styled(Paper)<{ isDragOver: boolean }>(({ theme, isDragOver }) => ({
  border: `2px dashed ${isDragOver ? theme.palette.primary.main : theme.palette.divider}`,
  borderRadius: 20,
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  background: isDragOver 
    ? (theme.palette.mode === 'dark' ? 'rgba(102, 126, 234, 0.1)' : 'rgba(118, 75, 162, 0.05)')
    : 'transparent',
  '&:hover': {
    borderColor: theme.palette.primary.main,
    background: theme.palette.mode === 'dark' ? 'rgba(102, 126, 234, 0.05)' : 'rgba(118, 75, 162, 0.05)',
  },
}));

interface FormData {
  brand: string;
  model: string;
  product_type: string;
  year: string;
  language: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AdminPage: React.FC = () => {
  const theme = useTheme();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { t } = useTranslation();
  
  // Form state
  const [formData, setFormData] = useState<FormData>({
    brand: 'Samsung',
    model: '',
    product_type: '',
    year: new Date().getFullYear().toString(),
    language: 'en'
  });
  
  // Upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // Admin state
  const [currentTab, setCurrentTab] = useState(0);
  const [manuals, setManuals] = useState<FileData[]>([]);
  const [loading, setLoading] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    manual: FileData | null;
    isDeleting: boolean;
  }>({ open: false, manual: null, isDeleting: false });
  const [deletingItems, setDeletingItems] = useState<Set<string>>(new Set());
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info';
  }>({ open: false, message: '', severity: 'info' });

  // Product type options
  const productTypes = [
    'Washing Machine',
    'Dryer',
    'Refrigerator',
    'Dishwasher',
    'Oven',
    'Microwave',
    'Air Conditioner',
    'Television',
    'Audio System',
    'Kitchen Appliance',
    'Home Appliance',
    'Electronics',
    'Other'
  ];

  // Language options
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'hi', name: 'Hindi' },
    { code: 'pl', name: 'Polish' }
  ];

  // Load manuals on component mount and tab change
  useEffect(() => {
    // Load manuals on component mount for duplicate filename validation
    loadManuals();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Reload manuals when switching to manage tab
  useEffect(() => {
    if (currentTab === 1) {
      loadManuals();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentTab]);

  const loadManuals = async () => {
    setLoading(true);
    
    // Set a timeout to prevent indefinite loading
    const loadingTimeout = setTimeout(() => {
      if (loading) {
        console.warn('Loading manuals timed out, setting empty state');
        setManuals([]);
        setLoading(false);
        showNotification(t('admin.loadingTimeout'), 'info');
      }
    }, 15000); // 15 second timeout
    
    try {
      const files = await getFiles();
      clearTimeout(loadingTimeout); // Clear timeout if request succeeds
      setManuals(files);
      
      // If no manuals found, show info message instead of error
      if (files.length === 0) {
        console.log('No manuals found in the system');
      }
    } catch (error) {
      clearTimeout(loadingTimeout); // Clear timeout if request fails
      console.error('Failed to load manuals:', error);
      
      // Provide more specific error messages based on the error type
      let errorMessage = t('admin.failedToLoadManuals');
      if (error instanceof Error) {
        if (error.message.includes('timeout')) {
          errorMessage = t('admin.requestTimedOut');
        } else if (error.message.includes('network') || error.message.includes('ECONNREFUSED')) {
          errorMessage = t('admin.cannotConnect');
        } else {
          errorMessage = `${t('admin.failedToLoadManuals')}: ${error.message}`;
        }
      }
      
      showNotification(errorMessage, 'error');
      
      // Set empty manuals array so the UI shows "no manuals" instead of hanging
      setManuals([]);
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message: string, severity: 'success' | 'error' | 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleInputChange = (field: keyof FormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleFileSelect = (file: File) => {
    const allowedTypes = ['.pdf', '.txt', '.doc', '.docx'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(fileExtension)) {
      setUploadResult({
        type: 'error',
        message: `${t('admin.unsupportedFileType')} ${allowedTypes.join(', ')}`
      });
      return;
    }

    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
      setUploadResult({
        type: 'error',
        message: t('admin.fileSizeExceedsLimit')
      });
      return;
    }

    // Check for duplicate filename in existing manuals
    const duplicateManual = manuals.find(manual => manual.name === file.name);
    if (duplicateManual) {
      const uploadDate = new Date(duplicateManual.timestamp).toLocaleDateString();
      setUploadResult({
        type: 'error',
        message: `${t('admin.fileAlreadyExists')}
${t('admin.existingFileDetails')}
• ${t('admin.brand')}: ${duplicateManual.brand || t('admin.unknown')}
• ${t('admin.model')}: ${duplicateManual.model || t('admin.unknown')}
• ${t('admin.uploadDate')}: ${uploadDate}

${t('admin.pleaseRenameOrDeleteExisting')}
`
      });
      return;
    }

    setSelectedFile(file);
    setUploadResult(null);
  };

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const file = event.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadResult({
        type: 'error',
        message: t('admin.pleaseSelectFile')
      });
      return;
    }

    // Validate required fields
    if (!formData.brand.trim() || !formData.model.trim()) {
      setUploadResult({
        type: 'error',
        message: t('admin.brandAndModelRequired')
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setUploadResult(null);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response: FileUploadResponse = await uploadFile(selectedFile, {
        brand: formData.brand.trim(),
        model: formData.model.trim(),
        product_type: formData.product_type.trim() || 'Unknown',
        year: formData.year.trim() || new Date().getFullYear().toString(),
        language: formData.language
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      setUploadResult({
        type: 'success',
        message: `${t('admin.successfullyUploaded')} ${response.filename}`
      });

      // Auto-dismiss success notification after 4 seconds
      setTimeout(() => {
        setUploadResult(null);
      }, 4000);

      // Reset form
      setSelectedFile(null);
      setFormData({
        brand: 'Samsung',
        model: '',
        product_type: '',
        year: new Date().getFullYear().toString(),
        language: 'en'
      });

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Refresh manuals if on that tab
      if (currentTab === 1) {
        loadManuals();
      }

    } catch (error: any) {
      setUploadResult({
        type: 'error',
        message: error.message || t('admin.uploadFailed')
      });
    } finally {
      setIsUploading(false);
      setTimeout(() => {
        setUploadProgress(0);
      }, 2000);
    }
  };

  const handleDeleteClick = (manual: FileData) => {
    setDeleteDialog({ open: true, manual, isDeleting: false });
  };

  const handleDeleteConfirm = async () => {
    if (!deleteDialog.manual?.file_id) return;

    const manualToDelete = deleteDialog.manual;
    const manualId = manualToDelete.file_id || manualToDelete.name;
    
    // Ensure we have a valid file_id
    if (!manualToDelete.file_id) {
      showNotification(t('admin.cannotDeleteInvalidFileId'), 'error');
      setDeleteDialog({ open: false, manual: null, isDeleting: false });
      return;
    }

    try {
      // Immediate UI feedback - show deleting state
      setDeleteDialog(prev => ({ ...prev, isDeleting: true }));
      setDeletingItems(prev => new Set(prev).add(manualId));
      
      // Optimistically remove from UI immediately
      setManuals(prevManuals => prevManuals.filter(m => 
        (m.file_id || m.name) !== manualId
      ));
      
      // Close dialog immediately for better UX
      setDeleteDialog({ open: false, manual: null, isDeleting: false });
      
      // Show immediate feedback
      showNotification(`${t('admin.deleting')} ${manualToDelete.name}...`, 'info');
      
      // Perform actual deletion
      await deleteFile(manualToDelete.file_id);
      
      // Success - show success message
      showNotification(`${t('admin.successfullyDeleted')} ${manualToDelete.name}`, 'success');
      
    } catch (error) {
      console.error('Failed to delete manual:', error);
      
      // On error - restore the item to the list
      setManuals(prevManuals => {
        // Check if item is already back in the list
        const exists = prevManuals.some(m => (m.file_id || m.name) === manualId);
        if (!exists) {
          return [...prevManuals, manualToDelete].sort((a, b) => b.timestamp - a.timestamp);
        }
        return prevManuals;
      });
      
      showNotification(`${t('admin.failedToDelete')} ${manualToDelete.name}. ${t('admin.pleaseTryAgain')}`, 'error');
    } finally {
      // Remove from deleting state
      setDeletingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(manualId);
        return newSet;
      });
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialog({ open: false, manual: null, isDeleting: false });
  };

  const handleDownload = async (manual: FileData) => {
    try {
      const filename = manual.name;
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
      
      // Show success notification
      showNotification(`${t('admin.successfullyDownloaded')} ${filename}`, 'success');
      
    } catch (error) {
      console.error('Download error:', error);
      showNotification(
        error instanceof Error ? error.message : t('admin.failedToDownloadFile'),
        'error'
      );
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp: number): string => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      py: 4, 
      px: 2,
      background: theme.palette.mode === 'dark' 
        ? 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)'
        : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
    }}>
      <StyledCard>
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <AdminIcon sx={{ fontSize: 48, color: theme.palette.primary.main, mb: 2 }} />
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
              {t('admin.title')}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              {t('admin.subtitle')}
            </Typography>
          </Box>

          {/* Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={currentTab} onChange={handleTabChange} centered>
              <Tab icon={<CloudUploadIcon />} label={t('admin.uploadTab')} />
              <Tab icon={<StorageIcon />} label={t('admin.manageTab')} />
            </Tabs>
          </Box>

          {/* Upload Tab */}
          <TabPanel value={currentTab} index={0}>
            {/* Upload Result Alert */}
            {uploadResult && (
              <Alert 
                severity={uploadResult.type} 
                sx={{ 
                  mb: 3, 
                  borderRadius: 2,
                  '& .MuiAlert-message': {
                    whiteSpace: 'pre-line', // Preserve line breaks in error messages
                    fontFamily: uploadResult.type === 'error' && uploadResult.message.includes('already exists') 
                      ? 'monospace' 
                      : 'inherit'
                  }
                }}
                icon={uploadResult.type === 'success' ? <CheckCircleIcon /> : <ErrorIcon />}
              >
                {uploadResult.message}
              </Alert>
            )}

            {/* File Upload Area */}
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                {t('admin.selectFile')}
              </Typography>
              
              <UploadArea
                elevation={0}
                isDragOver={isDragOver}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                
                {selectedFile ? (
                  <Box>
                    <Typography variant="h6" color="primary" gutterBottom>
                      {selectedFile.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {formatFileSize(selectedFile.size)}
                    </Typography>
                    <Chip 
                      label={t('admin.dropzone.fileSelected')}
                      color="success" 
                      size="small" 
                      sx={{ mt: 1 }}
                    />
                  </Box>
                ) : (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {t('admin.dropzone.title')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {t('admin.dropzone.subtitle')}
                    </Typography>
                  </Box>
                )}

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt,.doc,.docx"
                  onChange={handleFileInput}
                  style={{ display: 'none' }}
                />
              </UploadArea>
            </Box>

            {/* Metadata Form */}
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                {t('admin.productInformation')}
              </Typography>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
                <Box sx={{ flex: '1 1 300px', minWidth: '250px' }}>
                  <TextField
                    fullWidth
                    label={t('admin.brand')}
                    value={formData.brand}
                    onChange={handleInputChange('brand')}
                    placeholder={t('admin.brandPlaceholder')}
                    required
                  />
                </Box>
                
                <Box sx={{ flex: '1 1 300px', minWidth: '250px' }}>
                  <TextField
                    fullWidth
                    label={t('admin.model')}
                    value={formData.model}
                    onChange={handleInputChange('model')}
                    placeholder={t('admin.modelPlaceholder')}
                    required
                  />
                </Box>
                
                <Box sx={{ flex: '1 1 300px', minWidth: '250px' }}>
                  <TextField
                    fullWidth
                    select
                    label={t('admin.productType')}
                    value={formData.product_type}
                    onChange={handleInputChange('product_type')}
                  >
                    <MenuItem value="">
                      <em>{t('admin.selectProductType')}</em>
                    </MenuItem>
                    {productTypes.map((type) => (
                      <MenuItem key={type} value={type}>
                        {type}
                      </MenuItem>
                    ))}
                  </TextField>
                </Box>
                
                <Box sx={{ flex: '1 1 300px', minWidth: '250px' }}>
                  <TextField
                    fullWidth
                    label={t('admin.year')}
                    value={formData.year}
                    onChange={handleInputChange('year')}
                    placeholder={t('admin.yearPlaceholder')}
                    type="number"
                    inputProps={{ min: 1990, max: new Date().getFullYear() + 1 }}
                  />
                </Box>
                
                <Box sx={{ flex: '1 1 100%' }}>
                  <TextField
                    fullWidth
                    select
                    label={t('admin.language')}
                    value={formData.language}
                    onChange={handleInputChange('language')}
                  >
                    {languages.map((lang) => (
                      <MenuItem key={lang.code} value={lang.code}>
                        {lang.name}
                      </MenuItem>
                    ))}
                  </TextField>
                </Box>
              </Box>
            </Box>

            {/* Upload Progress */}
            {isUploading && (
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body2" sx={{ mr: 2 }}>
                    {t('admin.processingManual')}
                  </Typography>
                  <CircularProgress size={16} />
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                  {t('admin.largeFilesMayTakeSeveralMinutes')}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={uploadProgress} 
                  sx={{ borderRadius: 1 }}
                />
              </Box>
            )}

            {/* Upload Button */}
            <Box sx={{ textAlign: 'center' }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
                startIcon={isUploading ? <CircularProgress size={20} /> : <DescriptionIcon />}
                sx={{
                  px: 6,
                  py: 1.5,
                  fontSize: '1.1rem',
                  textTransform: 'none',
                  borderRadius: 3,
                }}
              >
                {isUploading ? t('admin.processing') : t('admin.uploadManual')}
              </Button>
            </Box>
          </TabPanel>

          {/* Manage Manuals Tab */}
          <TabPanel value={currentTab} index={1}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {t('admin.uploadedManuals')} ({manuals.length})
              </Typography>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadManuals}
                disabled={loading}
              >
                {t('admin.refresh')}
              </Button>
            </Box>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : manuals.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  {t('admin.noManuals.title')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('admin.noManuals.subtitle')}
                </Typography>
              </Box>
            ) : (
              <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>{t('admin.table.fileName')}</strong></TableCell>
                      <TableCell><strong>{t('admin.table.brand')}</strong></TableCell>
                      <TableCell><strong>{t('admin.table.model')}</strong></TableCell>
                      <TableCell><strong>{t('admin.table.type')}</strong></TableCell>
                      <TableCell><strong>{t('admin.table.language')}</strong></TableCell>
                      <TableCell><strong>{t('admin.table.uploadDate')}</strong></TableCell>
                      <TableCell><strong>{t('admin.table.actions')}</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {manuals.map((manual) => {
                      const manualId = manual.file_id || manual.name;
                      const isBeingDeleted = deletingItems.has(manualId);
                      
                      return (
                        <TableRow 
                          key={manual.file_id || manual.name}
                          sx={{
                            opacity: isBeingDeleted ? 0.5 : 1,
                            transition: 'opacity 0.3s ease',
                            backgroundColor: isBeingDeleted ? 'action.hover' : 'transparent'
                          }}
                        >
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {isBeingDeleted && (
                                <CircularProgress size={16} sx={{ color: 'warning.main' }} />
                              )}
                              <Typography 
                                variant="body2" 
                                sx={{ 
                                  fontWeight: 500,
                                  textDecoration: isBeingDeleted ? 'line-through' : 'none'
                                }}
                              >
                                {manual.name}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={manual.brand || t('admin.table.unknown')} 
                              size="small" 
                              variant="outlined"
                              sx={{ opacity: isBeingDeleted ? 0.6 : 1 }}
                            />
                          </TableCell>
                          <TableCell sx={{ opacity: isBeingDeleted ? 0.6 : 1 }}>
                            {manual.model || t('admin.table.unknown')}
                          </TableCell>
                          <TableCell sx={{ opacity: isBeingDeleted ? 0.6 : 1 }}>
                            {manual.product_type || t('admin.table.unknown')}
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={manual.language?.toUpperCase() || 'EN'} 
                              size="small"
                              color="primary"
                              sx={{ opacity: isBeingDeleted ? 0.6 : 1 }}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography 
                              variant="body2" 
                              color="text.secondary"
                              sx={{ opacity: isBeingDeleted ? 0.6 : 1 }}
                            >
                              {formatDate(manual.timestamp)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Tooltip title={t('admin.downloadPDF')}>
                                <IconButton 
                                  size="small" 
                                  color="primary"
                                  onClick={() => handleDownload(manual)}
                                  disabled={isBeingDeleted}
                                  sx={{ opacity: isBeingDeleted ? 0.4 : 1 }}
                                >
                                  <DownloadIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title={isBeingDeleted ? t('admin.deleting') : t('admin.deleteManual')}>
                                <IconButton 
                                  size="small" 
                                  color="error"
                                  onClick={() => handleDeleteClick(manual)}
                                  disabled={isBeingDeleted}
                                  sx={{ opacity: isBeingDeleted ? 0.4 : 1 }}
                                >
                                  {isBeingDeleted ? (
                                    <CircularProgress size={16} color="error" />
                                  ) : (
                                    <DeleteIcon />
                                  )}
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </TabPanel>
        </CardContent>
      </StyledCard>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog.open} onClose={handleDeleteCancel}>
        <DialogTitle>{t('admin.confirmDeletionTitle')}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('admin.confirmDeletionText')}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={handleDeleteCancel}
            disabled={deleteDialog.isDeleting}
          >
            {t('admin.cancel')}
          </Button>
          <Button 
            onClick={handleDeleteConfirm} 
            color="error" 
            variant="contained"
            disabled={deleteDialog.isDeleting}
            startIcon={deleteDialog.isDeleting ? <CircularProgress size={16} /> : null}
          >
            {deleteDialog.isDeleting ? t('admin.deleting') : t('admin.delete')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
        onClose={() => setNotification(prev => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          severity={notification.severity} 
          onClose={() => setNotification(prev => ({ ...prev, open: false }))}
          sx={{ borderRadius: 2 }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AdminPage; 