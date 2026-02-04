# OMNIVAULT

A ChatGPT-inspired chat interface built with React (frontend) and Flask (backend) with RAG capabilities, featuring dark and light themes, code block rendering, and seamless backend integration.

## Project Structure

```
.
├── frontend/          # React frontend application
├── backend/           # Flask backend API with RAG
└── README.md
```

## Features

- Modern chat interface inspired by ChatGPT
- Dark theme (Navy Blue) and Light theme (Beige) with toggle button
- Collapsible sidebar with chat history
- New chat functionality
- Settings modal with functional controls
- Code block rendering with copy functionality
- File upload support (PDF, DOCX, images, etc.)
- Multiple chat modes: Chat, Summarize, Deep Research
- RAG (Retrieval-Augmented Generation) support
- Conversation history context
- Responsive design
- Seamless backend integration

## Setup Instructions

### Backend Setup (Run First)

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. Install PyTorch (choose based on your system):
   - **CUDA (GPU)**: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
   - **CPU only**: `pip install torch torchvision torchaudio`

5. Install other dependencies:
```bash
pip install -r requirements.txt
```

6. (Optional) Download the model if needed:
```bash
python download_model.py
```

7. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

**Note**: The model loads in the background. The server will start immediately, but you may need to wait a few minutes for the model to fully load before chat responses work.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000` and automatically proxy API requests to the backend.

## Usage

1. **Start the backend first** (important!):
   ```bash
   cd backend
   python app.py
   ```

2. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

4. The interface will automatically connect to the backend

5. Features you can use:
   - **Chat**: Normal conversation with RAG support
   - **Summarize**: Summarize text or documents
   - **Deep Research**: Extensive research with multiple document sources
   - **File Upload**: Upload PDFs, DOCX, images, or code files for RAG indexing
   - **Code Blocks**: Code in responses is automatically formatted with copy buttons

## API Endpoints

The backend provides the following endpoints:

- `POST /api/chat` - Main chat endpoint
- `POST /api/upload` - File upload for RAG indexing
- `GET /api/documents` - Get all indexed documents
- `GET /health` - Health check endpoint

## Troubleshooting

### Backend not connecting
- Make sure the backend is running on port 5000
- Check that CORS is enabled (it should be by default)
- Verify the proxy setting in `frontend/package.json` points to `http://localhost:5000`

### Model not loading
- Check backend logs for errors
- Ensure you have enough RAM/VRAM
- Try reducing `MAX_NEW_TOKENS` in `backend/config.py` if you have memory issues

### Frontend errors
- Make sure the backend is running before starting the frontend
- Check browser console for detailed error messages
- Verify the proxy configuration in `package.json`

## Notes

- The frontend is configured to proxy API requests to `http://localhost:5000`
- Code blocks in responses are automatically detected and formatted
- Conversation history is maintained and sent to the backend for context
- File uploads are indexed into the RAG system for enhanced responses

