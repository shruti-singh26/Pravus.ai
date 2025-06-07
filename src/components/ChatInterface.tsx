import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  IconButton,
  CircularProgress,
  PaletteMode,
  useTheme,
  styled,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Rating,
  Alert,
} from '@mui/material';
import { 
  Send as SendIcon, 
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  VolumeUp as VolumeUpIcon,
} from '@mui/icons-material';
// @ts-ignore
import ReactMarkdown from 'react-markdown';
import Header from './Header';
import { summarizeConversation, sendMessage } from '../services/api';

// Styled components
const MessageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  width: '100%',
  maxWidth: '850px',
  margin: '0 auto',
}));

const MarkdownContent = styled(Box)(({ theme }) => ({
  '& p': {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
  '& ul, & ol': {
    marginTop: theme.spacing(0.5),
    marginBottom: theme.spacing(0.5),
    paddingLeft: theme.spacing(3),
  },
  '& li': {
    marginTop: theme.spacing(0.5),
    marginBottom: theme.spacing(0.5),
  },
  '& h2, & h3, & h4': {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(1),
    fontWeight: 600,
  },
  '& code': {
    backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
    padding: '2px 4px',
    borderRadius: 4,
    fontFamily: 'monospace',
  },
  '& strong': {
    fontWeight: 600,
    color: theme.palette.mode === 'dark' ? theme.palette.primary.light : theme.palette.primary.main,
  },
}));

const UserMessage = styled(MessageContainer)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#444654' : '#f7f7f8',
  color: theme.palette.text.primary,
  borderTop: `1px solid ${theme.palette.mode === 'dark' ? '#444654' : '#e5e5e5'}`,
  borderBottom: `1px solid ${theme.palette.mode === 'dark' ? '#444654' : '#e5e5e5'}`,
}));

const BotMessage = styled(MessageContainer)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#343541' : '#ffffff',
  color: theme.palette.text.primary,
  borderTop: `1px solid ${theme.palette.mode === 'dark' ? '#343541' : '#e5e5e5'}`,
  borderBottom: `1px solid ${theme.palette.mode === 'dark' ? '#343541' : '#e5e5e5'}`,
}));

const TypingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(3),
  marginBottom: theme.spacing(3),
  marginTop: theme.spacing(1),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.mode === 'dark' ? '#343541' : '#ffffff',
  color: theme.palette.text.primary,
  width: '100%',
  maxWidth: '850px',
  margin: '8px auto 24px auto',
  borderTop: `1px solid ${theme.palette.mode === 'dark' ? '#343541' : '#e5e5e5'}`,
  borderBottom: `1px solid ${theme.palette.mode === 'dark' ? '#343541' : '#e5e5e5'}`,
  minHeight: '80px',
  boxShadow: theme.palette.mode === 'dark' 
    ? '0 2px 8px rgba(0,0,0,0.3)' 
    : '0 2px 8px rgba(0,0,0,0.1)',
  position: 'relative',
  zIndex: 10,
}));

const MessageContent = styled(Box)({
  display: 'flex',
  alignItems: 'flex-start',
  maxWidth: '650px',
  margin: '0 auto',
  width: '100%',
  padding: '0',
});

const Avatar = styled(Box)(({ theme }) => ({
  width: 36,
  height: 36,
  minWidth: 36,
  minHeight: 36,
  borderRadius: '8px',
  marginRight: theme.spacing(2),
  backgroundColor: theme.palette.primary.main,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: 'white',
  fontWeight: 'bold',
  flexShrink: 0,
  marginTop: '0',
  boxShadow: theme.palette.mode === 'dark' ? 'none' : '0 2px 4px rgba(0,0,0,0.1)',
}));



interface FormattedMessageProps {
  text: string;
}

const FormattedMessage: React.FC<FormattedMessageProps> = ({ text }) => {
  const theme = useTheme();
  const darkModeClass = theme.palette.mode === 'dark' ? 'dark-mode' : '';
  
  return (
    <MarkdownContent 
      className={`markdown-content ${darkModeClass}`}
      sx={{ 
        width: '100%',
        pt: '2px',
      }}
    >
      <ReactMarkdown>{text}</ReactMarkdown>
    </MarkdownContent>
  );
};

interface ChatInterfaceProps {
  toggleColorMode: () => void;
  mode: PaletteMode;
}

interface FeedbackProps {
  onFeedbackSubmit: (isPositive: boolean) => void;
  feedbackSubmitted?: boolean;
}

const FeedbackButtons = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  marginTop: theme.spacing(2),
  marginBottom: theme.spacing(1),
  paddingTop: theme.spacing(0.1),
  paddingBottom: theme.spacing(1),
  position: 'relative',
  zIndex: 100,
  backgroundColor: 'transparent',
  minHeight: '48px',
  alignItems: 'center',
}));

const Feedback: React.FC<FeedbackProps & { feedbackSubmitted?: boolean }> = ({ onFeedbackSubmit, feedbackSubmitted }) => {
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);

  const handleFeedback = (isPositive: boolean) => {
    const newFeedback = isPositive ? 'up' : 'down';
    // If clicking the same button again, reset the state
    if (feedback === newFeedback) {
      setFeedback(null);
    } else {
      setFeedback(newFeedback);
      onFeedbackSubmit(isPositive);
    }
  };

  return (
    <FeedbackButtons>
      {!feedbackSubmitted ? (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
            Did this help?
          </Typography>
          <Tooltip title="Yes, this helped">
            <IconButton 
              size="small" 
              onClick={() => handleFeedback(true)}
            >
              <ThumbUpIcon 
                fontSize="small" 
                sx={{ 
                  color: feedback === 'up' ? 'success.main' : 'inherit'
                }} 
              />
            </IconButton>
          </Tooltip>
          <Tooltip title="No, I need more help">
            <IconButton 
              size="small" 
              onClick={() => handleFeedback(false)}
            >
              <ThumbDownIcon 
                fontSize="small" 
                sx={{ 
                  color: feedback === 'down' ? 'error.main' : 'inherit'
                }} 
              />
            </IconButton>
          </Tooltip>
        </>
      ) : (
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ 
            fontStyle: 'italic',
            opacity: 0.7,
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          ✓ Thank you for your feedback
        </Typography>
      )}
    </FeedbackButtons>
  );
};

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  showFeedback?: boolean;
  feedbackSubmitted?: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ toggleColorMode, mode }) => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { language } = useParams<{ language: string }>();
  const manual = location.state?.manual;
  const categoryId = location.state?.categoryId;
  const currentLanguage = language || i18n.language;
  
  const [messages, setMessages] = useState<Message[]>([{
    id: 1,
    text: manual 
      ? `# 👋 ${t('chat.welcome')}\n\n` +
        `${t('chat.welcomeManual', { brand: manual.brand, model: manual.model })}\n\n` +
        `### 🔍 ${t('chat.features.title')}\n` +
        `• ${t('chat.features.understand')}\n` +
        `• ${t('chat.features.performance')}\n` +
        `• ${t('chat.features.discover')}\n\n` +
        `### 🛠️ ${t('chat.setup.title')}\n` +
        `• ${t('chat.setup.installation')}\n` +
        `• ${t('chat.setup.configuration')}\n` +
        `• ${t('chat.setup.troubleshooting')}\n\n` +
        `### 💡 ${t('chat.maintenance.title')}\n` +
        `• ${t('chat.maintenance.practices')}\n` +
        `• ${t('chat.maintenance.tips')}\n` +
        `• ${t('chat.maintenance.safety')}\n\n` +
        `*${t('chat.assistPrompt', { brand: manual.brand, model: manual.model })}*`
      : `# 👋 ${t('chat.welcome')}\n\n` +
        `${t('chat.welcomeGeneral')}\n\n` +
        `### 🌟 ${t('chat.capabilities.title')}\n` +
        `• ${t('chat.capabilities.features')}\n` +
        `• ${t('chat.capabilities.support')}\n` +
        `• ${t('chat.capabilities.troubleshooting')}\n` +
        `• ${t('chat.capabilities.maintenance')}\n\n` +
        `*${t('chat.generalPrompt')}*`,
    sender: 'bot'
  }]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [ratingDialogOpen, setRatingDialogOpen] = useState(false);
  const [rating, setRating] = useState<number | null>(null);
  const [ticketDialogOpen, setTicketDialogOpen] = useState(false);
  const [showTicketSuccess, setShowTicketSuccess] = useState(false);
  const [awaitingClarification, setAwaitingClarification] = useState(false);
  const [conversation, setConversation] = useState<any[]>([]);
  
  // Support ticket form state
  const [ticketForm, setTicketForm] = useState({
    email: '',
    phone: '',
    chatSummary: '',
    comments: '',
    attachments: [] as File[]
  });
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [currentFeedbackMessageId, setCurrentFeedbackMessageId] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const theme = useTheme();

  // Add state for speech
  const [isSpeaking, setIsSpeaking] = useState(false);
  const speechSynthesis = window.speechSynthesis;
  
  // Function to stop any ongoing speech
  const stopSpeaking = () => {
    if (speechSynthesis.speaking) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };
  
  // Function to speak text
  const speakText = (text: string) => {
    // Stop any ongoing speech
    stopSpeaking();
    
    try {
      // Remove markdown formatting and clean up the text
      const cleanText = text
        .replace(/[#*`]/g, '') // Remove markdown symbols
        .replace(/\n/g, '. ') // Replace newlines with periods for better pausing
        .replace(/\s+/g, ' ') // Normalize spaces
        .trim();
      
      const utterance = new SpeechSynthesisUtterance(cleanText);
      
      // Set language based on current UI language
      utterance.lang = i18n.language;
      
      // Adjust speech parameters for better clarity
      utterance.rate = 1.0; // Normal speed
      utterance.pitch = 1.0; // Normal pitch
      utterance.volume = 1.0; // Full volume
      
      // Handle speech events
      utterance.onstart = () => {
        console.log('Started speaking');
        setIsSpeaking(true);
      };
      
      utterance.onend = () => {
        console.log('Finished speaking');
        setIsSpeaking(false);
      };
      
      utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        setIsSpeaking(false);
      };
      
      // Start speaking
      speechSynthesis.speak(utterance);
      
      // Chrome bug workaround: speech can sometimes end prematurely
      const intervalId = setInterval(() => {
        if (speechSynthesis.speaking) {
          speechSynthesis.pause();
          speechSynthesis.resume();
        } else {
          clearInterval(intervalId);
        }
      }, 14000);
      
    } catch (error) {
      console.error('Text-to-speech error:', error);
      setIsSpeaking(false);
    }
  };
  
  // Stop speaking when component unmounts or language changes
  useEffect(() => {
    return () => {
      stopSpeaking();
    };
  }, [i18n.language]);

  // Set the language from URL parameter
  useEffect(() => {
    if (language && language !== i18n.language) {
      i18n.changeLanguage(language);
    }
  }, [language, i18n]);

  // Update welcome message when language changes
  useEffect(() => {
    const welcomeMessage = manual 
      ? `# 👋 ${t('chat.welcome')}\n\n` +
        `${t('chat.welcomeManual', { brand: manual.brand, model: manual.model })}\n\n` +
        `### 🔍 ${t('chat.features.title')}\n` +
        `• ${t('chat.features.understand')}\n` +
        `• ${t('chat.features.performance')}\n` +
        `• ${t('chat.features.discover')}\n\n` +
        `### 🛠️ ${t('chat.setup.title')}\n` +
        `• ${t('chat.setup.installation')}\n` +
        `• ${t('chat.setup.configuration')}\n` +
        `• ${t('chat.setup.troubleshooting')}\n\n` +
        `### 💡 ${t('chat.maintenance.title')}\n` +
        `• ${t('chat.maintenance.practices')}\n` +
        `• ${t('chat.maintenance.tips')}\n` +
        `• ${t('chat.maintenance.safety')}\n\n` +
        `*${t('chat.assistPrompt', { brand: manual.brand, model: manual.model })}*`
      : `# 👋 ${t('chat.welcome')}\n\n` +
        `${t('chat.welcomeGeneral')}\n\n` +
        `### 🌟 ${t('chat.capabilities.title')}\n` +
        `• ${t('chat.capabilities.features')}\n` +
        `• ${t('chat.capabilities.support')}\n` +
        `• ${t('chat.capabilities.troubleshooting')}\n` +
        `• ${t('chat.capabilities.maintenance')}\n\n` +
        `*${t('chat.generalPrompt')}*`;

    setMessages(prev => [
      {
        id: 1,
        text: welcomeMessage,
        sender: 'bot'
      },
      ...prev.slice(1) // Keep all messages except the first welcome message
    ]);
  }, [currentLanguage, t, manual]);

  // Auto-scroll when processing starts to ensure thinking indicator is visible
  useEffect(() => {
    if (isProcessing) {
      // Immediate scroll to ensure thinking indicator is visible
      const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'end',
          inline: 'nearest'
        });
      };
      
      // Multiple scroll attempts to ensure it works
      scrollToBottom();
      setTimeout(scrollToBottom, 50);
      setTimeout(scrollToBottom, 150);
    }
  }, [isProcessing]);

  // Auto-scroll when new messages are added
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'end',
          inline: 'nearest'
        });
      }, 100);
    }
  }, [messages.length]);

  const handleFeedbackSubmit = async (messageId: number, isPositive: boolean) => {
    setCurrentFeedbackMessageId(messageId);
    
    if (isPositive) {
      setRatingDialogOpen(true);
    } else {
      // Generate intelligent summary using LLM
      setIsGeneratingSummary(true);
      setTicketDialogOpen(true); // Open dialog first to show loading state
      
      try {
        console.log('🤖 Generating intelligent conversation summary...');
        const summary = await summarizeConversation(messages);
        
        setTicketForm(prev => ({
          ...prev,
          chatSummary: summary
        }));
        
        console.log('✅ Summary generated successfully');
      } catch (error) {
        console.error('❌ Failed to generate summary:', error);
        // Fallback to basic formatting if LLM fails
        const fallbackSummary = messages
          .filter(msg => msg.sender === 'user' || msg.sender === 'bot')
          .filter(msg => !msg.text.includes('👋') && !msg.text.includes('Welcome'))
          .map(msg => `${msg.sender === 'user' ? 'User' : 'Assistant'}: ${msg.text}`)
          .join('\n\n');
        
        setTicketForm(prev => ({
          ...prev,
          chatSummary: fallbackSummary || "No conversation to summarize."
        }));
      } finally {
        setIsGeneratingSummary(false);
      }
    }
  };

  const handleRatingSubmit = async () => {
    // Mark feedback as submitted for the current message
    if (currentFeedbackMessageId !== null) {
      setMessages(prev => prev.map(msg => 
        msg.id === currentFeedbackMessageId 
          ? { ...msg, feedbackSubmitted: true }
          : msg
      ));
    }
    
    // Here you would typically send the rating to your backend
    setRatingDialogOpen(false);
    setRating(null);
    setCurrentFeedbackMessageId(null);
  };

  const handleRatingCancel = () => {
    setRatingDialogOpen(false);
    setRating(null);
    setCurrentFeedbackMessageId(null);
    // Don't mark as submitted since user cancelled
  };

  const handleTicketSubmit = async () => {
    // Mark feedback as submitted for the current message
    if (currentFeedbackMessageId !== null) {
      setMessages(prev => prev.map(msg => 
        msg.id === currentFeedbackMessageId 
          ? { ...msg, feedbackSubmitted: true }
          : msg
      ));
    }
    
    // Here you would typically send the ticket to your backend
    console.log('Support ticket submitted:', {
      ...ticketForm,
      attachmentCount: ticketForm.attachments.length,
      timestamp: new Date().toISOString()
    });
    
    setTicketDialogOpen(false);
    setShowTicketSuccess(true);
    setTimeout(() => setShowTicketSuccess(false), 5000);
    setTicketForm({
      email: '',
      phone: '',
      chatSummary: '',
      comments: '',
      attachments: []
    });
    setIsGeneratingSummary(false);
    setCurrentFeedbackMessageId(null);
  };

  const handleTicketCancel = () => {
    setTicketDialogOpen(false);
    setTicketForm({
      email: '',
      phone: '',
      chatSummary: '',
      comments: '',
      attachments: []
    });
    setIsGeneratingSummary(false);
    setCurrentFeedbackMessageId(null);
    // Don't mark as submitted since user cancelled
  };

  const handleFileAttachment = () => {
    fileInputRef.current?.click();
  };

  const removeAttachment = (index: number) => {
    setTicketForm(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isProcessing) return;

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsProcessing(true);

    // Immediate scroll to bottom when processing starts
    const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ 
        behavior: 'smooth',
        block: 'end',
        inline: 'nearest'
      });
    };
    
    // Multiple scroll attempts to ensure thinking indicator is visible
    scrollToBottom();
    setTimeout(scrollToBottom, 100);
    setTimeout(scrollToBottom, 200);

    try {
      const data = await sendMessage(
        inputValue,
        i18n.language,
        i18n.language,
        manual?.brand,
        manual?.model,
        { awaiting_clarification: awaitingClarification,
          conversation: conversation
         }
      );

      setAwaitingClarification(data.awaiting_clarification);

      setConversation(data.conversation); // <-- Update conversation from backend
      
      const botMessage: Message = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        showFeedback: true,
      };
      setMessages(prev => [...prev, botMessage]);

      // Scroll to bottom after bot response with better options
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'end',
          inline: 'nearest'
        });
      }, 150);

    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error while processing your request. Please try again.',
        sender: 'bot',
        showFeedback: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBack = () => {
    // Navigate back to the specific category page
    if (categoryId) {
      navigate(`/category/${categoryId}`);
    } else {
      // Fallback: Navigate based on the manual's context
      if (manual?.product_type?.toLowerCase().includes('washing') || 
          manual?.product_type?.toLowerCase().includes('appliance')) {
        navigate('/category/home_appliances');
      } else if (manual?.product_type?.toLowerCase().includes('tv')) {
        navigate('/category/tv_video');
      } else {
        // Default fallback to home page
        navigate('/');
      }
    }
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      height: '100vh', 
      overflow: 'hidden',
      backgroundColor: theme.palette.mode === 'dark' ? '#343541' : '#ffffff',
    }}>
      {/* Header */}
      <Header 
        mode={mode} 
        toggleColorMode={toggleColorMode} 
        onBackClick={handleBack}
        hideLanguageSelector={true}
      />

      {/* Main content */}
      <Box sx={{ 
        flexGrow: 1, 
        display: 'flex', 
        flexDirection: 'column',
        height: 'calc(100vh - 64px)',
        overflow: 'hidden',
        backgroundColor: theme.palette.mode === 'dark' ? '#343541' : '#ffffff',
        marginTop: '64px',
      }}>
        {/* Messages area */}
        <Box sx={{ 
          flexGrow: 1,
          overflow: 'hidden',
          display: 'flex',
          justifyContent: 'center',
          width: '100%',
          paddingBottom: '120px', // Reserve space for fixed input area
        }}>
          <Box sx={{ 
            width: '100%',
            maxWidth: '900px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'auto',
            px: 2,
            // Hide scrollbar
            '&::-webkit-scrollbar': {
              display: 'none',
            },
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
          }}>
            {messages.map((message) => (
              message.sender === 'user' ? (
                <UserMessage key={message.id}>
                  <MessageContent>
                    <Avatar>U</Avatar>
                    <Typography variant="body1" sx={{ wordBreak: 'break-word', width: '100%', pt: '2px' }}>
                      {message.text}
                    </Typography>
                  </MessageContent>
                </UserMessage>
              ) : (
                <BotMessage key={message.id}>
                  <MessageContent>
                    <Avatar>P</Avatar>
                    <Box sx={{ width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', width: '100%' }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <FormattedMessage text={message.text} />
                        </Box>
                        <Tooltip title={t('chat.speak')} placement="top">
                          <IconButton 
                            onClick={() => speakText(message.text)}
                            disabled={isSpeaking}
                            size="small"
                            sx={{ 
                              ml: 1,
                              color: isSpeaking ? 'primary.main' : 'text.secondary',
                              '&:hover': {
                                color: 'primary.main',
                              }
                            }}
                          >
                            <VolumeUpIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      {message.showFeedback && (
                        <Feedback 
                          onFeedbackSubmit={(isPositive) => handleFeedbackSubmit(message.id, isPositive)} 
                          feedbackSubmitted={message.feedbackSubmitted}
                        />
                      )}
                    </Box>
                  </MessageContent>
                </BotMessage>
              )
            ))}

            {isProcessing && (
              <TypingIndicator>
                <MessageContent>
                  <Avatar>P</Avatar>
                  <Box sx={{ display: 'flex', alignItems: 'center', pt: '2px' }}>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    <Typography variant="body2">Thinking...</Typography>
                  </Box>
                </MessageContent>
              </TypingIndicator>
            )}

            <div ref={messagesEndRef} />
            
            {/* Add extra bottom padding to ensure content is never hidden behind input */}
            <Box sx={{ height: '40px' }} />
          </Box>
        </Box>

        {/* Input area - Fixed at bottom */}
        <Box 
          component="form" 
          onSubmit={handleSubmit}
          sx={{ 
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            p: 2,
            borderTop: `1px solid ${theme.palette.mode === 'dark' ? '#444654' : '#e5e5e5'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: theme.palette.mode === 'dark' ? '#343541' : '#ffffff',
            zIndex: 1000,
            boxShadow: '0 -4px 20px rgba(0, 0, 0, 0.1)',
          }}
        >
          <Box sx={{ 
            width: '100%', 
            maxWidth: '900px', 
            display: 'flex', 
            alignItems: 'center',
            position: 'relative',
            border: `1px solid ${theme.palette.mode === 'dark' ? '#565869' : '#e5e5e5'}`,
            borderRadius: '25px',
            p: '4px',
            backgroundColor: theme.palette.mode === 'dark' ? '#40414f' : '#ffffff',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
            '&:focus-within': {
              borderColor: theme.palette.primary.main,
              boxShadow: `0 4px 20px ${theme.palette.mode === 'dark' ? 'rgba(33, 150, 243, 0.3)' : 'rgba(33, 150, 243, 0.2)'}`,
            }
          }}>
            <TextField
              fullWidth
              placeholder="Ask a question about your manual..."
              variant="standard"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isProcessing}
              InputProps={{
                disableUnderline: true,
              }}
              sx={{ 
                mx: 2,
                '& .MuiInputBase-input': {
                  py: 1.5,
                  fontSize: '1rem',
                }
              }}
            />
            <IconButton 
              type="submit" 
              size="large"
              disabled={!inputValue.trim() || isProcessing}
              sx={{ 
                mr: 1,
                backgroundColor: theme.palette.primary.main,
                color: 'white',
                '&:hover': {
                  backgroundColor: theme.palette.primary.dark,
                },
                '&:disabled': {
                  backgroundColor: theme.palette.action.disabled,
                },
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Rating Dialog */}
        <Dialog open={ratingDialogOpen} onClose={handleRatingCancel}>
          <DialogTitle>Rate Your Experience</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 2 }}>
              <Rating
                value={rating}
                onChange={(_, newValue) => setRating(newValue)}
                size="large"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleRatingCancel}>Cancel</Button>
            <Button onClick={handleRatingSubmit} variant="contained" disabled={!rating}>
              Submit
            </Button>
          </DialogActions>
        </Dialog>

        {/* Ticket Dialog */}
        <Dialog 
          open={ticketDialogOpen} 
          onClose={handleTicketCancel}
          maxWidth="md"
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: 3,
              maxHeight: '90vh'
            }
          }}
        >
          <DialogTitle sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}>
            <Box sx={{ 
              width: 40, 
              height: 40, 
              borderRadius: 2, 
              backgroundColor: 'error.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white'
            }}>
              📋
            </Box>
            Create Support Ticket
          </DialogTitle>
          <DialogContent sx={{ pt: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {/* Contact Information */}
              <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
                Contact Information
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', sm: 'row' } }}>
                <TextField
                  required
                  label="Email Address"
                  type="email"
                  fullWidth
                  value={ticketForm.email}
                  onChange={(e) => setTicketForm({ ...ticketForm, email: e.target.value })}
                  placeholder="your.email@example.com"
                  helperText="We'll use this to contact you about your ticket"
                />
                <TextField
                  required
                  label="Phone Number"
                  type="tel"
                  fullWidth
                  value={ticketForm.phone}
                  onChange={(e) => setTicketForm({ ...ticketForm, phone: e.target.value })}
                  placeholder="+1 (555) 123-4567"
                  helperText="For urgent issues, we may call you"
                />
              </Box>

              {/* Chat Summary */}
              <Typography variant="h6" color="primary" sx={{ mb: 1, mt: 2 }}>
                🤖 AI-Generated Conversation Summary
              </Typography>
              <TextField
                required
                label={isGeneratingSummary ? "Generating intelligent summary..." : "Conversation Summary"}
                multiline
                rows={6}
                fullWidth
                value={isGeneratingSummary ? "🤖 Analyzing conversation and generating intelligent summary..." : ticketForm.chatSummary}
                onChange={(e) => setTicketForm({ ...ticketForm, chatSummary: e.target.value })}
                placeholder="AI will automatically generate a professional summary of your conversation..."
                helperText={isGeneratingSummary ? "Please wait while AI analyzes your conversation..." : "AI-generated summary focusing on your main issue and key details. You can edit this if needed."}
                disabled={isGeneratingSummary}
                sx={{
                  '& .MuiInputBase-input': {
                    fontSize: '0.875rem',
                    fontFamily: isGeneratingSummary ? 'inherit' : 'monospace'
                  }
                }}
                InputProps={{
                  startAdornment: isGeneratingSummary ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', mr: 1 }}>
                      <CircularProgress size={16} />
                    </Box>
                  ) : null
                }}
              />

              {/* Additional Comments */}
              <Typography variant="h6" color="primary" sx={{ mb: 1, mt: 2 }}>
                Additional Information
              </Typography>
              <TextField
                required
                label="Comments & Additional Details"
                multiline
                rows={4}
                fullWidth
                value={ticketForm.comments}
                onChange={(e) => setTicketForm({ ...ticketForm, comments: e.target.value })}
                placeholder="Please describe your issue in detail, what you expected to happen, and any steps you've already tried..."
                helperText="The more details you provide, the better we can help you"
              />

              {/* File Attachments */}
              <Typography variant="h6" color="primary" sx={{ mb: 1, mt: 2 }}>
                Attachments (Optional)
              </Typography>
              
              <Box sx={{ 
                border: 2, 
                borderColor: 'divider', 
                borderStyle: 'dashed',
                borderRadius: 2,
                p: 3,
                textAlign: 'center',
                backgroundColor: 'background.paper'
              }}>
                <Button
                  variant="outlined"
                  onClick={handleFileAttachment}
                  startIcon={<Box>📎</Box>}
                  sx={{ mb: 1 }}
                >
                  Attach Files
                </Button>
                <Typography variant="body2" color="text.secondary">
                  Upload screenshots, documents, or any relevant files
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Supported formats: Images, PDFs, Documents (Max 10MB each)
                </Typography>
              </Box>

              {/* Display attached files */}
              {ticketForm.attachments.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Attached Files ({ticketForm.attachments.length}):
                  </Typography>
                  {ticketForm.attachments.map((file, index) => (
                    <Box 
                      key={index}
                      sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between',
                        p: 1,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1,
                        mb: 1,
                        backgroundColor: 'background.default'
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box>📄</Box>
                        <Box>
                          <Typography variant="body2" noWrap>
                            {file.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {(file.size / 1024 / 1024).toFixed(2)} MB
                          </Typography>
                        </Box>
                      </Box>
                      <IconButton 
                        size="small" 
                        onClick={() => removeAttachment(index)}
                        color="error"
                      >
                        ❌
                      </IconButton>
                    </Box>
                  ))}
                </Box>
              )}

              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt"
                style={{ display: 'none' }}
                onChange={(e) => {
                  if (e.target.files) {
                    const files = Array.from(e.target.files);
                    setTicketForm(prev => ({ 
                      ...prev, 
                      attachments: [...prev.attachments, ...files] 
                    }));
                  }
                }}
              />
            </Box>
          </DialogContent>
          <DialogActions sx={{ p: 3, borderTop: 1, borderColor: 'divider' }}>
            <Button 
              onClick={handleTicketCancel}
              variant="outlined"
            >
              Cancel
            </Button>
            <Button 
              onClick={handleTicketSubmit} 
              variant="contained" 
              disabled={!ticketForm.email.trim() || !ticketForm.phone.trim() || !ticketForm.chatSummary.trim() || !ticketForm.comments.trim()}
              sx={{ minWidth: 120 }}
            >
              Submit Ticket
            </Button>
          </DialogActions>
        </Dialog>

        {/* Success Alert */}
        {showTicketSuccess && (
          <Alert 
            severity="success" 
            sx={{ 
              position: 'fixed', 
              bottom: 16, 
              left: '50%', 
              transform: 'translateX(-50%)',
              zIndex: theme.zIndex.snackbar
            }}
          >
            Ticket submitted successfully! Our team will contact you soon.
          </Alert>
        )}

        <Typography variant="caption" color="text.secondary" align="center" sx={{ p: 1, opacity: 0.7 }}>
          Powered by Pravus.AI - Responses are generated based on your manual content
        </Typography>
      </Box>
    </Box>
  );
};

export default ChatInterface; 