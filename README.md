# Pravus.AI Chatbot

A React and Flask application for interacting with electronic manuals, leveraging advanced retrieval-augmented generation (RAG) capabilities with OpenAI embeddings and Deepseek API.

## Project Structure

The project consists of two parts:
- `src/`: React frontend
- `server/`: Flask backend API with RAG system for manuals

## Features

- **Smart Manual Search**: Advanced semantic search using OpenAI embeddings with optimized filtering
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
- **Deepseek API key** (for chat responses) - Get free trial at https://deepseek.com
- **OpenAI API key** (for embeddings) - Get at https://platform.openai.com

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

5. **IMPORTANT**: Set up your API keys by creating a `.env` file in the `server` directory:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

⚠️ **Security Note**: Never commit your API keys to version control. The `.env` file should be in your `.gitignore`.

Alternatively, set environment variables:
```bash
# On Windows
set DEEPSEEK_API_KEY=your_deepseek_api_key_here
set OPENAI_API_KEY=your_openai_api_key_here

# On macOS/Linux
export DEEPSEEK_API_KEY=your_deepseek_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
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
4. Wait for processing to complete (embeddings are generated using OpenAI)

### Chatting with Pravus

1. **Select Manual**: Choose specific brand/model from dropdown (recommended for best results)
2. **Ask Questions**: Type your question in natural language
3. **Get Answers**: Pravus searches through the selected manual and provides contextual answers
4. **Source Citations**: Responses include page references and source information

### Key Features:

- **Strict Manual Filtering**: When brand/model is selected, search is limited to that specific manual only
- **Semantic Search**: Understands context, synonyms, and meaning beyond keywords
- **Multilingual**: Works across different languages automatically
- **Performance Optimized**: Fast search with direct manual filtering (no cross-contamination)

## API Endpoints

### Health Check
- `GET /api/health` - Check system status and loaded models

### Chat
- `POST /api/chat` - Send message and get response based on uploaded manuals
  - Body: `{"message": "your question", "brand": "optional", "model": "optional"}`

### File Management
- `POST /api/upload` - Upload PDF with metadata
- `GET /api/files` - Get list of all uploaded files
- `DELETE /api/files/<file_id>` - Delete specific file

### Metadata
- `GET /api/brands` - Get list of all available brands
- `GET /api/models` - Get models (optionally filtered by brand)

## RAG Implementation Details

The system uses an advanced retrieval-augmented generation approach with recent optimizations:

### Architecture:
1. **Document Processing**: PDFs chunked using LangChain with smart text splitting
2. **Semantic Embeddings**: OpenAI `text-embedding-3-small` model (1536 dimensions)
3. **Vector Storage**: FAISS for efficient similarity search
4. **Optimized Retrieval**: Direct manual filtering for performance
5. **Response Generation**: Deepseek API for contextual answers

### Recent Optimizations:
- **Direct Manual Filtering**: Eliminates cross-manual contamination
- **Performance Enhancement**: Searches only relevant document chunks
- **Smart Scoring**: Content-based boosting for better relevance
- **Strict Filtering**: When brand/model specified, no fallback to other manuals

### Key Advantages:
- **High Accuracy**: Superior semantic understanding with OpenAI embeddings
- **Fast Performance**: Optimized search algorithms
- **Cost Effective**: Efficient use of `text-embedding-3-small`
- **Multilingual**: Single index handles multiple languages
- **Manual Isolation**: Prevents information mixing between different device manuals

## Testing

The system includes comprehensive testing capabilities. You can test various components:

```bash
cd server
# Test basic functionality
python -c "from document_processor import DocumentProcessor; dp = DocumentProcessor(); print('System ready!')"
```

## Cost Considerations

- **OpenAI Embeddings**: ~$0.01-0.05 per 200-page manual (one-time cost)
- **Query Processing**: ~$0.000001 per search query
- **Deepseek API**: Very cost-effective for chat responses (~$0.001 per response)
- **Storage**: Local FAISS index (no ongoing costs)

## Troubleshooting

### Common Issues:

1. **"No OpenAI API key"**: Ensure your `.env` file contains valid `OPENAI_API_KEY`
2. **"No documents found"**: Upload manuals first, ensure they processed successfully
3. **Slow search**: Restart Flask server to use optimized search algorithms
4. **Cross-manual results**: Select specific brand/model for strict filtering

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
- Integration with more LLM providers

