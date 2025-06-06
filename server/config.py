import os
from dotenv import load_dotenv

# Load .env file from parent directory (project root)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# LLM Provider Selection - only Azure OpenAI supported
LLM_PROVIDER = 'azure_openai'

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION')
AZURE_OPENAI_CHAT_DEPLOYMENT = os.environ.get('AZURE_OPENAI_CHAT_DEPLOYMENT')
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get('AZURE_OPENAI_EMBEDDING_DEPLOYMENT')

# Vector DB settings
VECTOR_DB_PATH = os.environ.get('VECTOR_DB_PATH', './vector_db')

# Upload settings
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # Default 16MB

# Manual metadata structure
MANUAL_FIELDS = ['brand', 'model', 'product_type', 'year', 'language']

# Default model
DEFAULT_LLM_MODEL = AZURE_OPENAI_CHAT_DEPLOYMENT

DEFAULT_LLM_TEMPERATURE = float(os.environ.get('DEFAULT_LLM_TEMPERATURE', 0.3))
DEFAULT_LLM_MAX_TOKENS = int(os.environ.get('DEFAULT_LLM_MAX_TOKENS', 500))

# Default RAG parameters
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_TOP_K = 4 