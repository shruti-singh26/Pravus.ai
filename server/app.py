import os
import time
import tempfile
import traceback
from typing import Dict, Any
from datetime import datetime

from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
from googletrans import Translator

from document_processor import DocumentProcessor
from llm_service import LLMService
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH, MANUAL_FIELDS, DEFAULT_LLM_MODEL, VECTOR_DB_PATH, LLM_PROVIDER

from tools import retrieve_tool, summarize_tool, translate_tool,greet_tool, help_tool, no_manuals_tool, no_matching_manuals_tool, no_context_tool, generate_tool,clarify_tool

from PravusAgent import PravusAgent

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Configure server timeouts for file upload processing
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)



# Initialize services
doc_processor = DocumentProcessor()
llm_service = LLMService()

# Initialize translator
translator = Translator()
retriever = doc_processor.get_retriever()

# Initialize the PravusAgent with the necessary components
tools = {
    'greet': greet_tool,
    'help': help_tool,
    'retrieve': retrieve_tool,
    'no_manuals': no_manuals_tool,
    'no_matching_manuals': no_matching_manuals_tool,
    'no_context': no_context_tool,
    'generate': generate_tool,
    'translate': translate_tool,
    'summarize': summarize_tool,
    'clarify': clarify_tool
}                            # Replace with actual tools if needed

pravus_agent  = PravusAgent(retriever, llm_service, tools)

# Log at startup if no documents are available
if not doc_processor.documents:
    print("No documents found in the database. The chatbot will operate in general knowledge mode until manuals are uploaded.")

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the server is running
    and the model is loaded correctly
    """
    return jsonify({
        'status': 'ok',
        'model': DEFAULT_LLM_MODEL,
        'timestamp': time.time(),
        'has_documents': len(doc_processor.documents) > 0
    })

@app.route('/manuals/<path:filename>')
def serve_manual(filename):
    """
    Serve PDF files from the uploads directory.
    This handles requests like /manuals/washing-machines/Samsung%20Washer%20DC68-02657F%20User%20Guide.pdf
    Supports both viewing in browser and downloading
    """
    try:
        # Decode URL-encoded filename
        import urllib.parse
        decoded_filename = urllib.parse.unquote(filename)
        
        # Extract just the filename from the path (remove category subdirectories)
        actual_filename = os.path.basename(decoded_filename)
        
        print(f"Looking for PDF file: {actual_filename}")
        
        # Check if it's a download request
        download = request.args.get('download', 'false').lower() == 'true'
        
        # Look for the file in the uploads directory
        file_path = os.path.join(UPLOAD_FOLDER, actual_filename)
        
        if os.path.exists(file_path):
            print(f"Found and serving PDF file: {file_path}")
            if download:
                return send_file(file_path, as_attachment=True, download_name=actual_filename, mimetype='application/pdf')
            else:
                return send_file(file_path, as_attachment=False, mimetype='application/pdf')
        
        # If not found, try to find it by searching through metadata
        print(f"File not found at {file_path}, searching through metadata...")
        for file_id, metadata in doc_processor.metadata.items():
            if metadata.get('filename') == actual_filename:
                print(f"Found file in metadata: {metadata}")
                # Try different possible paths
                possible_paths = [
                    os.path.join(UPLOAD_FOLDER, actual_filename),
                    os.path.join(UPLOAD_FOLDER, metadata.get('filename', '')),
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        print(f"Found PDF at: {path}")
                        if download:
                            return send_file(path, as_attachment=True, download_name=actual_filename, mimetype='application/pdf')
                        else:
                            return send_file(path, as_attachment=False, mimetype='application/pdf')
        
        # If still not found, return 404 with helpful message
        print(f"PDF file not found: {actual_filename}")
        print(f"Available files in uploads: {os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else 'No uploads directory'}")
        
        return jsonify({
            'error': 'File not found',
            'message': f'The requested file "{actual_filename}" could not be found.',
            'available_files': os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
        }), 404
        
    except Exception as e:
        print(f"Error serving PDF file: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Server error',
            'message': f'An error occurred while serving the file: {str(e)}'
        }), 500

@app.route('/api/download/<path:filename>')
def download_manual(filename):
    """
    Force download PDF files from the uploads directory.
    This endpoint always returns files as attachments for download.
    """
    try:
        # Decode URL-encoded filename
        import urllib.parse
        decoded_filename = urllib.parse.unquote(filename)
        
        # Extract just the filename from the path (remove category subdirectories)
        actual_filename = os.path.basename(decoded_filename)
        
        print(f"Download request for PDF file: {actual_filename}")
        
        # Look for the file in the uploads directory
        file_path = os.path.join(UPLOAD_FOLDER, actual_filename)
        
        if os.path.exists(file_path):
            print(f"Found and downloading PDF file: {file_path}")
            # Force download with proper filename
            return send_file(
                file_path, 
                as_attachment=True, 
                download_name=actual_filename, 
                mimetype='application/pdf'
            )
        
        # If not found, try to find it by searching through metadata
        print(f"File not found at {file_path}, searching through metadata...")
        for file_id, metadata in doc_processor.metadata.items():
            if metadata.get('filename') == actual_filename:
                print(f"Found file in metadata: {metadata}")
                # Try different possible paths
                possible_paths = [
                    os.path.join(UPLOAD_FOLDER, actual_filename),
                    os.path.join(UPLOAD_FOLDER, metadata.get('filename', '')),
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        print(f"Found and downloading PDF at: {path}")
                        return send_file(
                            path, 
                            as_attachment=True, 
                            download_name=actual_filename, 
                            mimetype='application/pdf'
                        )
        
        # If still not found, return 404 with helpful message
        print(f"PDF file not found for download: {actual_filename}")
        print(f"Available files in uploads: {os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else 'No uploads directory'}")
        
        return jsonify({
            'error': 'File not found',
            'message': f'The requested file "{actual_filename}" could not be found for download.',
            'available_files': os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
        }), 404
        
    except Exception as e:
        print(f"Error downloading PDF file: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Download error',
            'message': f'An error occurred while downloading the file: {str(e)}'
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['message']
    source_language = data.get('source_language', 'en')
    response_language = data.get('responseLanguage', 'en')
    
    print(f"\n🌐 CHAT: Received message in {source_language}")
    print(f"🌐 CHAT: Original message: '{user_message}'")
    
    # Translate to English if needed
    if source_language != 'en':
        try:
            print(f"🌐 CHAT: Translating to English...")
            translated = translator.translate(user_message, src=source_language, dest='en')
            user_message = translated.text
            print(f"🌐 CHAT: Translated message: '{user_message}'")
        except Exception as e:
            print(f"❌ CHAT: Translation error: {str(e)}")
            print(f"❌ CHAT: Proceeding with original message")
    
    # Get the flag from the frontend, default to False if not present
    awaiting_clarification = data.get('awaiting_clarification', True)
    context = {
        'brand': data.get('brand'),
        'model': data.get('model'),
        'response_language': response_language,
        'source_language': source_language,
        'doc_processor': doc_processor,
        'llm_service': llm_service,
        'awaiting_clarification': awaiting_clarification
    }
    
    response = pravus_agent.act(user_message, context)
    response['awaiting_clarification'] = context.get('awaiting_clarification', True)
    
    # Translate response back if needed
    if response_language != 'en' and response.get('response'):
        try:
            print(f"🌐 CHAT: Translating response to {response_language}...")
            translated = translator.translate(response['response'], src='en', dest=response_language)
            response['response'] = translated.text
            print(f"🌐 CHAT: Translated response: '{response['response']}'")
        except Exception as e:
            print(f"❌ CHAT: Response translation error: {str(e)}")
            print(f"❌ CHAT: Returning English response")
    
    return jsonify(response)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle file uploads with metadata from frontend
    """
    try:
        if 'file' not in request.files:
            print("Error: No file part in request")
            return jsonify({'success': False, 'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            print("Error: No selected file")
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        # Get metadata from form data
        metadata = {
            'brand': request.form.get('brand', 'Unknown'),
            'model': request.form.get('model', 'Unknown'),
            'language': request.form.get('language', 'en'),
            'product_type': request.form.get('product_type', 'Unknown'),
            'year': request.form.get('year', str(datetime.now().year)),
            'source': 'manual_upload',
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Processing file: {file.filename}")
        print(f"Metadata received: {metadata}")
        print(f"File size: {file.content_length if hasattr(file, 'content_length') else 'unknown'} bytes")
        
        # Check if this manual already exists
        existing_manuals = doc_processor.get_all_manuals()
        
        # First check for duplicate filename
        filename = secure_filename(file.filename)
        for existing in existing_manuals:
            if existing.get('filename') == filename:
                print(f"File with same name already exists: {filename}")
                return jsonify({
                    'success': False,
                    'error': f'A file with the name "{filename}" already exists in the system. Please rename your file or delete the existing one first.',
                    'duplicate_info': {
                        'filename': existing.get('filename'),
                        'brand': existing.get('brand', 'Unknown'),
                        'model': existing.get('model', 'Unknown'),
                        'upload_date': existing.get('timestamp'),
                        'file_id': existing.get('file_id')
                    }
                }), 409  # 409 Conflict status code
        
        # Then check for duplicate manual (brand/model/language combination)
        for existing in existing_manuals:
            if (existing.get('brand') == metadata['brand'] and 
                existing.get('model') == metadata['model'] and
                existing.get('language') == metadata['language']):
                
                print(f"Manual already exists: {metadata['brand']} {metadata['model']} ({metadata['language']})")
                
                # Return existing manual info instead of re-processing
                timestamp = int(datetime.fromisoformat(existing['timestamp']).timestamp() * 1000)
                
                return jsonify({
                    'success': True,
                    'file_id': existing['file_id'],
                    'filename': existing['filename'],
                    'timestamp': timestamp,
                    'language': existing.get('language', 'en'),
                    'brand': existing.get('brand', 'Unknown'),
                    'model': existing.get('model', 'Unknown'),
                    'product_type': existing.get('product_type', 'Unknown'),
                    'year': existing.get('year', '2023'),
                    'message': f'Manual already exists in database: {existing["filename"]}',
                    'cached': True
                })
        
        # Save file to uploads directory with secure filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        print(f"File saved at: {file_path}")
        print("Starting PDF processing and embedding generation...")
        
        try:
            # Process the PDF and add to vector store with provided metadata
            print("Calling document processor...")
            file_id = doc_processor.process_pdf(file_path, metadata)
            print(f"PDF processing completed successfully. File ID: {file_id}")
            
            # Get the stored metadata
            file_metadata = doc_processor.metadata[file_id]
            
            # Convert timestamp to milliseconds for JavaScript
            timestamp = int(datetime.fromisoformat(file_metadata['timestamp']).timestamp() * 1000)
            
            # Prepare response with metadata
            response_data = {
                'success': True,
                'file_id': file_id,
                'filename': file_metadata['filename'],
                'timestamp': timestamp,
                'language': metadata['language'],
                'brand': metadata['brand'],
                'model': metadata['model'],
                'product_type': metadata['product_type'],
                'year': metadata['year'],
                'message': f'Successfully uploaded and processed {file_metadata["filename"]}'
            }
            
            return jsonify(response_data)
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Error processing file: {str(e)}'
            }), 500
        finally:
            # Keep the uploaded file for serving via /manuals/ endpoint
            # The original PDF is now available for viewing
            print(f"Original PDF kept at: {file_path}")
            # Note: We no longer delete the file so it can be served later
            pass
    except Exception as e:
        print(f"Unexpected error in upload_file: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/files', methods=['GET'])
def get_files():
    """
    Return list of uploaded files with metadata
    """
    try:
        manuals = doc_processor.get_all_manuals()
        
        # Convert to the format expected by the frontend
        files = []
        for manual in manuals:
            file_data = {
                'name': manual['filename'],
                'timestamp': manual['timestamp'],
                'file_id': manual['file_id']
            }
            
            # Include all metadata fields if they exist
            if 'brand' in manual and manual['brand'] != 'Unknown':
                file_data['brand'] = manual['brand']
            if 'model' in manual and manual['model'] != 'Unknown':
                file_data['model'] = manual['model']
            if 'product_type' in manual and manual['product_type'] != 'Unknown':
                file_data['product_type'] = manual['product_type']
            if 'year' in manual and manual['year'] != 'Unknown':
                file_data['year'] = manual['year']
            if 'language' in manual and manual['language'] != 'Unknown':
                file_data['language'] = manual['language']
            
            files.append(file_data)
        
        return jsonify(files)
    
    except Exception as e:
        print(f"Error in get_files endpoint: {str(e)}")
        print(traceback.format_exc())
        
        # Always return a valid response, even if there's an error
        # This ensures the frontend receives an empty array instead of failing
        return jsonify([])  # Return empty array instead of error

@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """
    Completely delete a file and its associated data from the system
    """
    # Check if the file exists
    if file_id not in doc_processor.metadata:
        return jsonify({'error': 'File not found'}), 404
    
    # Get file info before deletion
    file_info = doc_processor.metadata[file_id]
    filename = file_info['filename']
    
    # Build response message with available metadata
    message_parts = [filename]
    if 'brand' in file_info and file_info['brand'] != 'Unknown':
        message_parts.append(f"brand: {file_info['brand']}")
    if 'model' in file_info and file_info['model'] != 'Unknown':
        message_parts.append(f"model: {file_info['model']}")
    
    # Delete the file and all associated data
    success = doc_processor.delete_document(file_id)
    
    if success:
        # Check if database is now empty
        is_empty = doc_processor.is_db_empty()
        
        # Prepare response with only available metadata
        response_data = {
            'success': True,
            'message': f'Successfully deleted {" (".join(message_parts)})',
            'deleted_info': {
                'file_id': file_id,
                'filename': filename
            },
            'database_empty': is_empty
        }
        
        # Only include brand/model if they exist and are not Unknown
        if 'brand' in file_info and file_info['brand'] != 'Unknown':
            response_data['deleted_info']['brand'] = file_info['brand']
        if 'model' in file_info and file_info['model'] != 'Unknown':
            response_data['deleted_info']['model'] = file_info['model']
        
        return jsonify(response_data)
    else:
        return jsonify({
            'error': f'Failed to delete {filename}. The file may be in use or the system encountered an error.',
            'file_info': {
                'file_id': file_id,
                'filename': filename
            }
        }), 500

@app.route('/api/brands', methods=['GET'])
def get_brands():
    """
    Return a list of all unique brands in the system
    """
    manuals = doc_processor.get_all_manuals()
    brands = sorted(list(set(manual.get('brand', 'Unknown') for manual in manuals)))
    
    return jsonify({
        'brands': brands
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """
    Return a list of all models, optionally filtered by brand
    """
    brand = request.args.get('brand')
    manuals = doc_processor.get_all_manuals()
    
    if brand:
        # Filter by brand
        filtered_manuals = [m for m in manuals if m.get('brand') == brand]
        models = sorted(list(set(manual.get('model', 'Unknown') for manual in filtered_manuals)))
    else:
        models = sorted(list(set(manual.get('model', 'Unknown') for manual in manuals)))
    
    return jsonify({
        'models': models
    })


@app.route('/api/database/clear', methods=['POST'])
def clear_database():
    """
    Clear all data from the vector database
    """
    success = doc_processor.clear_database()
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Successfully cleared all data from the database',
            'database_empty': doc_processor.is_db_empty()
        })
    else:
        return jsonify({
            'error': 'Failed to clear database'
        }), 500

@app.route('/api/database/stats', methods=['GET'])
def get_database_stats():
    """
    Get current statistics about the database
    """
    stats = doc_processor.get_database_stats()
    stats['is_empty'] = doc_processor.is_db_empty()
    
    return jsonify(stats)

@app.route('/api/database/verify', methods=['GET'])
def verify_database():
    """
    Verify the integrity and state of the database
    """
    stats = doc_processor.get_database_stats()
    is_empty = doc_processor.is_db_empty()
    
    # Check for consistency
    consistent = (
        stats['total_documents'] == stats['index_size'] and
        len(stats['manuals']) == stats['total_manuals'] and
        (is_empty == (stats['total_documents'] == 0))
    )
    
    return jsonify({
        'is_empty': is_empty,
        'is_consistent': consistent,
        'stats': stats
    })

@app.route('/api/debug/search', methods=['POST'])
def debug_search():
    """
    Debug endpoint to test search functionality and inspect database contents
    """
    try:
        data = request.json
        query = data.get('query', '')
        brand = data.get('brand')
        model = data.get('model')
        
        print(f"\n🔍 DEBUG SEARCH REQUEST")
        print(f"Query: '{query}'")
        print(f"Brand: {brand}")
        print(f"Model: {model}")
        
        # Get database debug info
        debug_info = doc_processor.debug_database_contents(query)
        
        # Perform search with debug output
        search_results = doc_processor.similarity_search(
            query=query,
            brand=brand,
            model=model,
            k=4
        )
        
        # Format results for response
        formatted_results = []
        for i, doc in enumerate(search_results):
            formatted_results.append({
                'rank': i + 1,
                'brand': doc.metadata.get('brand'),
                'model': doc.metadata.get('model'),
                'page': doc.metadata.get('page'),
                'chunk': doc.metadata.get('chunk'),
                'content_preview': doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                'metadata': {
                    'filename': doc.metadata.get('filename'),
                    'language': doc.metadata.get('language'),
                    'timestamp': doc.metadata.get('timestamp')
                }
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'filters': {'brand': brand, 'model': model},
            'database_info': debug_info,
            'search_results': {
                'count': len(search_results),
                'results': formatted_results
            }
        })
        
    except Exception as e:
        print(f"Error in debug_search: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/debug/database', methods=['GET'])
def debug_database():
    """
    Debug endpoint to inspect database contents and search behavior
    """
    try:
        query = request.args.get('query')
        debug_info = doc_processor.debug_database_contents(query)
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        })
        
    except Exception as e:
        print(f"Error in debug database: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/summarize', methods=['POST'])
def summarize_conversation():
    """
    Summarize a conversation using LLM for support ticket creation
    """
    try:
        data = request.json
        
        if not data or 'messages' not in data:
            return jsonify({'error': 'No messages provided'}), 400
        
        messages = data['messages']
        context = data.get('context', 'general')
        
        if not messages or len(messages) == 0:
            return jsonify({'summary': 'No conversation to summarize.'}), 200
        
        # Format messages for summarization
        conversation_text = ""
        for msg in messages:
            role = "User" if msg.get('sender') == 'user' else "Assistant"
            text = msg.get('text', '').strip()
            if text:
                conversation_text += f"{role}: {text}\n\n"
        
        if not conversation_text.strip():
            return jsonify({'summary': 'No meaningful conversation to summarize.'}), 200
        
        # Create summarization prompt
        if context == 'support_ticket':
            prompt = f"""Please create a professional, well-structured summary of this customer support conversation for a support ticket. Format the response exactly as shown below:

**Support Ticket Summary**

**Customer's Main Issue/Question:**
[Provide a clear, concise statement of the primary issue or question, including any specific product/model mentioned]

**Goal:**
[One-line description of what the customer was trying to accomplish]

**Key Details:**
1. [Important detail with page reference if available]
2. [Important detail with page reference if available]
3. [Important detail with page reference if available]
4. [Important detail with page reference if available]

**Additional Context:**
- [Any relevant background information]
- [Any important clarifications made]
- [Any safety or critical notes]

**Actionable Next Steps:**
[Clear recommendation for what should happen next]

Use the above format strictly, maintaining the bold headers and bullet points. Include page references whenever available from the manual. Be specific about product names and model numbers when mentioned.

Conversation:
{conversation_text}

Summary:"""
        else:
            prompt = f"""Please create a concise, well-structured summary of this conversation:

{conversation_text}

Summary:"""
        
        # Generate summary using LLM
        print(f"🤖 Generating conversation summary using {LLM_PROVIDER.upper()} LLM")
        
        try:
            summary = llm_service.generate_direct_response(
                prompt=prompt,
                max_tokens=500,  # Limit summary length
                temperature=0.3  # Lower temperature for more focused summaries
            )
            
            # Clean up the summary
            summary = summary.strip()
            if summary.startswith("Summary:"):
                summary = summary[8:].strip()
            
            print(f"✅ Summary generated successfully ({len(summary)} characters)")
            
            return jsonify({
                'summary': summary,
                'timestamp': time.time()
            })
            
        except Exception as llm_error:
            print(f"❌ LLM summarization failed: {str(llm_error)}")
            # Fallback to basic formatting
            fallback_summary = f"Conversation Summary:\n\n{conversation_text}"
            return jsonify({
                'summary': fallback_summary,
                'timestamp': time.time(),
                'note': 'Generated using fallback method due to LLM unavailability'
            })
        
    except Exception as e:
        print(f"Error in summarize conversation: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to summarize conversation',
            'details': str(e)
        }), 500

@app.route('/api/clear-memory', methods=['POST'])
def clear_memory():
    """Clear the PravusAgent's conversation memory"""
    try:
        pravus_agent.clear_conversation_memory()
        return jsonify({'success': True, 'message': 'Memory cleared successfully'})
    except Exception as e:
        print(f"❌ Error clearing memory: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000) 