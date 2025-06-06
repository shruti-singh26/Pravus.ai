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
   
   ### LLM Provider Configuration
   ```
   # Choose your LLM provider: 'openai' or 'deepseek'
   LLM_PROVIDER=openai
   
   # OpenAI Configuration (Required for embeddings, optional for chat if using Deepseek)
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_CHAT_MODEL=gpt-3.5-turbo
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   OPENAI_EMBEDDING_DIMENSIONS=1536
   
   # Deepseek Configuration (Optional - only if using Deepseek for chat)
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   DEEPSEEK_API_BASE=https://api.deepseek.com/v1
   DEEPSEEK_MODEL=deepseek-chat

   # Storage paths
   VECTOR_DB_PATH=./vector_db
   UPLOAD_FOLDER=./uploads

   # Upload settings
   MAX_CONTENT_LENGTH=16777216  # 16MB
   ```

   ### Provider Options:
   
   **Option 1: OpenAI Only (Recommended for simplicity)**
   ```
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   **Option 2: Deepseek for Chat + OpenAI for Embeddings (Cost-effective)**
   ```
   LLM_PROVIDER=deepseek
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # Still needed for embeddings
   ```

3. Run the server:
   ```
   python app.py
   ```

## Features

- PDF processing with text extraction and OpenAI embeddings
- RAG (Retrieval-Augmented Generation) with configurable LLM providers
- FAISS vector database for fast semantic search
- Persistent storage of uploaded manuals
- Intelligent conversation summarization for support tickets
- Multi-language support
- Brand/model-specific manual filtering

## LLM Provider Options

### OpenAI (Default)
- **Chat Model**: GPT-3.5-turbo (default) or GPT-4
- **Embeddings**: text-embedding-3-small
- **Pros**: High quality, reliable, well-tested
- **Cons**: Higher cost per token

### Deepseek
- **Chat Model**: deepseek-chat
- **Embeddings**: Uses OpenAI (Deepseek doesn't provide embeddings)
- **Pros**: Very cost-effective, good performance
- **Cons**: Requires two API keys (Deepseek + OpenAI)

## API Configuration

### Single Provider (OpenAI)
Set `LLM_PROVIDER=openai` and provide only `OPENAI_API_KEY`. This uses OpenAI for both chat and embeddings.

### Hybrid Setup (Deepseek + OpenAI)
Set `LLM_PROVIDER=deepseek` and provide both:
- `DEEPSEEK_API_KEY` for chat completions
- `OPENAI_API_KEY` for embeddings (required)

**Note**: OpenAI embeddings are always required for document processing, regardless of chat provider.

## Cost Optimization

- **Most Cost-Effective**: Deepseek for chat + OpenAI embeddings
- **Simplest Setup**: OpenAI for everything
- **Performance**: Both providers offer excellent quality
- Includes batch processing, rate limiting, and retry logic

## Switching Providers

You can easily switch between providers by changing the `LLM_PROVIDER` environment variable:
- `LLM_PROVIDER=openai` - Use OpenAI for chat
- `LLM_PROVIDER=deepseek` - Use Deepseek for chat

No code changes required - just restart the server after updating the environment variable. 