# 🚀 OMNIVAULT
## AI-Powered Intelligent Chat Assistant with RAG Technology

---

# 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [System Architecture](#-system-architecture)
5. [How It Works](#-how-it-works)
6. [Chat Modes](#-chat-modes)
7. [RAG Pipeline](#-rag-pipeline)
8. [User Interface](#-user-interface)
9. [Future Enhancements](#-future-enhancements)

---

# 🎯 Project Overview

**OMNIVAULT** is a modern, AI-powered chat assistant that combines the power of Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) technology to provide intelligent, context-aware responses.

### What Makes It Special?
- **Local AI Model**: Runs entirely on your machine - no cloud API costs
- **Document Intelligence**: Upload your documents and chat with them
- **Deep Research**: Web search integration for comprehensive research
- **Persistent Memory**: Chat history is saved and restored across sessions
- **Beautiful UI**: Modern, responsive interface with dark/light themes

---

# ✨ Key Features

## 💬 Intelligent Chat
- Natural conversation with AI
- Context-aware responses using conversation history
- Support for follow-up questions

## 📄 Document Upload & Processing
- Upload PDFs, Word documents, text files, images, and code
- Automatic text extraction and indexing
- Asynchronous processing for large files

## 🔍 RAG (Retrieval-Augmented Generation)
- Semantic search across uploaded documents
- ChromaDB vector database for efficient retrieval
- Context injection for accurate answers

## 🌐 Deep Research Mode
- Live web search integration (Tavily API)
- Combines web results with local documents
- Comprehensive research synthesis

## 📝 Summarization
- Intelligent text summarization
- Works with uploaded documents
- Clean, structured output

## 💾 Persistent Chat History
- All conversations saved automatically
- Resume conversations across sessions
- Sidebar with chat management

## 🎨 Modern UI/UX
- Dark theme (Navy Blue) and Light theme (Beige)
- Responsive design for all screen sizes
- Code block rendering with syntax highlighting
- Copy button for code snippets

---

# 🛠 Technology Stack

## Frontend
| Technology | Purpose |
|------------|---------|
| **React.js** | UI Framework |
| **JavaScript (ES6+)** | Programming Language |
| **CSS3** | Styling & Animations |
| **Marked.js** | Markdown Rendering |
| **Highlight.js** | Code Syntax Highlighting |

## Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.12** | Programming Language |
| **Flask** | Web Framework & REST API |
| **Flask-CORS** | Cross-Origin Resource Sharing |

## AI/ML Stack
| Technology | Purpose |
|------------|---------|
| **Llama 3.2 3B Instruct** | Large Language Model |
| **Hugging Face Transformers** | Model Loading & Inference |
| **PyTorch** | Deep Learning Framework |
| **BitsAndBytes** | 4-bit Quantization for GPU efficiency |

## RAG & Vector Database
| Technology | Purpose |
|------------|---------|
| **ChromaDB** | Vector Database |
| **Sentence-Transformers** | Text Embeddings (all-MiniLM-L6-v2) |
| **LangChain (concepts)** | Document Chunking |

## Document Processing
| Technology | Purpose |
|------------|---------|
| **PyPDF2** | PDF Extraction |
| **python-docx** | Word Document Processing |
| **Pillow + pytesseract** | Image OCR |

## Web Search
| Technology | Purpose |
|------------|---------|
| **Tavily API** | Real-time Web Search |

---

# 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        OMNIVAULT ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────┘

     ┌──────────────────┐         ┌──────────────────┐
     │   React Frontend │◄───────►│   Flask Backend  │
     │    (Port 3000)   │  HTTP   │    (Port 5000)   │
     └──────────────────┘         └────────┬─────────┘
                                           │
          ┌────────────────────────────────┼────────────────────────────────┐
          │                                │                                │
          ▼                                ▼                                ▼
   ┌──────────────┐              ┌──────────────────┐             ┌─────────────────┐
   │   Llama 3.2  │              │    ChromaDB      │             │   Tavily API    │
   │   3B Model   │              │  Vector Database │             │   Web Search    │
   │  (GPU/CPU)   │              │   (Embeddings)   │             │   (Optional)    │
   └──────────────┘              └──────────────────┘             └─────────────────┘
          │                                │
          │                                │
          ▼                                ▼
   ┌──────────────┐              ┌──────────────────┐
   │   Response   │              │    Document      │
   │  Generation  │◄─────────────│    Retrieval     │
   └──────────────┘   Context    └──────────────────┘
```

---

# ⚙️ How It Works

## 1️⃣ User Input
User types a message or uploads a document through the React frontend.

## 2️⃣ Request Processing
The Flask backend receives the request and determines the mode (Chat, Summarize, Deep Research).

## 3️⃣ Document Retrieval (RAG)
- User query is converted to embeddings
- ChromaDB performs semantic similarity search
- Top-K relevant document chunks are retrieved

## 4️⃣ Context Augmentation
- Retrieved documents are added to the prompt
- Conversation history is included for context
- System prompts guide the model's behavior

## 5️⃣ LLM Generation
- Llama 3.2 3B model generates the response
- Uses 4-bit quantization for memory efficiency
- Runs on GPU (CUDA) or CPU

## 6️⃣ Response Formatting
- Response is post-processed for clean formatting
- Markdown is rendered in the frontend
- Code blocks get syntax highlighting

---

# 🎭 Chat Modes

## 💬 Chat Mode
- **Purpose**: General conversation with document context
- **Temperature**: 0.7 (balanced creativity)
- **RAG Enabled**: Yes (Top 3 documents)
- **Max Tokens**: 1024

## 📝 Summarize Mode
- **Purpose**: Condensed summaries of text/documents
- **Temperature**: 0.3 (focused, deterministic)
- **RAG Enabled**: No
- **Max Tokens**: 512

## 🔬 Deep Research Mode
- **Purpose**: Comprehensive research with web + documents
- **Temperature**: 0.5 (balanced)
- **RAG Enabled**: Yes (Top 10 documents)
- **Web Search**: Enabled
- **Max Tokens**: 2048

## 💻 Coding Mode
- **Purpose**: Code assistance and generation
- **Temperature**: 0.2 (precise, minimal hallucination)
- **RAG Enabled**: Yes (Top 5 documents)
- **Max Tokens**: 1536

---

# 📚 RAG Pipeline

## Document Ingestion Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Upload     │────►│   Extract    │────►│    Chunk     │────►│   Embed &    │
│   Document   │     │    Text      │     │    Text      │     │    Store     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
     PDF/DOCX            PyPDF2/           512 chars/chunk         ChromaDB
     TXT/Images          docx/OCR          50 char overlap       Vector Store
```

## Query Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│   Generate   │────►│   Vector     │────►│  Retrieve    │
│    Query     │     │  Embeddings  │     │   Search     │     │  Top-K Docs  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                      MiniLM-L6-v2         Cosine Similarity     Relevant Chunks
```

## Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Speed**: Fast inference
- **Quality**: High semantic understanding

---

# 🖥 User Interface

## Sidebar
- ✅ Chat history list
- ✅ New chat button
- ✅ Delete chat option
- ✅ Rename chat
- ✅ Settings access

## Chat Area
- ✅ Message bubbles (user & assistant)
- ✅ Markdown rendering
- ✅ Code blocks with copy button
- ✅ File upload with visual chips
- ✅ Mode selector dropdown
- ✅ Thinking indicator during generation

## Settings
- ✅ Theme toggle (Dark/Light)
- ✅ Privacy policy
- ✅ Terms of use

---

# 🚀 Future Enhancements

## Planned Features
- 🔜 Streaming responses (real-time token display)
- 🔜 Voice input/output support
- 🔜 Multi-language support
- 🔜 Custom model fine-tuning
- 🔜 Plugin system for extensions
- 🔜 Export conversations to PDF
- 🔜 Collaborative chat sessions
- 🔜 Advanced document management

## Performance Improvements
- 🔜 Model caching optimization
- 🔜 Batch processing for multiple documents
- 🔜 Response caching for common queries

---

# 📊 Technical Specifications

| Specification | Value |
|---------------|-------|
| **LLM Model** | Llama 3.2 3B Instruct |
| **Quantization** | 4-bit (BitsAndBytes) |
| **Embedding Model** | all-MiniLM-L6-v2 |
| **Vector Database** | ChromaDB |
| **Chunk Size** | 512 characters |
| **Chunk Overlap** | 50 characters |
| **Max File Size** | 50 MB |
| **Supported Formats** | PDF, DOCX, TXT, MD, PNG, JPG, PY, JS, etc. |

---

# 🎓 Conclusion

**OMNIVAULT** demonstrates the power of combining:
- 🤖 **Local LLMs** for privacy and cost-efficiency
- 📚 **RAG Technology** for accurate, grounded responses
- 🌐 **Web Search** for up-to-date information
- 💾 **Persistent Storage** for seamless user experience
- 🎨 **Modern UI** for intuitive interaction

### The Future of AI Assistants is Local, Intelligent, and Context-Aware!

---

# 🙏 Thank You!

## Questions?

**Project**: OMNIVAULT  
**Technologies**: React, Flask, Llama 3.2, ChromaDB, RAG  
**GitHub**: [Your Repository Link]

---
