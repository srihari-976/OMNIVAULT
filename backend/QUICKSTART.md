# 🚀 Quick Start Guide

Get your Lumina RAG backend running in 5 steps!

## Prerequisites Check ✅

Before starting, ensure you have:
- [ ] Windows with WSL 2 (Ubuntu)
- [ ] NVIDIA GPU (8GB+ VRAM recommended)
- [ ] Python 3.8+
- [ ] ~15GB free disk space

Quick check:
```bash
wsl --version
nvidia-smi
python3 --version
```

---
source torch_env/bin/activate
 
## Step 1: Install PyTorch with CUDA (3 minutes)

```bash
cd "d:/Project/New folder (2)/backend"

# Install PyTorch with CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

**Expected output:** `CUDA: True`

---

## Step 2: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

This installs:
- Flask & Flask-CORS
- Transformers & Accelerate
- ChromaDB & Sentence Transformers
- Document processors (PyMuPDF, python-docx, etc.)

---

## Step 3: Verify GPU Setup (1 minute)

```bash
chmod +x setup_gpu.sh
./setup_gpu.sh
```

Should show:
```
✓ NVIDIA driver detected!
✓ CUDA toolkit installed!
✓ GPU is ready for use!
```

---

## Step 4: Download Llama Model (10-20 minutes)

```bash
python download_model.py
```

This will:
- Authenticate with your HuggingFace token (already configured)
- Download Llama 3.2 3B (~6-7 GB)
- Cache the model for reuse

**Note:** This is a one-time download. Subsequent starts will be instant.

---

## Step 5: Start the Server! (1 minute)

```bash
python app.py
```

You should see:
```
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

---

## Test It! (2 minutes)

Open a new terminal:

```bash
cd "d:/Project/New folder (2)/backend"

# Run all tests
python test_backend.py
```

Should show:
```
✓ PASS  Health Check
✓ PASS  Chat
✓ PASS  Document Upload
✓ PASS  RAG Search
✓ PASS  RAG-Enhanced Chat
✓ PASS  Summarization
✓ PASS  Documents List

Total: 7/7 tests passed
🎉 All tests passed! Your backend is working perfectly!
```

---

## Try It Out!

### Chat Test
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What can you do?", "mode": "chat"}'
```

### Upload a Document
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@sample_documents/artificial_intelligence.txt"
```

### Ask About the Document
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are applications of AI?", "mode": "chat", "use_rag": true}'
```

---

## Troubleshooting

### Problem: CUDA not available
```bash
# Check GPU
nvidia-smi

# Reinstall PyTorch
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Problem: Model download fails
```bash
# Check your token in .env
cat .env | grep HUGGINGFACE_TOKEN

# Try again
python download_model.py
```

### Problem: Out of memory
Edit `config.py`:
```python
USE_4BIT_QUANTIZATION = True  # Must be True
MAX_NEW_TOKENS = 512  # Reduce if needed
```

---

## Next Steps

1. **Upload your documents** to build knowledge base
2. **Test different modes**: chat, summarize, deep-research, coding
3. **Connect your frontend** to http://localhost:5000
4. **Monitor GPU usage**: `watch -n 1 nvidia-smi`

---

## Performance Tips

### Faster Responses
- Ensure GPU is being used: `nvidia-smi`
- Keep 4-bit quantization enabled
- Reduce `MAX_NEW_TOKENS` if needed

### Better Answers
- Upload relevant documents for context
- Use appropriate mode for task
- Adjust temperature (lower = focused, higher = creative)

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server status |
| `/api/chat` | POST | Multi-mode chat |
| `/api/summarize` | POST | Text summarization |
| `/api/deep-research` | POST | Research queries |
| `/api/code-assist` | POST | Coding help |
| `/api/upload` | POST | Upload documents |
| `/api/documents` | GET | List documents |
| `/api/search` | POST | Semantic search |

---

## Success Checklist

After completing all steps:

- [ ] PyTorch installed with CUDA
- [ ] All dependencies installed
- [ ] GPU detected and working
- [ ] Llama model downloaded
- [ ] Server starts successfully
- [ ] All tests pass
- [ ] Can make API requests

**If all checked: You're ready! 🎉**

---

## Getting Help

1. Check [README.md](README.md) for detailed documentation
2. See [SETUP_GUIDE.md](SETUP_GUIDE.md) for troubleshooting
3. Review server logs for error messages
4. Run `./setup_gpu.sh` to verify GPU setup

---

**Total Setup Time: ~20-30 minutes** (mostly waiting for model download)

**Once setup: Server starts in ~1 minute!**
