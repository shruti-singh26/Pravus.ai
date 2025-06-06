import os
from dotenv import load_dotenv

# Load .env file from parent directory (project root)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# LLM Provider Selection
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'azure_openai').lower()  # 'openai', 'azure_openai', or 'deepseek'
# OpenAI Configuration (Used for embeddings and optionally for chat)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenAI Embeddings Configuration (Always used for document processing)
OPENAI_EMBEDDING_MODEL = os.environ.get('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')  # Cost-effective option
OPENAI_EMBEDDING_DIMENSIONS = int(os.environ.get('OPENAI_EMBEDDING_DIMENSIONS', 1536))  # Default for text-embedding-3-small

# OpenAI Chat Model Configuration
OPENAI_CHAT_MODEL = os.environ.get('OPENAI_CHAT_MODEL', 'gpt-3.5-turbo')  # Default chat model

# Deepseek Configuration (Alternative LLM provider)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_BASE = os.environ.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
DEEPSEEK_MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')

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

if LLM_PROVIDER == 'openai':
    DEFAULT_LLM_MODEL = OPENAI_CHAT_MODEL
elif LLM_PROVIDER == 'azure_openai':
    DEFAULT_LLM_MODEL = AZURE_OPENAI_CHAT_DEPLOYMENT
else:  # deepseek
    DEFAULT_LLM_MODEL = DEEPSEEK_MODEL

DEFAULT_LLM_TEMPERATURE = float(os.environ.get('DEFAULT_LLM_TEMPERATURE', 0.3))
DEFAULT_LLM_MAX_TOKENS = int(os.environ.get('DEFAULT_LLM_MAX_TOKENS', 500))
# Default RAG parameters
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_TOP_K = 4 