# Lumina RAG Backend - Setup Guide

This guide will walk you through setting up the RAG backend step by step.

## Step 1: Verify WSL and GPU Setup

### Check WSL Version
```bash
wsl --version
# Should show WSL version 2
```

If not on WSL 2:
```bash
wsl --set-version Ubuntu 2
```

### Verify GPU is Available
```bash
nvidia-smi
```

You should see your GPU information. If not, install NVIDIA drivers for WSL:
https://docs.nvidia.com/cuda/wsl-user-guide/index.html

## Step 2: Install System Dependencies

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-dev

# Install Tesseract OCR (for image processing)
sudo apt-get install -y tesseract-ocr libtesseract-dev

# Install other dependencies
sudo apt-get install -y build-essential libssl-dev libffi-dev
```

## Step 3: Install PyTorch with CUDA

**IMPORTANT**: Install PyTorch FIRST before other dependencies!

```bash
cd "d:/Project/New folder (2)/backend"

# Install PyTorch with CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Verify PyTorch CUDA
```bash
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"
```

Should output:
```
CUDA Available: True
CUDA Version: 11.8
```

## Step 4: Install Python Dependencies

```bash
# Install all other dependencies
pip install -r requirements.txt
```

This will install:
- Flask and Flask-CORS
- Transformers, Accelerate, BitsAndBytes
- ChromaDB and Sentence Transformers
- Document processing libraries (PyMuPDF, python-docx, pytesseract, Pillow)
- Utilities

## Step 5: Configure Environment

Your `.env` file is already created with your HuggingFace token:
```bash
cat .env
```

Should show:
```
HUGGINGFACE_TOKEN=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
MODEL_NAME=meta-llama/Llama-3.2-3B-Instruct
...
```

## Step 6: Run GPU Setup Check

```bash
chmod +x setup_gpu.sh
./setup_gpu.sh
```

This will verify:
- ✓ NVIDIA driver detected
- ✓ CUDA toolkit installed
- ✓ PyTorch CUDA availability

## Step 7: Download Llama Model

```bash
python download_model.py
```

This will:
1. Authenticate with HuggingFace using your token
2. Download Llama 3.2 3B (~6-7 GB)
3. Cache the model in `./model_cache`

**Note**: This will take some time depending on your internet speed.

## Step 8: Start the Backend Server

```bash
python app.py
```

You should see:
```
====================================================================
 LUMINA RAG BACKEND - INITIALIZATION
====================================================================

📚 Initializing RAG Engine...
✓ RAG Engine ready

🤖 Initializing Model Manager...
✓ CUDA is available!
  GPU: NVIDIA GeForce RTX 3080
  CUDA Version: 11.8

⏳ Loading Llama model (this may take a few minutes)...
Loading tokenizer...
Configuring 4-bit quantization...
Loading model (this may take a few minutes)...

✓ Model loaded successfully!
  Device: CUDA
  Quantization: 4-bit
  Memory allocated: 3.45 GB

====================================================================
 ✓ BACKEND INITIALIZED SUCCESSFULLY
====================================================================

🚀 Starting Flask server on 0.0.0.0:5000
📚 Knowledge base: 0 chunks indexed
🤖 Model: meta-llama/Llama-3.2-3B-Instruct
💾 GPU: NVIDIA GeForce RTX 3080

====================================================================
 Server ready! Access at http://localhost:5000
====================================================================
```

## Step 9: Test the API

### Test Health Endpoint
```bash
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "ok",
  "model_loaded": true,
  "gpu_available": true,
  "gpu_name": "NVIDIA GeForce RTX 3080",
  "rag_documents": 0,
  "rag_unique_docs": 0
}
```

### Test Chat Endpoint
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, who are you?", "mode": "chat"}'
```

### Upload a Test Document
```bash
# Create a test file
echo "This is a test document about artificial intelligence." > test.txt

# Upload it
curl -X POST http://localhost:5000/api/upload \
  -F "file=@test.txt"
```

### Test RAG-Enhanced Chat
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What does the document say about AI?", "mode": "chat", "use_rag": true}'
```

## Troubleshooting

### Issue: CUDA not available
```bash
# Check GPU
nvidia-smi

# Reinstall PyTorch
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify
python3 -c "import torch; print(torch.cuda.is_available())"
```

### Issue: Model download fails
```bash
# Check token
echo $HUGGINGFACE_TOKEN

# Try manual download
huggingface-cli login --token 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
huggingface-cli download meta-llama/Llama-3.2-3B-Instruct
```

### Issue: Out of memory
Edit `config.py`:
```python
USE_4BIT_QUANTIZATION = True  # Must be True for 8GB GPUs
MAX_NEW_TOKENS = 512  # Reduce if still having issues
```

### Issue: Port already in use
```bash
# Find process using port 5000
lsof -i :5000

# Kill it or change port in config.py
FLASK_PORT = 5001
```

## Next Steps

1. **Upload Documents**: Upload PDFs, DOCX, or other files to build your knowledge base
2. **Test Modes**: Try different modes (chat, summarize, deep-research, coding)
3. **Integrate Frontend**: Connect your frontend to the backend API
4. **Monitor Performance**: Use `nvidia-smi` to monitor GPU usage

## Performance Tips

### For Faster Responses
- Ensure GPU is being used (check `nvidia-smi`)
- Reduce `MAX_NEW_TOKENS` in config.py
- Use 4-bit quantization (enabled by default)

### For Better Quality
- Increase `MAX_NEW_TOKENS` (if you have VRAM)
- Upload relevant documents for RAG context
- Adjust `TEMPERATURE` (lower = more focused, higher = more creative)

### For Large Document Collections
- Increase `TOP_K_RETRIEVAL` for more context
- Adjust `CHUNK_SIZE` based on document types
- Monitor ChromaDB performance

## Connecting Frontend

Your frontend should make requests to:
```
http://localhost:5000/api/chat
http://localhost:5000/api/upload
http://localhost:5000/api/documents
etc.
```

Example fetch request:
```javascript
const response = await fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userInput,
    mode: 'chat',
    use_rag: true
  })
});

const data = await response.json();
console.log(data.response);
```

## Production Deployment

For production:
1. Set `FLASK_DEBUG = False` in config.py
2. Use a production WSGI server (gunicorn, uWSGI)
3. Add authentication/authorization
4. Set up HTTPS
5. Configure CORS properly
6. Add rate limiting
7. Monitor logs and errors

## Success Checklist

- [ ] WSL 2 installed and running
- [ ] NVIDIA GPU detected with `nvidia-smi`
- [ ] PyTorch installed with CUDA support
- [ ] All dependencies installed
- [ ] Llama model downloaded
- [ ] Server starts without errors
- [ ] Health endpoint returns success
- [ ] Chat endpoint responds correctly
- [ ] Document upload works
- [ ] RAG search retrieves context

If all checked, you're ready to go! 🚀
