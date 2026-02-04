"""
Lumina RAG Backend
Production-ready RAG backend with Llama 3.2 3B model, ChromaDB vector database,
and comprehensive document processing
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
import traceback
import threading
import queue
import time
import uuid

from config import Config
from utils import ModelManager, DocumentProcessor, RAGEngine, PromptBuilder
from chat_storage import ChatStorage
from web_search import WebSearch, synthesize_web_results

# Initialize Flask app with frontend folder
app = Flask(__name__, 
            static_folder='frontend',
            static_url_path='')
CORS(app)

# Create necessary directories
Config.create_directories()

# Global instances
model_manager = None
rag_engine = None
model_loaded = False
chat_storage = None
web_search = None

# Processing queue and status tracking
processing_queue = queue.Queue()
processing_status = {}  # {file_id: {status, message, progress, etc.}}
processing_lock = threading.Lock()

def initialize_backend():
    """Initialize model and RAG engine in background thread"""
    global model_manager, rag_engine, model_loaded
    
    print("\n" + "="*70)
    print(" LUMINA RAG BACKEND - INITIALIZATION")
    print("="*70 + "\n")
    
    try:
        # Initialize RAG Engine first (lighter weight)
        print("📚 Initializing RAG Engine...")
        rag_engine = RAGEngine()
        print("✓ RAG Engine ready\n")
        
        # Initialize Model Manager
        print("🤖 Initializing Model Manager...")
        model_manager = ModelManager()
        
        # Load model
        print("⏳ Loading Llama model (this may take a few minutes)...")
        print("📡 Server will start immediately and model will load in background...\n")
        model_manager.load_model()
        model_loaded = True
        
        print("\n" + "="*70)
        print(" ✓ MODEL LOADED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        print("\nIf model not found, run: python download_model.py")
        print("="*70 + "\n")
        traceback.print_exc()
        model_loaded = False


def process_documents_worker():
    """Background worker to process documents from the queue"""
    print("📋 Document processing worker started")
    
    while True:
        try:
            # Get next document from queue (blocking)
            task = processing_queue.get()
            
            if task is None:  # Poison pill to stop worker
                break
            
            file_id = task['file_id']
            filepath = task['filepath']
            filename = task['filename']
            
            print(f"\n📄 Processing queued file: {filename} (ID: {file_id})")
            
            # Update status: processing
            with processing_lock:
                processing_status[file_id] = {
                    'status': 'processing',
                    'message': 'Extracting text from document...',
                    'progress': 30,
                    'filename': filename,
                    'updated_at': datetime.now().isoformat()
                }
            
            try:
                # Process document
                processed = DocumentProcessor.process_document(filepath)
                
                if not processed['success']:
                    raise Exception('Failed to extract text from document')
                
                # Update status: indexing
                with processing_lock:
                    processing_status[file_id]['status'] = 'indexing'
                    processing_status[file_id]['message'] = 'Adding to knowledge base...'
                    processing_status[file_id]['progress'] = 70
                    processing_status[file_id]['updated_at'] = datetime.now().isoformat()
                
                # Add to RAG engine
                chunks_added = rag_engine.add_document(
                    filename=filename,
                    text=processed['text'],
                    metadata={
                        'file_type': processed['file_type'],
                        'extension': processed['extension'],
                        'word_count': processed['word_count'],
                        'file_id': file_id
                    }
                )
                
                # Update status: completed
                with processing_lock:
                    processing_status[file_id] = {
                        'status': 'completed',
                        'message': 'Document indexed successfully',
                        'progress': 100,
                        'filename': filename,
                        'chunks_added': chunks_added,
                        'word_count': processed['word_count'],
                        'file_type': processed['file_type'],
                        'completed_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                
                print(f"✓ Completed processing: {filename} ({chunks_added} chunks added)")
                
            except Exception as e:
                # Update status: failed
                error_msg = str(e)
                print(f"❌ Error processing {filename}: {error_msg}")
                traceback.print_exc()
                
                with processing_lock:
                    processing_status[file_id] = {
                        'status': 'failed',
                        'message': f'Processing failed: {error_msg}',
                        'progress': 0,
                        'filename': filename,
                        'error': error_msg,
                        'updated_at': datetime.now().isoformat()
                    }
            
            finally:
                processing_queue.task_done()
                
        except Exception as e:
            print(f"❌ Worker error: {str(e)}")
            traceback.print_exc()
            time.sleep(1)  # Prevent tight loop on errors



# ============================================================================
# FRONTEND ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory('frontend', 'index.html')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    gpu_info = model_manager.get_status()['gpu_info'] if model_manager else {}
    
    return jsonify({
        'status': 'ok',
        'model_loaded': model_loaded,
        'gpu_available': gpu_info.get('available', False),
        'gpu_name': gpu_info.get('name', 'N/A'),
        'rag_documents': rag_engine.collection.count() if rag_engine else 0,
        'rag_unique_docs': len(rag_engine.get_all_documents()) if rag_engine else 0,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint with RAG support
    
    Request JSON:
        {
            "message": "user message",
            "mode": "chat|summarize|deep-research|coding",
            "use_rag": true|false (optional),
            "conversation_history": [] (optional)
        }
    """
    try:
        if not model_loaded:
            return jsonify({
                'error': 'Model not loaded. Please wait for initialization or check server logs.'
            }), 503
        
        data = request.get_json()
        message = data.get('message', '')
        mode = data.get('mode', 'chat')
        use_rag = data.get('use_rag', True)
        conversation_history = data.get('conversation_history', [])
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get mode settings
        mode_settings = Config.MODES.get(mode, Config.MODES['chat'])
        
        # Retrieve relevant context if RAG is enabled
        context_docs = []
        if use_rag and mode_settings.get('use_rag', False):
            top_k = mode_settings.get('top_k', 3)
            if top_k > 0:
                context_docs = rag_engine.semantic_search(message, top_k=top_k)
                print(f"📚 Retrieved {len(context_docs)} relevant documents")
        
        # Build prompt
        prompt = PromptBuilder.build_prompt(
            mode=mode,
            user_message=message,
            context_docs=context_docs,
            conversation_history=conversation_history
        )
        
        # Generate response
        print(f"💭 Generating response in '{mode}' mode...")
        response_text = model_manager.generate(
            prompt,
            max_new_tokens=mode_settings.get('max_tokens', 1024),
            temperature=mode_settings.get('temperature', 0.7)
        )
        
        # Format response
        formatted_response = PromptBuilder.format_response(mode, response_text)
        
        return jsonify({
            'response': formatted_response,
            'mode': mode,
            'used_rag': use_rag and len(context_docs) > 0,
            'context_sources': [
                {
                    'filename': doc['metadata'].get('filename'),
                    'similarity': doc.get('similarity')
                }
                for doc in context_docs[:3]
            ] if context_docs else [],
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    Summarization endpoint
    
    Request JSON:
        {
            "text": "text to summarize"
        }
    """
    try:
        if not model_loaded:
            return jsonify({'error': 'Model not loaded'}), 503
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        prompt = PromptBuilder.build_summarize_prompt(text)
        
        response_text = model_manager.generate(
            prompt,
            max_new_tokens=512,
            temperature=0.3
        )
        
        return jsonify({
            'summary': response_text,
            'original_length': len(text),
            'summary_length': len(response_text),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in summarize endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/deep-research', methods=['POST'])
def deep_research():
    """
    Deep research endpoint with web search + RAG retrieval
    
    Request JSON:
        {
            "query": "research query"
        }
    """
    try:
        if not model_loaded:
            return jsonify({'error': 'Model not loaded'}), 503
        
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Phase 1: Web Search (if available)
        web_results = []
        if web_search and web_search.is_available():
            print(f"🌐 Performing web search for: {query}")
            web_results = web_search.search_web(query, max_results=5)
        else:
            print("⚠️ Web search not available (API key not configured)")
        
        # Phase 2: RAG Retrieval
        rag_docs = []
        if rag_engine.collection.count() > 0:
            rag_docs = rag_engine.semantic_search(query, top_k=10)
            print(f"📚 Retrieved {len(rag_docs)} documents from knowledge base")
        
        # Phase 3: Synthesize answer
        if web_results or rag_docs:
            print("🧠 Synthesizing comprehensive research answer...")
            response_text = synthesize_web_results(query, web_results, rag_docs, model_manager)
        else:
            # Fallback: just use model without context
            print("⚠️ No web or RAG results, using model alone")
            prompt = f"Provide a comprehensive answer to this research query:\n\n{query}"
            response_text = model_manager.generate(
                prompt,
                max_new_tokens=2048,
                temperature=0.6
            )
        
        # Prepare sources
        web_sources = [
            {
                'type': 'web',
                'title': r.get('title'),
                'url': r.get('url'),
                'is_summary': r.get('is_summary', False)
            }
            for r in web_results
            if not r.get('is_summary')  # Exclude AI summary from sources list
        ]
        
        rag_sources = [
            {
                'type': 'document',
                'filename': doc['metadata'].get('filename'),
                'similarity': doc.get('similarity'),
                'chunk_index': doc['metadata'].get('chunk_index')
            }
            for doc in rag_docs[:5]  # Top 5 document sources
        ]
        
        return jsonify({
            'research': response_text,
            'web_sources': web_sources,
            'document_sources': rag_sources,
            'web_search_used': len(web_results) > 0,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in deep-research endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/code-assist', methods=['POST'])
def code_assist():
    """
    Coding assistance endpoint
    
    Request JSON:
        {
            "message": "coding question or request",
            "context": "optional code context"
        }
    """
    try:
        if not model_loaded:
            return jsonify({'error': 'Model not loaded'}), 503
        
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Search for relevant code context
        context_docs = rag_engine.semantic_search(message, top_k=3)
        
        prompt = PromptBuilder.build_coding_prompt(message, context_docs)
        
        response_text = model_manager.generate(
            prompt,
            max_new_tokens=1536,
            temperature=0.2
        )
        
        return jsonify({
            'response': response_text,
            'mode': 'coding',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in code-assist endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    File upload endpoint for RAG indexing
    Files are saved immediately and processed asynchronously
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({
                'error': f'File type not supported. Allowed: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file immediately
        filename = file.filename
        # Add timestamp to filename to avoid collisions
        base_name, ext = os.path.splitext(filename)
        safe_filename = f"{base_name}_{int(time.time())}{ext}"
        filepath = os.path.join(Config.UPLOAD_DIR, safe_filename)
        
        file.save(filepath)
        print(f"✓ File saved: {safe_filename}")
        
        # Set initial status
        with processing_lock:
            processing_status[file_id] = {
                'status': 'queued',
                'message': 'File uploaded, waiting to be processed...',
                'progress': 10,
                'filename': filename,
                'safe_filename': safe_filename,
                'uploaded_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        # Queue for processing
        processing_queue.put({
            'file_id': file_id,
            'filepath': filepath,
            'filename': filename
        })
        
        print(f"📋 File queued for processing: {filename} (ID: {file_id})")
        
        # Return immediately with file ID
        return jsonify({
            'message': 'File uploaded successfully and queued for processing',
            'file_id': file_id,
            'filename': filename,
            'status': 'queued',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in upload endpoint: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/status/<file_id>', methods=['GET'])
def get_upload_status(file_id):
    """
    Get processing status for an uploaded file
    """
    try:
        with processing_lock:
            status = processing_status.get(file_id)
        
        if not status:
            return jsonify({'error': 'File ID not found'}), 404
        
        return jsonify(status), 200
        
    except Exception as e:
        print(f"❌ Error getting upload status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/status', methods=['GET'])
def get_all_upload_status():
    """
    Get processing status for all uploads
    """
    try:
        with processing_lock:
            all_status = dict(processing_status)
        
        return jsonify({
            'uploads': all_status,
            'count': len(all_status),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting upload statuses: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get all indexed documents"""
    try:
        documents = rag_engine.get_all_documents()
        stats = rag_engine.get_stats()
        
        return jsonify({
            'documents': documents,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting documents: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document by ID"""
    try:
        deleted_count = rag_engine.delete_document(doc_id=doc_id)
        
        if deleted_count > 0:
            return jsonify({
                'message': f'Document deleted ({deleted_count} chunks removed)',
                'deleted_chunks': deleted_count
            }), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
            
    except Exception as e:
        print(f"❌ Error deleting document: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search_documents():
    """Search documents"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        results = rag_engine.semantic_search(query, top_k=top_k)
        
        return jsonify({
            'query': query,
            'results': [
                {
                    'text': r['document'],
                    'filename': r['metadata'].get('filename'),
                    'similarity': r.get('similarity'),
                    'chunk_index': r['metadata'].get('chunk_index')
                }
                for r in results
            ],
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in search: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# CHAT HISTORY ENDPOINTS
# ============================================================================

@app.route('/api/chats', methods=['GET'])
def get_chats():
    """Get list of all chats"""
    try:
        chats = chat_storage.get_chat_list()
        return jsonify({
            'chats': chats,
            'count': len(chats),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        print(f"❌ Error getting chats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chats/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Get specific chat by ID"""
    try:
        chat = chat_storage.load_chat(chat_id)
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        return jsonify(chat), 200
    except Exception as e:
        print(f"❌ Error getting chat: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chats/save', methods=['POST'])
def save_chat():
    """Save or update a chat"""
    try:
        data = request.get_json()
        chat_id = data.get('id')
        
        if not chat_id:
            return jsonify({'error': 'Chat ID is required'}), 400
        
        # Save chat
        success = chat_storage.save_chat(str(chat_id), data)
        
        if success:
            return jsonify({
                'message': 'Chat saved successfully',
                'chat_id': chat_id,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({'error': 'Failed to save chat'}), 500
            
    except Exception as e:
        print(f"❌ Error saving chat: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/chats/<chat_id>', methods=['DELETE'])
def delete_chat_endpoint(chat_id):
    """Delete a chat by ID"""
    try:
        success = chat_storage.delete_chat(chat_id)
        
        if success:
            return jsonify({
                'message': 'Chat deleted successfully',
                'chat_id': chat_id
            }), 200
        else:
            return jsonify({'error': 'Chat not found'}), 404
            
    except Exception as e:
        print(f"❌ Error deleting chat: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize Chat Storage
    print("💾 Initializing Chat Storage...")
    chat_storage = ChatStorage(Config.CHAT_HISTORY_DIR)
    print("✓ Chat Storage ready\n")
    
    # Initialize Web Search
    print("🔍 Initializing Web Search...")
    web_search = WebSearch()
    if web_search.is_available():
        print("✓ Web Search ready (API key configured)\n")
    else:
        print("⚠️  Web Search API key not configured (deep research will use RAG only)\n")
    
    # Initialize RAG Engine first (lightweight, can be done synchronously)
    print("📚 Initializing RAG Engine...")
    rag_engine = RAGEngine()
    print("✓ RAG Engine ready\n")
    
    # Start document processing worker in background thread
    print("📋 Starting document processing worker...")
    worker_thread = threading.Thread(target=process_documents_worker, daemon=True)
    worker_thread.start()
    print("✓ Document processing worker ready\n")
    
    # Start model loading in background thread
    print("🚀 Starting model loading in background thread...")
    init_thread = threading.Thread(target=initialize_backend, daemon=True)
    init_thread.start()
    
    # Start Flask server immediately
    print(f"\n🚀 Starting Flask server on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"📚 Knowledge base: {rag_engine.collection.count() if rag_engine else 0} chunks indexed")
    print(f"🤖 Model: {Config.MODEL_NAME} (loading in background...)")
    print("\n" + "="*70)
    print(" Server ready! Access at http://localhost:5000")
    print(" ⏳ Model is loading in background - check frontend for status")
    print(" 📋 File uploads will be processed asynchronously")
    print("="*70 + "\n")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
