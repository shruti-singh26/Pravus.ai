# API Setup Guide

This document provides instructions for setting up Azure OpenAI API for use with Pravus.AI.

## Required API

Pravus.AI requires Azure OpenAI API configuration for both chat responses and embeddings.

## Azure OpenAI Setup

### Getting Azure OpenAI Access

1. Visit https://azure.microsoft.com/en-us/products/cognitive-services/openai-service
2. Sign up for an Azure account if you don't have one
3. Request access to Azure OpenAI Service
4. Once approved, create an Azure OpenAI resource in your Azure portal

### Setting Up Azure OpenAI Environment Variables

#### Option 1: Using environment variables directly

```bash
# On Windows (PowerShell)
$env:AZURE_OPENAI_API_KEY="your_api_key_here"
$env:AZURE_OPENAI_ENDPOINT="your_endpoint_here"
$env:AZURE_OPENAI_API_VERSION="your_api_version_here"
$env:AZURE_OPENAI_CHAT_DEPLOYMENT="your_chat_deployment_here"
$env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT="your_embedding_deployment_here"

# On Windows (Command Prompt)
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

#### Option 2: Using a .env file

Create a file named `.env` in the `server` directory with the following content:

```
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_VERSION=your_api_version_here
AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment_here
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment_here
```

## Azure OpenAI Configuration

Pravus.AI uses Azure OpenAI's models for both chat and embeddings:

- **Chat Model**: GPT-3.5 Turbo or GPT-4 (configurable via deployment)
- **Embeddings Model**: text-embedding-ada-002 (via deployment)
- **Features**: Multilingual support, semantic understanding, high accuracy

## Cost Considerations

### Azure OpenAI Pricing
- Pricing varies based on your Azure subscription and chosen models
- Check current pricing at https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/
- For a typical 200-page manual: Cost depends on your Azure pricing tier
- Query costs: Depends on your Azure pricing tier

## Verifying Setup

To verify that your Azure OpenAI configuration is working correctly:

1. Run the Flask application: `python app.py`
2. Check the console for initialization messages
3. Try uploading a manual (will show embedding processing)
4. Try chatting with Pravus

You should see messages like:
```
Initialized Azure OpenAI embeddings with deployment: your_embedding_deployment
DocumentProcessor initialization complete with X documents using Azure OpenAI embeddings.
```

## Testing Embeddings

Run the embedding test script to verify Azure OpenAI embeddings are working:

```bash
cd server
python test_embeddings.py
```

This will test semantic similarity and multilingual capabilities.

## Troubleshooting

If you encounter issues:

### 1. Azure OpenAI API Issues
- Verify your API key and endpoint are correct
- Check your internet connection
- Look at the server logs for API error messages
- Verify your API key has not reached its rate limit or usage quota
- Ensure your deployments are properly configured in Azure OpenAI Studio
- Check if your Azure subscription is active and has sufficient credits 