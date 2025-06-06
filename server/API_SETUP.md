# API Setup Guide

This document provides instructions for setting up APIs for use with Pravus.AI.

## Required APIs

Pravus.AI requires both Deepseek (for chat responses) and OpenAI (for embeddings) API keys to function properly.

## Deepseek API Setup (Required for Chat)

### Getting a Deepseek API Key

1. Visit https://deepseek.com and sign up for an account
2. Navigate to the API section of your account
3. Create a new API key and copy it

### Setting Up Deepseek Environment Variables

#### Option 1: Using environment variables directly

```bash
# On Windows (PowerShell)
$env:DEEPSEEK_API_KEY="your_api_key_here"

# On Windows (Command Prompt)
set DEEPSEEK_API_KEY=your_api_key_here

# On macOS/Linux
export DEEPSEEK_API_KEY=your_api_key_here
```

#### Option 2: Using a .env file

Create a file named `.env` in the `server` directory with the following content:

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

## OpenAI API Setup (Required for Embeddings)

### Getting an OpenAI API Key

1. Visit https://platform.openai.com and sign up for an account
2. Navigate to the API section
3. Create a new API key and copy it

### Setting Up OpenAI Environment Variables

#### Option 1: Using environment variables directly

```bash
# On Windows (PowerShell)
$env:OPENAI_API_KEY="your_openai_api_key_here"

# On Windows (Command Prompt)
set OPENAI_API_KEY=your_openai_api_key_here

# On macOS/Linux
export OPENAI_API_KEY=your_openai_api_key_here
```

#### Option 2: Using a .env file

Add these lines to your `.env` file in the `server` directory:

```
# Complete .env file example:
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
```

## OpenAI Embedding Configuration

Pravus.AI uses OpenAI's `text-embedding-3-small` model by default for the best balance of cost and performance:

- **Model**: `text-embedding-3-small`
- **Dimensions**: 1536
- **Cost**: $0.00002 per 1K tokens
- **Features**: Multilingual support, semantic understanding, high accuracy

### Alternative Models

You can configure different OpenAI embedding models:

```bash
# For higher accuracy (more expensive)
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSIONS=3072

# For lower cost (slightly less accurate)
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_EMBEDDING_DIMENSIONS=1536
```

## Cost Considerations

### OpenAI Embeddings Pricing
- **text-embedding-3-small**: $0.00002 per 1K tokens
- **text-embedding-3-large**: $0.00013 per 1K tokens
- **For a typical 200-page manual**: ~$0.01-0.05 total cost
- **Query embeddings**: ~$0.000001 per query

### Deepseek API Pricing
- Very cost-effective for chat responses
- Check current pricing at https://deepseek.com

## Verifying Setup

To verify that your API keys are working correctly:

1. Run the Flask application: `python app.py`
2. Check the console for initialization messages
3. Try uploading a manual (will show embedding processing)
4. Try chatting with Pravus

You should see messages like:
```
Initialized OpenAI embeddings with model: text-embedding-3-small (1536 dimensions)
DocumentProcessor initialization complete with X documents using OpenAI embeddings.
```

## Testing Embeddings

Run the embedding test script to verify OpenAI embeddings are working:

```bash
cd server
python test_embeddings.py
```

This will test semantic similarity and multilingual capabilities.

## Troubleshooting

If you encounter issues:

### 1. Deepseek API Issues
- Verify your API key is correct
- Check your internet connection
- Look at the server logs for API error messages
- Verify your API key has not reached its rate limit or usage quota

### 2. OpenAI API Issues
- Verify your OpenAI API key is correct
- Check you have sufficient credits in your OpenAI account
- Monitor for rate limiting (the system includes automatic retry logic)
- Ensure your API key has the necessary permissions

### 3. Common Error Messages

**"OPENAI_API_KEY is required"**
- Set your OpenAI API key in environment variables or .env file

**"Rate limit hit"**
- The system will automatically retry with exponential backoff
- Consider upgrading your OpenAI plan for higher rate limits

**"Insufficient credits"**
- Add credits to your OpenAI account at https://platform.openai.com

### 4. Performance Tips

- **Batch processing**: The system automatically batches embedding requests
- **Caching**: Embeddings are cached in the FAISS index
- **Cost optimization**: Using text-embedding-3-small for best cost/performance ratio 