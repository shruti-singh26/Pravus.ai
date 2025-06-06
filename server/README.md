# Pravus.AI Server

This is the backend server for the Pravus.AI chatbot for electronic manuals.

## Setup Instructions

1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   Create a `.env` file in the server directory with the following content:
   
   ### Azure OpenAI Configuration
   ```
   # Azure OpenAI Configuration (Required)
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_API_VERSION=your_api_version_here
   AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment_here
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment_here

   # Storage paths
   VECTOR_DB_PATH=./vector_db
   UPLOAD_FOLDER=./uploads

   # Upload settings
   MAX_CONTENT_LENGTH=16777216  # 16MB
   ```

3. Run the server:
   ```
   python app.py
   ```

## Features

- PDF processing with text extraction and Azure OpenAI embeddings
- RAG (Retrieval-Augmented Generation) with Azure OpenAI
- FAISS vector database for fast semantic search
- Persistent storage of uploaded manuals
- Intelligent conversation summarization for support tickets
- Multi-language support
- Brand/model-specific manual filtering

## Azure OpenAI Configuration

### Required Settings
- **API Key**: Your Azure OpenAI API key
- **Endpoint**: Your Azure OpenAI service endpoint
- **API Version**: Azure OpenAI API version (e.g., "2023-05-15")
- **Chat Deployment**: Your GPT deployment name
- **Embedding Deployment**: Your embedding model deployment name

### Model Recommendations
- **Chat**: GPT-3.5-turbo or GPT-4 deployment
- **Embeddings**: text-embedding-ada-002 deployment

## Cost Considerations

- **Azure OpenAI Usage**: Costs depend on your Azure subscription and chosen models
- **Storage**: Local FAISS index (no ongoing costs)
- Check current pricing at https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/

## Performance Tips

- Use brand/model filtering for faster, more accurate results
- Keep manual metadata consistent for better organization
- Batch process documents for efficient embedding generation
- Includes rate limiting and retry logic for API stability

## Troubleshooting

### Common Issues:

1. **"No Azure OpenAI configuration"**: Check your `.env` file and environment variables
2. **"API rate limit"**: Adjust batch sizes or add delay between requests
3. **"Invalid deployment"**: Verify your deployment names in Azure OpenAI Studio
4. **"Token limit exceeded"**: Adjust chunk sizes in configuration

### Performance Optimization:

- Use appropriate chunk sizes for your content
- Enable strict filtering for faster searches
- Monitor Azure OpenAI usage and adjust as needed
- Regular maintenance of the vector store

## Recent Updates

- ✅ **Azure OpenAI Integration**: Full integration with Azure OpenAI services
- ✅ **Optimized Search**: Direct manual filtering for better performance
- ✅ **Enhanced Scoring**: Better relevance ranking with content-based boosting
- ✅ **Batch Processing**: Efficient document processing with rate limiting

## Future Improvements

- Enhanced Azure OpenAI integration features
- Advanced metadata extraction
- Improved multilingual support
- Extended document format support 