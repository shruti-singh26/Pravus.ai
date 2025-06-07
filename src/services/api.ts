/**
 * API service for communicating with the backend
 */

import axios, { AxiosError } from 'axios';

const API_BASE_URL = 'http://localhost:5000/api'; // Hardcoded to ensure correct backend URL

export interface ChatResponse {
  response: string;
  sources?: Array<{
    filename: string;
    brand?: string;
    model?: string;
    page: number | string;
  }>;
  timestamp: number;
}

export interface FileUploadResponse {
  success: boolean;
  file_id: string;
  filename: string;
  brand?: string;
  model?: string;
  language?: string;
  timestamp: number;
  message: string;
}

export interface FileData {
  name: string;
  brand?: string;
  model?: string;
  product_type?: string;
  year?: string;
  timestamp: number;
  file_id?: string;
  language?: string;
}

export interface ManualMetadata {
  brand?: string;
  model?: string;
  product_type?: string;
  year?: string;
  language?: string;
  file_id?: string;
  filename?: string;
  isDemoData?: boolean; // Flag to indicate if this is demo/fake data
}

export interface ApiResponse {
  success: boolean;
  message: string;
  data?: any;
}

/**
 * Send a message to the backend and get a response
 */
export const sendMessage = async (
  message: string, 
  language: string = 'en', 
  responseLanguage: string = 'en',
  brand?: string,
  model?: string,
  context?: {
    awaiting_clarification?: boolean;
    conversation?: any[];
    source_language?: string;
  }
): Promise<any> => {
  const response = await axios.post(`${API_BASE_URL}/chat`, {
    message,
    language,
    responseLanguage,
    brand,
    model,
    ...(context && { 
      context: {
        ...context,
        source_language: context.source_language || language
      }
    })
  });
  
  return response.data;
};

/**
 * Upload a file to the backend with metadata
 */
export const uploadFile = async (
  file: File,
  metadata?: {
    brand?: string;
    model?: string;
    language?: string;
    product_type?: string;
    year?: string;
  }
): Promise<FileUploadResponse> => {
  try {
    // Validate file type
    const allowedTypes = ['.pdf', '.txt', '.doc', '.docx'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!allowedTypes.includes(fileExtension)) {
      throw new Error(`Unsupported file type. Allowed types: ${allowedTypes.join(', ')}`);
    }

    // Validate file size (16MB limit)
    const maxSize = 16 * 1024 * 1024; // 16MB in bytes
    if (file.size > maxSize) {
      throw new Error('File size exceeds 16MB limit');
    }

    const formData = new FormData();
    formData.append('file', file);
    
    // Add metadata if provided
    if (metadata) {
      Object.entries(metadata).forEach(([key, value]) => {
        if (value) {
          formData.append(key, value);
        }
      });
    }
    
    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      // Increase timeout to 5 minutes for large file processing
      timeout: 300000, // 5 minutes timeout
    });
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Upload failed');
    }
    
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('Upload timeout. Please try again.');
      }
      if (error.response) {
        // Handle duplicate filename error specifically
        if (error.response.status === 409 && error.response.data?.duplicate_info) {
          const duplicateInfo = error.response.data.duplicate_info;
          const uploadDate = new Date(duplicateInfo.upload_date).toLocaleDateString();
          throw new Error(
            `File "${duplicateInfo.filename}" already exists!\n\n` +
            `Existing file details:\n` +
            `• Brand: ${duplicateInfo.brand}\n` +
            `• Model: ${duplicateInfo.model}\n` +
            `• Upload Date: ${uploadDate}\n\n` +
            `Please rename your file or delete the existing one first.`
          );
        }
        
        const errorMessage = error.response.data?.error || error.response.statusText;
        throw new Error(`Upload failed: ${errorMessage}`);
      }
    }
    throw error;
  }
};

/**
 * Get list of uploaded files
 */
export const getFiles = async (): Promise<FileData[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/files`, {
      timeout: 10000, // 10 seconds timeout for this request
    });
    // Handle both array and object responses for backward compatibility
    return Array.isArray(response.data) ? response.data : response.data.files || [];
  } catch (error) {
    console.error('Failed to get files:', error);
    
    // If it's a timeout or network error, return empty array instead of throwing
    if (error instanceof AxiosError) {
      if (error.code === 'ECONNABORTED') {
        console.warn('Request timeout when fetching files, assuming no manuals exist');
        return [];
      }
      if (error.response?.status === 404 || error.response?.status === 500) {
        console.warn('Server error when fetching files, assuming no manuals exist');
        return [];
      }
    }
    
    // For other errors, still throw to maintain error handling behavior
    throw error;
  }
};

/**
 * Delete a file by ID
 */
export const deleteFile = async (fileId: string): Promise<ApiResponse> => {
  const response = await axios.delete(`${API_BASE_URL}/files/${fileId}`);
  return response.data;
};

/**
 * Get all available brands
 */
export const getBrands = async (): Promise<string[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/brands`);
    return response.data.brands;
  } catch (error) {
    console.error('Failed to get brands:', error);
    throw error;
  }
};

/**
 * Get models for a specific brand
 */
export const getModels = async (brand?: string): Promise<string[]> => {
  try {
    const url = brand 
      ? `${API_BASE_URL}/models?brand=${encodeURIComponent(brand)}`
      : `${API_BASE_URL}/models`;
      
    const response = await axios.get(url);
    return response.data.models;
  } catch (error) {
    console.error('Failed to get models:', error);
    throw error;
  }
};

export const getSupportedLanguages = async (): Promise<string[]> => {
  const response = await axios.get(`${API_BASE_URL}/languages`);
  return response.data.supported_languages;
};

/**
 * Download a file from the server
 */
export const downloadFile = async (filename: string): Promise<Blob> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/download/${encodeURIComponent(filename)}`, {
      responseType: 'blob',
      timeout: 30000, // 30 seconds timeout for downloads
    });
    
    if (response.status !== 200) {
      throw new Error(`Download failed: ${response.status} ${response.statusText}`);
    }
    
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('Download timeout. Please try again.');
      }
      if (error.response && error.response.data instanceof Blob) {
        // Try to extract error message from blob response
        const text = await error.response.data.text();
        try {
          const errorData = JSON.parse(text);
          throw new Error(errorData.message || 'Download failed');
        } catch {
          throw new Error('Download failed. Please try again.');
        }
      }
      if (error.response) {
        const errorMessage = error.response.data?.message || error.response.statusText;
        throw new Error(`Download failed: ${errorMessage}`);
      }
    }
    throw error;
  }
};

/**
 * Summarize a conversation using LLM for support ticket creation
 */
export const summarizeConversation = async (messages: Array<{text: string, sender: 'user' | 'bot'}>): Promise<string> => {
  try {
    // Filter out welcome messages and format conversation
    const conversationMessages = messages.filter(msg => 
      !msg.text.includes('👋') && // Filter out welcome messages
      !msg.text.includes('Welcome') &&
      msg.text.trim().length > 0
    );

    if (conversationMessages.length === 0) {
      return "No conversation to summarize.";
    }

    const response = await axios.post(`${API_BASE_URL}/summarize`, {
      messages: conversationMessages,
      context: "support_ticket"
    });
    
    return response.data.summary || "Unable to generate summary.";
  } catch (error) {
    console.error('Failed to summarize conversation:', error);
    // Fallback to basic formatting if LLM summarization fails
    const fallbackSummary = messages
      .filter(msg => !msg.text.includes('👋') && !msg.text.includes('Welcome'))
      .map(msg => `${msg.sender === 'user' ? 'User' : 'Assistant'}: ${msg.text}`)
      .join('\n\n');
    
    return fallbackSummary || "No conversation to summarize.";
  }
}; 