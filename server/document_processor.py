import os
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime
import langdetect
import time

import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document
import faiss
import openai

from config import (
    UPLOAD_FOLDER,
    VECTOR_DB_PATH,
    LLM_PROVIDER,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_DIMENSIONS,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT
)

class OpenAIEmbeddings:
    """OpenAI embeddings class with cost optimization and error handling."""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set your OpenAI API key in the environment variables.")
        
        openai.api_key = OPENAI_API_KEY
        self.model = OPENAI_EMBEDDING_MODEL
        self.dimensions = OPENAI_EMBEDDING_DIMENSIONS
        print(f"Initialized OpenAI embeddings with model: {self.model} ({self.dimensions} dimensions)")
    
    def _make_embedding_request(self, texts: List[str], retry_count: int = 3):
        """Make embedding request with retry logic and rate limiting."""
        for attempt in range(retry_count):
            try:
                response = openai.Embedding.create(
                    input=texts,
                    model=self.model
                )
                return response
            except openai.error.RateLimitError as e:
                if attempt < retry_count - 1:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff with minimum 1 second
                    print(f"      ⏳ Rate limit hit, waiting {wait_time} seconds... (attempt {attempt + 1}/{retry_count})")
                    time.sleep(wait_time)
                else:
                    print(f"      ❌ Rate limit exceeded after {retry_count} attempts")
                    raise e
            except openai.error.Timeout as e:
                if attempt < retry_count - 1:
                    wait_time = 3 + attempt  # Longer wait for timeouts
                    print(f"      ⏳ Request timeout, waiting {wait_time} seconds... (attempt {attempt + 1}/{retry_count})")
                    time.sleep(wait_time)
                else:
                    print(f"      ❌ Request timeout after {retry_count} attempts")
                    raise e
            except Exception as e:
                if attempt < retry_count - 1:
                    wait_time = 1 + attempt
                    print(f"      ⏳ OpenAI API error: {str(e)}, retrying in {wait_time} seconds... (attempt {attempt + 1}/{retry_count})")
                    time.sleep(wait_time)
                else:
                    print(f"      ❌ OpenAI API error after {retry_count} attempts: {str(e)}")
                    raise e
    
    def embed_documents(self, texts: List[str]) -> np.ndarray:
        """Convert documents to OpenAI embeddings with adaptive batch processing."""
        if not texts:
            return np.zeros((1, self.dimensions), dtype=np.float32)
        
        print(f"🧠 Generating embeddings for {len(texts)} text chunks...")
        
        # Adaptive batch sizing - start large, reduce if errors occur
        initial_batch_size = 75  # Start with 75 (between 50 and 100)
        min_batch_size = 25      # Minimum batch size if errors persist
        current_batch_size = initial_batch_size
        consecutive_errors = 0
        
        all_embeddings = []
        i = 0
        
        while i < len(texts):
            batch = texts[i:i + current_batch_size]
            batch_num = len(all_embeddings) // initial_batch_size + 1
            total_estimated_batches = (len(texts) + initial_batch_size - 1) // initial_batch_size
            
            print(f"   Processing batch {batch_num} with size {current_batch_size} ({len(batch)} chunks)")
            
            try:
                response = self._make_embedding_request(batch)
                batch_embeddings = [item['embedding'] for item in response['data']]
                all_embeddings.extend(batch_embeddings)
                print(f"   ✅ Batch completed successfully")
                
                # Success - can try increasing batch size next time
                consecutive_errors = 0
                if current_batch_size < initial_batch_size:
                    current_batch_size = min(current_batch_size + 10, initial_batch_size)
                    print(f"   📈 Increasing batch size to {current_batch_size}")
                
                # Move to next batch
                i += len(batch)
                
                # Small delay between batches to be respectful to API
                if i < len(texts):
                    time.sleep(0.05)  # Reduced delay for speed
                    
            except Exception as e:
                print(f"   ❌ Error processing batch: {str(e)}")
                consecutive_errors += 1
                
                # Reduce batch size if getting errors
                if consecutive_errors >= 2 and current_batch_size > min_batch_size:
                    current_batch_size = max(current_batch_size // 2, min_batch_size)
                    print(f"   📉 Reducing batch size to {current_batch_size} due to errors")
                
                # Add zero vectors for failed batch and continue
                batch_embeddings = [np.zeros(self.dimensions).tolist() for _ in batch]
                all_embeddings.extend(batch_embeddings)
                i += len(batch)
        
        embeddings_array = np.array(all_embeddings, dtype=np.float32)
        print(f"✅ Generated {len(embeddings_array)} embeddings with shape {embeddings_array.shape}")
        return embeddings_array
    
    def embed_query(self, text: str) -> np.ndarray:
        """Convert query to OpenAI embedding."""
        if not text:
            return np.zeros(self.dimensions, dtype=np.float32)
        
        try:
            response = self._make_embedding_request([text])
            embedding = response['data'][0]['embedding']
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            print(f"Error embedding query: {str(e)}")
            return np.zeros(self.dimensions, dtype=np.float32)

class AzureOpenAIEmbeddings:
    """Azure OpenAI embeddings class with cost optimization and error handling."""

    def __init__(self):
        if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are required. Please set your Azure OpenAI configuration in the environment variables.")

        # Configure Azure OpenAI
        openai.api_type = "azure"
        openai.api_key = AZURE_OPENAI_API_KEY
        openai.api_base = AZURE_OPENAI_ENDPOINT
        openai.api_version = AZURE_OPENAI_API_VERSION

        self.deployment_name = AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        self.dimensions = OPENAI_EMBEDDING_DIMENSIONS  # Azure OpenAI uses same dimensions
        print(f"Initialized Azure OpenAI embeddings with deployment: {self.deployment_name} ({self.dimensions} dimensions)")

    def _make_embedding_request(self, texts: List[str], retry_count: int = 3):
        """Make embedding request with retry logic and rate limiting."""
        for attempt in range(retry_count):
            try:
                response = openai.Embedding.create(
                    input=texts,
                    engine=self.deployment_name  # Use engine for Azure
                )
                return response
            except openai.error.RateLimitError as e:
                if attempt < retry_count - 1:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff with minimum 1 second
                    print(f"      ⏳ Rate limit hit, waiting {wait_time} seconds... (attempt {attempt + 1}/{retry_count})")
                    time.sleep(wait_time)
                else:
                    print(f"      ❌ Rate limit exceeded after {retry_count} attempts")
                    raise e
            except openai.error.Timeout as e:
                if attempt < retry_count - 1:
                    wait_time = 3 + attempt  # Longer wait for timeouts
                    print(f"      ⏳ Request timeout, waiting {wait_time} seconds... (attempt {attempt + 1}/{retry_count})")
                    time.sleep(wait_time)
                else:
                    print(f"      ❌ Request timeout after {retry_count} attempts")
                    raise e
            except Exception as e:
                if attempt < retry_count - 1:
                    wait_time = 1 + attempt
                    print(f"      ⏳ Azure OpenAI API error: {str(e)}, retrying in {wait_time} seconds... (attempt {attempt + 1}/{retry_count})")
                    time.sleep(wait_time)
                else:
                    print(f"      ❌ Azure OpenAI API error after {retry_count} attempts: {str(e)}")
                    raise e

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        """Convert documents to Azure OpenAI embeddings with adaptive batch processing."""
        if not texts:
            return np.zeros((1, self.dimensions), dtype=np.float32)

        print(f"🧠 Generating embeddings for {len(texts)} text chunks using Azure OpenAI...")

        # Adaptive batch sizing - start large, reduce if errors occur
        initial_batch_size = 75  # Start with 75 (between 50 and 100)
        min_batch_size = 25      # Minimum batch size if errors persist
        current_batch_size = initial_batch_size
        consecutive_errors = 0

        all_embeddings = []
        i = 0

        while i < len(texts):
            batch = texts[i:i + current_batch_size]
            batch_num = len(all_embeddings) // initial_batch_size + 1
            total_estimated_batches = (len(texts) + initial_batch_size - 1) // initial_batch_size

            print(f"   Processing batch {batch_num} with size {current_batch_size} ({len(batch)} chunks)")

            try:
                response = self._make_embedding_request(batch)
                batch_embeddings = [item['embedding'] for item in response['data']]
                all_embeddings.extend(batch_embeddings)
                print(f"   ✅ Batch completed successfully")

                # Success - can try increasing batch size next time
                consecutive_errors = 0
                if current_batch_size < initial_batch_size:
                    current_batch_size = min(current_batch_size + 10, initial_batch_size)
                    print(f"   📈 Increasing batch size to {current_batch_size}")

                # Move to next batch
                i += len(batch)

                # Small delay between batches to be respectful to API
                if i < len(texts):
                    time.sleep(0.05)  # Reduced delay for speed

            except Exception as e:
                print(f"   ❌ Error processing batch: {str(e)}")
                consecutive_errors += 1

                # Reduce batch size if getting errors
                if consecutive_errors >= 2 and current_batch_size > min_batch_size:
                    current_batch_size = max(current_batch_size // 2, min_batch_size)
                    print(f"   📉 Reducing batch size to {current_batch_size} due to errors")

                # Add zero vectors for failed batch and continue
                batch_embeddings = [np.zeros(self.dimensions).tolist() for _ in batch]
                all_embeddings.extend(batch_embeddings)
                i += len(batch)

        embeddings_array = np.array(all_embeddings, dtype=np.float32)
        print(f"✅ Generated {len(embeddings_array)} embeddings with shape {embeddings_array.shape}")
        return embeddings_array

    def embed_query(self, text: str) -> np.ndarray:
        """Convert query to Azure OpenAI embedding."""
        if not text:
            return np.zeros(self.dimensions, dtype=np.float32)

        try:
            response = self._make_embedding_request([text])
            embedding = response['data'][0]['embedding']
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            print(f"Error embedding query: {str(e)}")
            return np.zeros(self.dimensions, dtype=np.float32)

class DocumentProcessor:
    """Handles PDF processing, chunking, and embedding using OpenAI embeddings."""
    
    def __init__(self):
        self.upload_dir = UPLOAD_FOLDER
        self.vector_db_dir = VECTOR_DB_PATH
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.vector_db_dir, exist_ok=True)
        
        print("Initializing DocumentProcessor with OpenAI embeddings...")
        
        # Initialize OpenAI embeddings
        try:
            if LLM_PROVIDER == 'azure_openai':
                self.embeddings = AzureOpenAIEmbeddings()
                print("Using Azure OpenAI for embeddings")
            else:
                self.embeddings = OpenAIEmbeddings()
                print("Using regular OpenAI for embeddings")
            self.embedding_dimensions = OPENAI_EMBEDDING_DIMENSIONS
        except ValueError as e:
            print(f"Error: {str(e)}")
            if LLM_PROVIDER == 'azure_openai':
                print("Please set your Azure OpenAI configuration environment variables to use Pravus.AI")
            else:
                print("Please set your OPENAI_API_KEY environment variable to use Pravus.AI")
            raise
        
        # Initialize single multilingual FAISS index (OpenAI handles all languages well)
        self.index = faiss.IndexFlatL2(self.embedding_dimensions)
        
        # Load existing index if available
        index_path = os.path.join(self.vector_db_dir, "manual_index.faiss")
        if os.path.exists(index_path):
            try:
                loaded_index = faiss.read_index(index_path)
                if loaded_index.d == self.embedding_dimensions:
                    self.index = loaded_index
                    print(f"Loaded existing index with {loaded_index.ntotal} vectors")
                else:
                    print(f"Dimension mismatch in saved index. Expected {self.embedding_dimensions}, got {loaded_index.d}. Creating new index.")
            except Exception as e:
                print(f"Error loading index: {str(e)}. Creating new index.")
        
        # Load documents and metadata
        print("Loading documents and metadata...")
        self.documents = self._load_documents() or []
        self.metadata = self._load_metadata() or {}
        
        # Validate consistency between documents and index
        if self.documents and self.index.ntotal != len(self.documents):
            print(f"⚠️  Inconsistency detected: {len(self.documents)} documents but {self.index.ntotal} vectors in index")
            print("This is normal on first load or after updates. Index will be rebuilt when needed.")
            # Note: We don't rebuild here to avoid unnecessary processing on every startup
            # The index will be rebuilt only when actually needed (e.g., during search if mismatch detected)
        elif self.documents:
            print(f"✅ Consistency check passed: {len(self.documents)} documents match {self.index.ntotal} vectors")
        
        print(f"DocumentProcessor initialization complete with {len(self.documents)} documents using OpenAI embeddings.")
    
    def _save_index(self):
        """Save FAISS index to disk with proper error handling."""
        try:
            # Ensure the directory exists
            os.makedirs(self.vector_db_dir, exist_ok=True)
            
            # Use proper path normalization for Windows
            index_path = os.path.normpath(os.path.join(self.vector_db_dir, "manual_index.faiss"))
            
            # Create a temporary file first to avoid corruption
            temp_path = index_path + ".tmp"
            
            print(f"💾 Saving FAISS index to: {index_path}")
            
            # Save to temporary file first
            faiss.write_index(self.index, temp_path)
            
            # Remove old file if it exists and move temp file to final location
            if os.path.exists(index_path):
                try:
                    os.remove(index_path)
                except OSError as e:
                    print(f"Warning: Could not remove old index file: {e}")
            
            # Move temp file to final location
            os.rename(temp_path, index_path)
            print(f"✅ FAISS index saved successfully")
            
        except Exception as e:
            print(f"❌ Error saving FAISS index: {str(e)}")
            # Clean up temp file if it exists
            temp_path = os.path.normpath(os.path.join(self.vector_db_dir, "manual_index.faiss.tmp"))
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            raise Exception(f"Failed to save FAISS index: {str(e)}")
    
     
    def get_retriever(self):
        return self  # or return a specific retriever object if you have one 

    def _load_documents(self) -> List[Document]:
        """Load document chunks if they exist."""
        doc_path = os.path.join(self.vector_db_dir, "documents.json")
        
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                docs_data = json.load(f)
                
            return [
                Document(
                    page_content=doc['page_content'],
                    metadata=doc['metadata']
                )
                for doc in docs_data
            ]
        
        return []
    
    def _load_metadata(self) -> Dict:
        """Load manual metadata if it exists."""
        meta_path = os.path.join(self.vector_db_dir, "metadata.json")
        
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}
    
    def _save_documents(self):
        """Save document chunks to disk with error handling."""
        try:
            doc_path = os.path.normpath(os.path.join(self.vector_db_dir, "documents.json"))
            
            docs_data = [
                {
                    'page_content': doc.page_content,
                    'metadata': doc.metadata
                }
                for doc in self.documents
            ]
            
            # Ensure directory exists
            os.makedirs(self.vector_db_dir, exist_ok=True)
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                json.dump(docs_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise Exception(f"Failed to save documents: {str(e)}")
    
    def _save_metadata(self):
        """Save manual metadata to disk with error handling."""
        try:
            meta_path = os.path.normpath(os.path.join(self.vector_db_dir, "metadata.json"))
            
            # Ensure directory exists
            os.makedirs(self.vector_db_dir, exist_ok=True)
            
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise Exception(f"Failed to save metadata: {str(e)}")
    
    def _save_state(self):
        """Save all state to disk: index, documents, and metadata with error handling."""
        print("💾 Saving all state to disk...")
        
        errors = []
        success_count = 0
        
        # Save FAISS index
        try:
            self._save_index()
            success_count += 1
        except Exception as e:
            error_msg = f"Failed to save FAISS index: {str(e)}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
        
        # Save documents
        try:
            self._save_documents()
            print("✅ Documents saved successfully")
            success_count += 1
        except Exception as e:
            error_msg = f"Failed to save documents: {str(e)}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
        
        # Save metadata
        try:
            self._save_metadata()
            print("✅ Metadata saved successfully")
            success_count += 1
        except Exception as e:
            error_msg = f"Failed to save metadata: {str(e)}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
        
        # Report results
        if errors:
            print(f"⚠️  Partial save completed: {success_count}/3 operations successful")
            for error in errors:
                print(f"   - {error}")
            # Still raise an exception if critical components failed
            if success_count == 0:
                raise Exception("All save operations failed: " + "; ".join(errors))
        else:
            print("✅ All state saved successfully")
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        try:
            return langdetect.detect(text)
        except:
            return 'en'  # Default to English if detection fails
    
    def process_pdf(self, file_path: str, metadata: Dict) -> str:
        """Process a PDF file and add it to the vector store."""
        try:
            print(f"🔄 Starting PDF processing for: {os.path.basename(file_path)}")
            
            # Generate a unique file ID
            file_id = self._generate_file_id(file_path)
            print(f"📝 Generated file ID: {file_id}")
            
            # Load and process the PDF
            print("📖 Loading PDF pages...")
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            print(f"📄 Loaded {len(pages)} pages from PDF")
            
            if not pages:
                raise ValueError("No content found in PDF")
            
            # Detect document language if not provided
            doc_language = metadata.get('language', 'en')
            
            # Enhanced text splitting with better chunking strategy
            print("✂️ Starting text chunking...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""],  # Order matters
                keep_separator=True
            )
            
            # Process each page and maintain metadata
            all_chunks = []
            print("📝 Processing pages and creating chunks...")
            for i, page in enumerate(pages):
                if i % 5 == 0:  # Log progress every 5 pages
                    print(f"   Processing page {i+1}/{len(pages)}")
                
                # Extract and clean the text
                page_text = page.page_content
                
                # Preserve important formatting
                page_text = page_text.replace('\n\n', '[PARA]')  # Mark paragraphs
                page_text = page_text.replace('\n', ' ')  # Replace single newlines
                page_text = page_text.replace('[PARA]', '\n\n')  # Restore paragraphs
                
                # Create the page document with cleaned text
                page_doc = Document(
                    page_content=page_text,
                    metadata=page.metadata
                )
                
                # Split into chunks
                chunks = text_splitter.split_documents([page_doc])
                
                for j, chunk in enumerate(chunks):
                    # Preserve user-provided metadata and add chunk-specific metadata
                    chunk.metadata.update({
                        'file_id': file_id,
                        'page': i + 1,
                        'chunk': j + 1,
                        'total_chunks_in_page': len(chunks),
                        'filename': os.path.basename(file_path),
                        'brand': metadata.get('brand', 'Unknown'),
                        'model': metadata.get('model', 'Unknown'),
                        'product_type': metadata.get('product_type', 'Unknown'),
                        'year': metadata.get('year', str(datetime.now().year)),
                        'language': doc_language,
                        'timestamp': datetime.now().isoformat(),
                        'is_start_of_page': j == 0,
                        'is_end_of_page': j == len(chunks) - 1
                    })
                    
                    # Add context from adjacent chunks if available
                    if j > 0:
                        chunk.metadata['prev_chunk_preview'] = chunks[j-1].page_content[-100:]
                    if j < len(chunks) - 1:
                        chunk.metadata['next_chunk_preview'] = chunks[j+1].page_content[:100]
                    
                    all_chunks.append(chunk)
            
            print(f"📊 Created {len(all_chunks)} chunks total")
            
            # Get embeddings for all chunks at once
            print("🧠 Generating embeddings using OpenAI API...")
            print(f"   Processing {len(all_chunks)} chunks for embedding generation")
            texts = [chunk.page_content for chunk in all_chunks]
            embeddings = self.embeddings.embed_documents(texts)
            print("✅ Embedding generation completed")
            
            # Add to FAISS index
            print("💾 Adding embeddings to FAISS index...")
            self.index.add(np.array(embeddings).astype('float32'))
            print("✅ FAISS index updated")
            
            # Update documents and metadata
            start_idx = len(self.documents)
            self.documents.extend(all_chunks)
            
            # Store metadata
            self.metadata[file_id] = {
                'filename': os.path.basename(file_path),
                'brand': metadata.get('brand', 'Unknown'),
                'model': metadata.get('model', 'Unknown'),
                'product_type': metadata.get('product_type', 'Unknown'),
                'year': metadata.get('year', str(datetime.now().year)),
                'timestamp': datetime.now().isoformat(),
                'num_pages': len(pages),
                'num_chunks': len(all_chunks),
                'start_idx': start_idx,
                'end_idx': start_idx + len(all_chunks),
                'chunks_per_page': [len(text_splitter.split_documents([page])) for page in pages],
                'total_tokens': sum(len(chunk.page_content.split()) for chunk in all_chunks),
                'language': doc_language
            }
            
            # Save state
            print("💾 Saving database state...")
            self._save_state()
            print(f"🎉 PDF processing completed successfully! File ID: {file_id}")
            
            return file_id
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            raise
    
    def delete_document(self, file_id: str) -> bool:
        """
        Completely delete a document and its associated data from the system.
        
        Args:
            file_id: Unique ID of the file to delete
            
        Returns:
            success: Whether the deletion was successful
        """
        if file_id not in self.metadata:
            return False
        
        try:
            # Get document indices for this file
            start_idx = self.metadata[file_id]['start_idx']
            end_idx = self.metadata[file_id]['end_idx']
            num_chunks = end_idx - start_idx
            
            # Remove documents from the list
            self.documents = self.documents[:start_idx] + self.documents[end_idx:]
            
            # Update metadata indices for all files that come after this one
            for meta in self.metadata.values():
                if meta['start_idx'] > start_idx:
                    meta['start_idx'] -= num_chunks
                    meta['end_idx'] -= num_chunks
            
            # Remove from metadata
            del self.metadata[file_id]
            
            # Rebuild the index with remaining documents
            print("Rebuilding index after document deletion...")
            self.index = faiss.IndexFlatL2(self.embedding_dimensions)
            
            if self.documents:  # Only rebuild if we have documents
                # Get embeddings for all remaining documents
                texts = [doc.page_content for doc in self.documents]
                try:
                    embeddings = self.embeddings.embed_documents(texts)
                    self.index.add(np.array(embeddings).astype('float32'))
                except Exception as e:
                    print(f"Error rebuilding embeddings: {str(e)}")
                    raise
            
            # Save updated state
            self._save_state()
            
            print(f"Successfully deleted document {file_id} and rebuilt index")
            return True
            
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False
    
    def get_all_manuals(self) -> List[Dict]:
        """Get metadata for all manuals in the system."""
        try:
            # Check if metadata is available
            if not hasattr(self, 'metadata') or self.metadata is None:
                print("Warning: metadata not initialized, returning empty list")
                return []
            
            return [
                {
                    'file_id': file_id,
                    'filename': data['filename'],
                    'brand': data.get('brand', 'Unknown'),
                    'model': data.get('model', 'Unknown'),
                    'timestamp': data['timestamp']
                }
                for file_id, data in self.metadata.items()
            ]
        except Exception as e:
            print(f"Error in get_all_manuals: {str(e)}")
            return []  # Return empty list instead of failing
    
    def similarity_search(
        self, 
        query: str, 
        language: str = 'en',
        brand: Optional[str] = None,
        model: Optional[str] = None,
        k: int = 4,
        include_deleted: bool = False
    ) -> List[Document]:
        """
        Search for similar documents to the query.
        
        Args:
            query: The search query
            language: The preferred language (OpenAI embeddings work across languages)
            brand: Optional filter for specific brand (STRICT filtering when provided)
            model: Optional filter for specific model (STRICT filtering when provided)
            k: Number of results to return
            include_deleted: Whether to include documents marked as deleted
            
        Returns:
            docs: List of Documents similar to the query
        """
        if not self.documents:
            print("No documents available for search")
            return []
        
        print(f"🔍 Searching for: '{query}'")
        print(f"📚 Total documents in database: {len(self.documents)}")
        print(f"🎯 Filters - Brand: {brand}, Model: {model}")
        
        # If brand/model specified, directly find matching manuals first
        if brand or model:
            print(f"🔒 STRICT FILTERING: Only searching within {brand or 'any'} {model or 'any'} documents")
            
            # Find matching manual(s) by metadata
            matching_manuals = []
            for file_id, manual_meta in self.metadata.items():
                # Skip deleted manuals
                if not include_deleted and manual_meta.get('is_deleted', False):
                    continue
                
                # Check brand/model match
                manual_brand = manual_meta.get('brand', '').strip()
                manual_model = manual_meta.get('model', '').strip()
                
                brand_match = not brand or manual_brand == brand
                model_match = not model or manual_model == model
                
                if brand_match and model_match:
                    matching_manuals.append({
                        'file_id': file_id,
                        'brand': manual_brand,
                        'model': manual_model,
                        'start_idx': manual_meta['start_idx'],
                        'end_idx': manual_meta['end_idx'],
                        'num_chunks': manual_meta['num_chunks']
                    })
            
            print(f"📋 Found {len(matching_manuals)} matching manual(s):")
            for manual in matching_manuals:
                print(f"   - {manual['brand']} {manual['model']} ({manual['num_chunks']} chunks)")
            
            if not matching_manuals:
                print(f"❌ No manuals found for {brand or 'any'} {model or 'any'}")
                return []
            
            # Use existing index and filter results instead of recreating embeddings
            query_embedding = self.embeddings.embed_query(query)
            search_k = min(k * 10, len(self.documents))  # Search more to get better results
            D, I = self.index.search(
                np.array([query_embedding], dtype=np.float32), 
                k=search_k
            )
            
            print(f"🔎 Index search returned {len(I[0])} results")
            
            # Filter results to only include documents from matching manuals
            docs_with_scores = []
            for i, doc_idx in enumerate(I[0]):
                if doc_idx < len(self.documents):
                    doc = self.documents[doc_idx]
                    score = D[0][i]
                    
                    # Check if this document belongs to one of the matching manuals
                    doc_file_id = doc.metadata.get('file_id')
                    if any(manual['file_id'] == doc_file_id for manual in matching_manuals):
                        
                        print(f"  📄 Doc {len(docs_with_scores)+1}: Score={score:.4f}, Brand={doc.metadata.get('brand')}, Model={doc.metadata.get('model')}")
                        print(f"      Content preview: {doc.page_content[:100]}...")
                        
                        # Apply content-based scoring improvements
                        query_lower = query.lower()
                        content_lower = doc.page_content.lower()
                        
                        # Boost for exact phrase matches
                        if query_lower in content_lower:
                            score = score * 0.7
                            print(f"      🎯 EXACT PHRASE MATCH BOOST")
                        
                        # Boost for multiple word matches
                        query_words = query_lower.split()
                        word_matches = sum(1 for word in query_words if word in content_lower)
                        if word_matches > 1:
                            boost_factor = 1.0 - (word_matches * 0.05)
                            score = score * boost_factor
                            print(f"      🎯 WORD MATCH BOOST: {word_matches} words")
                        
                        # Special boosting for program/cycle queries
                        program_keywords = ['program', 'cycle', 'course', 'setting', 'mode', 'function']
                        if any(keyword in query_lower for keyword in program_keywords):
                            content_length = len(doc.page_content)
                            if content_length > 500:
                                score = score * 0.8
                                print(f"      🎯 DETAILED CONTENT BOOST: {content_length} chars")
                            
                            instructional_terms = ['press', 'select', 'button', 'follow', 'step', 'wash', 'rinse', 'spin', 'temperature', 'time', 'recommended', 'use']
                            instruction_matches = sum(1 for term in instructional_terms if term in content_lower)
                            if instruction_matches >= 3:
                                score = score * 0.85
                                print(f"      🎯 INSTRUCTIONAL CONTENT BOOST: {instruction_matches} terms")
                            
                            detail_terms = ['gentle', 'protect', 'temperature', 'detergent', 'fabric', 'care', 'approved', 'woolmark', 'neutral', 'horizontal', 'cradling', 'soaking']
                            detail_matches = sum(1 for term in detail_terms if term in content_lower)
                            if detail_matches >= 2:
                                score = score * 0.9
                                print(f"      🎯 DETAILED EXPLANATION BOOST: {detail_matches} terms")
                        
                        print(f"      ✅ Final score: {score:.4f}")
                        docs_with_scores.append((doc, score))
        
        else:
            # No brand/model filter - search all documents (original behavior)
            print("🌐 Searching across ALL documents (no brand/model filter)")
            
            query_embedding = self.embeddings.embed_query(query)
            search_k = min(k * 50, len(self.documents), 200)
            D, I = self.index.search(
                np.array([query_embedding], dtype=np.float32), 
                k=search_k
            )
        
            print(f"🔎 Global search returned {len(I[0])} results")
            
            docs_with_scores = []
            for i, doc_idx in enumerate(I[0]):
                if doc_idx < len(self.documents):
                    doc = self.documents[doc_idx]
                    score = D[0][i]
                    
                    # Skip deleted documents
                    file_id = doc.metadata.get('file_id')
                    if not include_deleted and file_id and self.metadata.get(file_id, {}).get('is_deleted', False):
                        continue
                    
                    # Apply same scoring improvements as above
                    query_lower = query.lower()
                    content_lower = doc.page_content.lower()
                    
                    if query_lower in content_lower:
                        score = score * 0.7
                    
                    query_words = query_lower.split()
                    word_matches = sum(1 for word in query_words if word in content_lower)
                    if word_matches > 1:
                        score = score * (1.0 - (word_matches * 0.05))
                    
                    docs_with_scores.append((doc, score))
        
        print(f"📊 Total candidates after filtering: {len(docs_with_scores)}")
        
        # Sort by similarity score (lower is better for L2 distance)
        docs_with_scores.sort(key=lambda x: x[1])
        
        # Take the best results, avoiding duplicates
        result_docs = []
        seen_content = set()
        
        for doc, score in docs_with_scores[:k*3]:
            # Avoid near-duplicate content
            content_hash = hash(doc.page_content[:200])
            if content_hash in seen_content:
                continue
            seen_content.add(content_hash)
            
            # Add context from surrounding chunks if available
            if doc.metadata.get('prev_chunk_preview'):
                doc.metadata['context_before'] = doc.metadata['prev_chunk_preview']
            if doc.metadata.get('next_chunk_preview'):
                doc.metadata['context_after'] = doc.metadata['next_chunk_preview']
            
            result_docs.append(doc)
            
            if len(result_docs) >= k:
                break
        
        print(f"🎯 Final results: {len(result_docs)} documents")
        for i, doc in enumerate(result_docs):
            print(f"  {i+1}. {doc.metadata.get('brand')} {doc.metadata.get('model')} - Page {doc.metadata.get('page')}")
            print(f"      Content: {doc.page_content[:150]}...")
        
        return result_docs
    
    def _generate_file_id(self, file_path: str) -> str:
        """Generate a unique ID for a file based on content and timestamp."""
        # Read the first 8KB of the file for the hash
        with open(file_path, 'rb') as f:
            content = f.read(8 * 1024)
        
        # Create a hash based on content and current time
        time_component = str(datetime.now().timestamp()).encode()
        return hashlib.md5(content + time_component).hexdigest()
    
    def is_db_empty(self) -> bool:
        """Check if the vector database is completely empty."""
        return (
            len(self.documents) == 0 and
            len(self.metadata) == 0 and
            self.index.ntotal == 0
        )
    
    def clear_database(self) -> bool:
        """
        Clear all data from the vector database and associated storage.
        
        Returns:
            success: Whether the clearing operation was successful
        """
        try:
            print("Clearing vector database...")
            
            # Clear in-memory data
            self.documents = []
            self.metadata = {}
            
            # Reset index
            self.index = faiss.IndexFlatL2(self.embedding_dimensions)
            
            # Clear files from disk
            vector_db_files = [
                "documents.json",
                "metadata.json",
                "manual_index.faiss"
            ]
            
            for filename in vector_db_files:
                file_path = os.path.join(self.vector_db_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted {filename}")
            
            # Save empty state
            self._save_state()
            
            print("Database cleared successfully")
            return True
            
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict:
        """
        Get current statistics about the database.
        
        Returns:
            Dict containing database statistics
        """
        # Count documents by language
        language_counts = {}
        for doc in self.documents:
            lang = doc.metadata.get('language', 'en')
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            'total_documents': len(self.documents),
            'total_manuals': len(self.metadata),
            'index_size': self.index.ntotal,
            'documents_by_language': language_counts,
            'embedding_model': OPENAI_EMBEDDING_MODEL,
            'embedding_dimensions': self.embedding_dimensions,
            'manuals': [{
                'file_id': file_id,
                'filename': data['filename'],
                'brand': data.get('brand', 'Unknown'),
                'model': data.get('model', 'Unknown'),
                'language': data.get('language', 'en'),
                'num_chunks': data['num_chunks'],
                'num_pages': data['num_pages']
            } for file_id, data in self.metadata.items()]
        }
    
    def debug_database_contents(self, query: str = None) -> Dict:
        """
        Debug method to inspect database contents and search behavior.
        
        Args:
            query: Optional query to test search with
            
        Returns:
            Dict with debug information
        """
        debug_info = {
            'total_documents': len(self.documents),
            'total_manuals': len(self.metadata),
            'index_size': self.index.ntotal,
            'manuals': [],
            'sample_documents': []
        }
        
        # Get manual information
        for file_id, meta in self.metadata.items():
            debug_info['manuals'].append({
                'file_id': file_id,
                'filename': meta.get('filename'),
                'brand': meta.get('brand'),
                'model': meta.get('model'),
                'num_chunks': meta.get('num_chunks'),
                'language': meta.get('language')
            })
        
        # Get sample documents
        for i, doc in enumerate(self.documents[:5]):  # First 5 documents
            debug_info['sample_documents'].append({
                'index': i,
                'brand': doc.metadata.get('brand'),
                'model': doc.metadata.get('model'),
                'page': doc.metadata.get('page'),
                'content_preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        # If query provided, test search
        if query:
            print(f"\n🔍 Testing search for: '{query}'")
            results = self.similarity_search(query, k=3)
            debug_info['search_test'] = {
                'query': query,
                'results_count': len(results),
                'results': [
                    {
                        'brand': doc.metadata.get('brand'),
                        'model': doc.metadata.get('model'),
                        'page': doc.metadata.get('page'),
                        'content_preview': doc.page_content[:150] + "..."
                    }
                    for doc in results
                ]
            }
        
        return debug_info 