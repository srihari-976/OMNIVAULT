# Lumina RAG Backend 🚀

Production-ready RAG (Retrieval-Augmented Generation) backend powered by **Llama 3.2 3B** with GPU acceleration, **ChromaDB** vector database, and comprehensive multi-format document processing.

## Features ✨

- **🤖 Llama 3.2 3B Model**: State-of-the-art language model with 4-bit quantization for efficiency
- **🎯 GPU Acceleration**: CUDA support for fast inference on NVIDIA GPUs
- **📚 Vector Database**: ChromaDB for semantic search and document retrieval
- **📄 Multi-Format Support**: PDF, DOCX, TXT, Markdown, Images (OCR), and Code files
- **🔍 Multiple Modes**:
  - **Chat**: Conversational AI with RAG context
  - **Summarize**: Intelligent document summarization
  - **Deep Research**: Comprehensive analysis with extensive context
  - **Coding**: Programming assistance with code-aware responses
- **⚡ Efficient**: 4-bit quantization reduces memory usage by ~75%
- **🔒 Offline**: All processing happens locally - no cloud API calls

## Prerequisites 📋

- **OS**: Windows with WSL 2 (Ubuntu recommended)
- **GPU**: NVIDIA GPU with 8GB+ VRAM (recommended)
- **CUDA**: CUDA 11.8 or higher
- **Python**: 3.8 or higher
- **Disk Space**: ~15GB (10GB for model, 5GB for dependencies)
- **HuggingFace Account**: For model download access

## Quick Start 🚀

### 1. Install Dependencies

```bash
# Install PyTorch with CUDA support first
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
pip install -r requirements.txt

# For OCR support (optional)
sudo apt-get install tesseract-ocr
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your HuggingFace token
# HUGGINGFACE_TOKEN=your_token_here
```

Your HuggingFace token is already configured: `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`

### 3. Setup GPU (WSL)

```bash
# Make setup script executable
chmod +x setup_gpu.sh

# Run GPU setup verification
./setup_gpu.sh
```

### 4. Download Model

```bash
# Download Llama 3.2 3B model (~6-7 GB)
python download_model.py
```

This will:
- Authenticate with HuggingFace using your token
- Download the model to `./model_cache`
- Verify the download

### 5. Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints 📡

### Health Check
```http
GET /health
```

Returns server status, GPU info, and document count.

### Chat
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Explain quantum computing",
  "mode": "chat",
  "use_rag": true,
  "conversation_history": []
}
```

**Modes**: `chat`, `summarize`, `deep-research`, `coding`

### Summarize
```http
POST /api/summarize
Content-Type: application/json

{
  "text": "Long text to summarize..."
}
```

### Deep Research
```http
POST /api/deep-research
Content-Type: application/json

{
  "query": "What are the implications of quantum computing?"
}
```

Retrieves top 10 relevant documents for comprehensive analysis.

### Code Assist
```http
POST /api/code-assist
Content-Type: application/json

{
  "message": "Write a Python function to reverse a linked list"
}
```

### Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data

file: <your_file>
```

**Supported formats**: PDF, DOCX, TXT, MD, PNG, JPG, PY, JS, JAVA, CPP, HTML, CSS, JSON, XML

### Get Documents
```http
GET /api/documents
```

Returns all indexed documents with stats.

### Search Documents
```http
POST /api/search
Content-Type: application/json

{
  "query": "machine learning",
  "top_k": 5
}
```

### Delete Document
```http
DELETE /api/documents/<doc_id>
```

## Project Structure 📁

```
backend/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── download_model.py      # Model download script
├── setup_gpu.sh          # GPU setup script
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
│
├── utils/
│   ├── __init__.py
│   ├── model_loader.py    # Llama model management
│   ├── document_processor.py  # Multi-format document processing
│   ├── rag_engine.py      # RAG and vector database
│   └── prompt_builder.py  # Mode-specific prompt templates
│
├── knowledge_data/
│   └── examples/
│       ├── normal_chat_examples.json
│       ├── summarize_examples.json
│       ├── deep_research_examples.json
│       └── coding_examples.json
│
├── uploads/              # Uploaded documents
├── chroma_db/           # Vector database storage
├── model_cache/         # Downloaded model cache
└── rag_storage/         # RAG metadata storage
```

## Configuration ⚙️

Edit `config.py` or `.env` to customize:

### Model Settings
- `MODEL_NAME`: Llama model to use
- `USE_4BIT_QUANTIZATION`: Enable 4-bit quantization (recommended)
- `MAX_NEW_TOKENS`: Maximum response length
- `TEMPERATURE`: Response randomness (0.0 - 1.0)

### RAG Settings
- `CHUNK_SIZE`: Document chunk size (default: 512)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `TOP_K_RETRIEVAL`: Number of results to retrieve (default: 5)
- `SIMILARITY_THRESHOLD`: Minimum similarity score (default: 0.5)

### GPU Settings
- `DEVICE`: "cuda" or "cpu"
- `CUDA_VISIBLE_DEVICES`: GPU device ID (default: "0")

## Performance Optimization 🚀

### Memory Usage
- **4-bit quantization**: Reduces VRAM from ~13GB to ~3.5GB
- **Batch processing**: Process multiple documents efficiently
- **Chunk caching**: Reuse embeddings when possible

### Speed Optimization
- **GPU acceleration**: ~10x faster than CPU
- **Vector search**: Sub-second semantic search
- **Model caching**: Load model once, reuse for all requests

### Recommended Settings
```python
# For 8GB GPU
USE_4BIT_QUANTIZATION = True
MAX_NEW_TOKENS = 1024

# For 16GB+ GPU
USE_4BIT_QUANTIZATION = False  # Full precision
MAX_NEW_TOKENS = 2048
```

## Troubleshooting 🔧

### Model fails to load
```bash
# Verify HuggingFace token
echo $HUGGINGFACE_TOKEN

# Re-download model
python download_model.py
```

### CUDA out of memory
```python
# In config.py, ensure 4-bit quantization is enabled
USE_4BIT_QUANTIZATION = True

# Or reduce max tokens
MAX_NEW_TOKENS = 512
```

### GPU not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Test CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

### Slow inference
- Enable GPU acceleration (check `nvidia-smi`)
- Reduce `MAX_NEW_TOKENS`
- Use 4-bit quantization
- Close other GPU-intensive applications

### Document processing fails
```bash
# For PDF issues
pip install --upgrade PyMuPDF

# For OCR issues
sudo apt-get install tesseract-ocr

# For encoding issues
pip install chardet
```

## Example Usage 💡

### Python Client
```python
import requests

BASE_URL = "http://localhost:5000"

# Upload a document
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/upload",
        files={"file": f}
    )
    print(response.json())

# Chat with RAG context
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "message": "What does the document say about AI?",
        "mode": "chat",
        "use_rag": True
    }
)
print(response.json()["response"])
```

### JavaScript Client
```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:5000/api/upload', {
  method: 'POST',
  body: formData
});

// Chat
const chatResponse = await fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Summarize the key points',
    mode: 'summarize',
    use_rag: true
  })
});

const data = await chatResponse.json();
console.log(data.response);
```

## Knowledge Base 📚

The backend includes example responses for each mode in `knowledge_data/examples/`:
- **normal_chat_examples.json**: Conversational responses
- **summarize_examples.json**: Summarization templates
- **deep_research_examples.json**: Research analysis formats
- **coding_examples.json**: Code assistance patterns

These serve as reference for expected output quality and formatting.

## Development 🛠️

### Adding New Document Types
Edit `utils/document_processor.py`:
```python
@staticmethod
def extract_text_from_new_format(file_path):
    # Your extraction logic
    return extracted_text

# Add to process_document() method
elif file_ext in ['new', 'format']:
    text = DocumentProcessor.extract_text_from_new_format(file_path)
    doc_type = "new_format"
```

### Custom Prompt Templates
Edit `utils/prompt_builder.py`:
```python
SYSTEM_PROMPTS['new_mode'] = """Your custom system prompt"""

@staticmethod
def build_new_mode_prompt(message, context):
    # Build custom prompt
    return prompt
```

### Testing
```bash
# Test model loading
python utils/model_loader.py

# Test document processing
python utils/document_processor.py path/to/document.pdf

# Test RAG engine
python utils/rag_engine.py
```

## License 📄

This project uses:
- **Llama 3.2 3B**: Meta's Llama license
- **ChromaDB**: Apache License 2.0
- **Sentence Transformers**: Apache License 2.0

## Support 💬

For issues or questions:
1. Check this README's troubleshooting section
2. Review server logs for error messages
3. Verify GPU setup with `./setup_gpu.sh`
4. Ensure model is downloaded with `python download_model.py`

## Credits 🙏

- **Meta AI**: Llama 3.2 model
- **HuggingFace**: Model hosting and transformers library
- **Chroma**: Vector database
- **Sentence Transformers**: Embedding models

---

**Built with ❤️ for offline, privacy-focused AI**
