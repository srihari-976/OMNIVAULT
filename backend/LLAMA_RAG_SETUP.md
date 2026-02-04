# LLaMA and RAG Integration Setup

## Overview

Lumina backend is designed to work as an offline chatbot that connects to LLaMA models with RAG (Retrieval Augmented Generation) capabilities. All processing happens locally on your device.

## Current Implementation

The backend currently includes:
- Structure for LLaMA model integration
- RAG document storage and retrieval system
- File upload endpoints for RAG indexing
- Multiple chat modes (chat, deep-research, summarize, rag-enhanced)

## Setting Up LLaMA Models

### Option 1: Using llama-cpp-python

1. Install llama-cpp-python:
```bash
pip install llama-cpp-python
```

2. Download a LLaMA model (e.g., from Hugging Face):
   - Recommended: Llama-2-7b-chat or Llama-3-8b-instruct
   - Save the model file locally

3. Update `backend/app.py`:
```python
from llama_cpp import Llama

# Initialize model
llm = Llama(
    model_path="./models/llama-2-7b-chat.gguf",
    n_ctx=2048,
    n_threads=4
)

def process_with_llama(message, mode='chat', context=None):
    # Use the model
    response = llm(
        message,
        max_tokens=512,
        temperature=0.7,
        top_p=0.9,
        repeat_penalty=1.1
    )
    return response['choices'][0]['text']
```

### Option 2: Using Ollama (Recommended for Easy Setup)

1. Install Ollama: https://ollama.ai

2. Pull a model:
```bash
ollama pull llama2
# or
ollama pull llama3
```

3. Update backend to use Ollama API:
```python
import requests

def process_with_llama(message, mode='chat', context=None):
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'llama2',
        'prompt': message,
        'stream': False
    })
    return response.json()['response']
```

## Setting Up RAG with Vector Database

### Option 1: Using ChromaDB

1. Install ChromaDB:
```bash
pip install chromadb sentence-transformers
```

2. Update RAG functions in `backend/app.py`:
```python
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("lumina_documents")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def index_document(filename, content):
    # Chunk the content
    chunks = chunk_text(content)
    embeddings = embedder.encode(chunks)
    
    # Store in ChromaDB
    collection.add(
        embeddings=embeddings.tolist(),
        documents=chunks,
        ids=[f"{filename}_{i}" for i in range(len(chunks))]
    )

def retrieve_relevant_documents(query, n=5):
    query_embedding = embedder.encode([query])
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=n
    )
    return results['documents'][0]
```

### Option 2: Using FAISS

1. Install FAISS:
```bash
pip install faiss-cpu sentence-transformers
```

2. Similar implementation using FAISS for vector storage

## File Processing

The backend currently accepts file uploads and stores them. To enable full RAG:

1. Extract text from files (PDF, DOCX, images with OCR)
2. Chunk the text into smaller pieces
3. Generate embeddings
4. Store in vector database

Example libraries:
- `PyPDF2` or `pdfplumber` for PDFs
- `python-docx` for Word documents
- `pytesseract` for OCR from images
- `Pillow` for image processing

## API Endpoints

- `POST /api/chat` - Send chat message with optional mode
- `POST /api/upload` - Upload files for RAG indexing
- `GET /api/rag/documents` - List indexed documents
- `DELETE /api/rag/documents/<id>` - Delete a document
- `POST /api/rag/search` - Search RAG documents

## Modes

- `chat` - Standard chat mode
- `deep-research` - Enhanced research with RAG context
- `summarize` - Summarization mode
- `rag-enhanced` - Uses RAG to find relevant context

## Next Steps

1. Choose your LLaMA setup method (Ollama recommended for beginners)
2. Set up vector database (ChromaDB recommended)
3. Install required dependencies
4. Update the `process_with_llama` function with actual model calls
5. Update file processing to extract and index text
6. Test with sample documents

## Notes

- All processing is offline - no data leaves your device
- Models can be large (several GB) - ensure sufficient storage
- GPU acceleration recommended for faster inference
- RAG improves response quality by using your uploaded documents as context

