import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Model Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct")
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "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")
    
    # Model Loading Settings
    USE_4BIT_QUANTIZATION = True
    MAX_NEW_TOKENS = 5000        # Model stops early when done — this is the ceiling, not the default
    TEMPERATURE = 0.7
    TOP_P = 0.9
    TOP_K = 50
    REPETITION_PENALTY = 1.1
    
    # GPU Configuration
    DEVICE = "cuda"  # Will auto-fallback to CPU if CUDA not available
    CUDA_VISIBLE_DEVICES = os.getenv("CUDA_VISIBLE_DEVICES", "0")
    
    # Vector Database Settings
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    COLLECTION_NAME = "lumina_documents"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE = "cuda"   # Use GPU for sentence-transformer; falls back to cpu if unavailable
    
    # RAG Settings
    CHUNK_SIZE = 6000         # Doubled → half the chunks → 2x faster embedding
    CHUNK_OVERLAP = 200
    TOP_K_RETRIEVAL = 5
    SIMILARITY_THRESHOLD = 0.5
    MAX_CHUNKS_PER_DOC = 500  # Raised cap to handle 50 MB documents
    
    # Document Processing
    UPLOAD_DIR = os.path.abspath(os.getenv("UPLOAD_DIR", "./uploads"))
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB (hard HTTP limit)
    MAX_UPLOAD_SIZE_MB = 50           # Raised: allow full 50 MB uploads
    ALLOWED_EXTENSIONS = {
        'pdf', 'docx', 'doc', 'txt', 'md', 'markdown',
        'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp',
        'py', 'js', 'java', 'cpp', 'c', 'html', 'css', 'json', 'xml'
    }
    
    # Storage Directories
    RAG_STORAGE_DIR = "./rag_storage"
    KNOWLEDGE_DATA_DIR = "./knowledge_data"
    MODEL_CACHE_DIR = "./model_cache"
    CHAT_HISTORY_DIR = "./chat_history"
    
    # Web Search Settings (for Deep Research)
    WEB_SEARCH_API_KEY = os.getenv("WEB_SEARCH_API_KEY", "")
    WEB_SEARCH_PROVIDER = os.getenv("WEB_SEARCH_PROVIDER", "tavily")
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    
    # API Settings
    FLASK_HOST = "127.0.0.1"
    FLASK_PORT = 5000
    FLASK_DEBUG = False
    
    # Mode-specific settings
    MODES = {
        'chat': {
            'max_tokens': 2048,   # Stops early when answer is complete
            'temperature': 0.7,
            'use_rag': True,
            'top_k': 3
        },
        'summarize': {
            'max_tokens': 2048,
            'temperature': 0.3,
            'use_rag': False,
            'top_k': 0
        },
        'deep-research': {
            'max_tokens': 5000,
            'temperature': 0.5,
            'use_rag': True,
            'top_k': 10
        },
        'coding': {
            'max_tokens': 4096,
            'temperature': 0.2,
            'use_rag': True,
            'top_k': 5
        }
    }
    
    @staticmethod
    def create_directories():
        """Create necessary directories if they don't exist"""
        dirs = [
            Config.UPLOAD_DIR,
            Config.RAG_STORAGE_DIR,
            Config.KNOWLEDGE_DATA_DIR,
            Config.MODEL_CACHE_DIR,
            Config.VECTOR_DB_PATH,
            Config.CHAT_HISTORY_DIR,
            os.path.join(Config.KNOWLEDGE_DATA_DIR, "examples"),
            os.path.join(Config.KNOWLEDGE_DATA_DIR, "prompts")
        ]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
