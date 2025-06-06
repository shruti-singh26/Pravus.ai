# Pravus.AI Chatbot

A React and Flask application for interacting with electronic manuals, leveraging advanced retrieval-augmented generation (RAG) capabilities with Azure OpenAI.

## Project Structure

The project consists of two parts:
- `src/`: React frontend
- `server/`: Flask backend API with RAG system for manuals

## Features

- **Smart Manual Search**: Advanced semantic search using Azure OpenAI embeddings with optimized filtering
- **Brand/Model Specific Search**: Strict filtering to search only within selected manual/model
- **Chat Interface**: Natural language interaction with electronic manuals
- **Upload and Management**: Upload and manage multiple PDF manuals with metadata
- **Multilingual Support**: Automatic language detection and cross-language search capabilities
- **Advanced RAG System**: Retrieval-augmented generation with context-aware responses
- **Performance Optimized**: Direct manual filtering for faster search results
- **Dark/Light Mode**: Toggle between themes
- **Responsive Design**: Works on desktop and mobile devices

## Setup and Installation

### Requirements
- Node.js (v14+ recommended)
- Python (v3.8+ recommended)
- npm or yarn
- **Azure OpenAI API access** - Get access at https://azure.microsoft.com/en-us/products/cognitive-services/openai-service

### Frontend Setup

1. Install dependencies:
```bash
cd pravus-chatbot
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will run on http://localhost:3000

### Backend Setup

1. Navigate to server directory:
```bash
cd pravus-chatbot/server
```

2. Set up a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- macOS/Linux:
```bash
source venv/bin/activate
```

4. Install the required packages:
```bash
pip install -r requirements.txt
```

5. **IMPORTANT**: Set up your Azure OpenAI configuration by creating a `.env` file in the `server` directory:
```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_VERSION=your_api_version_here
AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment_here
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment_here
```

⚠️ **Security Note**: Never commit your API keys to version control. The `.env` file should be in your `.gitignore`.

Alternatively, set environment variables:
```bash
# On Windows
set AZURE_OPENAI_API_KEY=your_api_key_here
set AZURE_OPENAI_ENDPOINT=your_endpoint_here
set AZURE_OPENAI_API_VERSION=your_api_version_here
set AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment_here
set AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment_here

# On macOS/Linux
export AZURE_OPENAI_API_KEY=your_api_key_here
export AZURE_OPENAI_ENDPOINT=your_endpoint_here
export AZURE_OPENAI_API_VERSION=your_api_version_here
export AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment_here
export AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment_here
```

6. Run the Flask server:
```bash
python app.py
```

The backend API will run on http://localhost:5000

## Usage

### Uploading Manuals

1. Click "Upload Manual" button in the interface
2. Select a PDF file (max 16MB)
3. Fill in metadata:
   - **Brand**: Manufacturer name (e.g., "Samsung", "LG")
   - **Model**: Specific model number (e.g., "DC68-02657F", "SW80SP")
   - **Product Type**: Device category (e.g., "Washing Machine", "Dryer")
   - **Year**: Manufacturing year
   - **Language**: Document language (auto-detected if not specified)
4. Wait for processing to complete (embeddings are generated using Azure OpenAI)

### Chatting with Pravus

1. **Select Manual**: Choose specific brand/model from dropdown (recommended for best results)
2. **Ask Questions**: Type your question in natural language
3. **Get Answers**: Pravus searches through the selected manual and provides contextual answers
4. **Source Citations**: Responses include page references and source information

### Key Features:

- **Strict Manual Filtering**: When brand/model is selected, search is limited to that specific manual only
- **Semantic Search**: Understands context, synonyms, and meaning beyond keywords
- **Multilingual**: Works across different languages automatically

## Testing

To verify the setup:

```bash
cd server
# Test basic functionality
python -c "from document_processor import DocumentProcessor; dp = DocumentProcessor(); print('System ready!')"
```

## Cost Considerations

- **Azure OpenAI Usage**: Costs depend on your Azure subscription and chosen models
- **Storage**: Local FAISS index (no ongoing costs)
- Check current pricing at https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/

## Troubleshooting

### Common Issues:

1. **"No Azure OpenAI configuration"**: Ensure your `.env` file contains valid Azure OpenAI configuration
2. **"No documents found"**: Upload manuals first, ensure they processed successfully
3. **"Slow search"**: Restart Flask server to use optimized search algorithms
4. **"Cross-manual results"**: Select specific brand/model for strict filtering

### Performance Tips:

- Restart Flask server after code updates to use latest optimizations
- Use brand/model filtering for faster, more accurate results
- Keep manual metadata consistent for better organization

## Recent Updates

- ✅ **Optimized Search Algorithm**: Direct manual filtering for better performance
- ✅ **Strict Brand/Model Filtering**: Eliminates cross-manual contamination  
- ✅ **Enhanced Scoring**: Better relevance ranking with content-based boosting
- ✅ **Performance Improvements**: Faster search with reduced processing overhead

## Future Improvements

- User authentication and multi-tenant support
- Support for additional file formats (Word, Excel, etc.)
- Real-time collaborative manual analysis
- Advanced metadata extraction from documents
- Enhanced filtering and search capabilities

