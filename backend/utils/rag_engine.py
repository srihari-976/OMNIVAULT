"""
RAG Engine Module
Handles document chunking, embedding generation, vector storage, and semantic search
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config import Config
import uuid
from datetime import datetime

class RAGEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGEngine, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            print("Initializing RAG Engine...")
            self.embedding_model = self._load_embedding_model()
            self.client = self._init_chromadb()
            self.collection = self._get_or_create_collection()
            self.initialized = True
            print(f"✓ RAG Engine initialized with {self.collection.count()} documents")
    
    def _load_embedding_model(self):
        """Load sentence transformer model for embeddings"""
        print(f"Loading embedding model: {Config.EMBEDDING_MODEL}")
        model = SentenceTransformer(Config.EMBEDDING_MODEL)
        print("✓ Embedding model loaded")
        return model
    
    def _init_chromadb(self):
        """Initialize ChromaDB client"""
        client = chromadb.PersistentClient(
            path=Config.VECTOR_DB_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        return client
    
    def _get_or_create_collection(self):
        """Get or create the main document collection"""
        try:
            collection = self.client.get_collection(name=Config.COLLECTION_NAME)
            print(f"✓ Using existing collection: {Config.COLLECTION_NAME}")
        except:
            collection = self.client.create_collection(
                name=Config.COLLECTION_NAME,
                metadata={"description": "Lumina RAG document collection"}
            )
            print(f"✓ Created new collection: {Config.COLLECTION_NAME}")
        return collection
    
    @staticmethod
    def chunk_text(text, chunk_size=None, overlap=None):
        """
        Split text into chunks with overlap
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or Config.CHUNK_SIZE
        overlap = overlap or Config.CHUNK_OVERLAP
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If not at the end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for sep in ['. ', '.\n', '! ', '?\n', '? ']:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep != -1:
                        end = start + last_sep + len(sep)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    def generate_embeddings(self, texts):
        """Generate embeddings for a list of texts"""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def add_document(self, filename, text, metadata=None):
        """
        Add a document to the vector database
        
        Args:
            filename: Name of the source file
            text: Extracted text from document
            metadata: Additional metadata (dict)
        
        Returns:
            Number of chunks added
        """
        # Chunk the text
        chunks = self.chunk_text(text)
        
        if not chunks:
            print(f"No chunks generated for {filename}")
            return 0
        
        print(f"Generated {len(chunks)} chunks from {filename}")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)
        
        # Prepare metadata
        base_metadata = {
            "filename": filename,
            "timestamp": datetime.now().isoformat(),
            "total_chunks": len(chunks)
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        # Generate unique IDs
        doc_id = str(uuid.uuid4())
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Prepare metadata for each chunk
        metadatas = []
        for i in range(len(chunks)):
            chunk_meta = base_metadata.copy()
            chunk_meta["chunk_index"] = i
            chunk_meta["doc_id"] = doc_id
            metadatas.append(chunk_meta)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        print(f"✓ Added {len(chunks)} chunks to vector database")
        return len(chunks)
    
    def semantic_search(self, query, top_k=None, filter_metadata=None):
        """
        Perform semantic search on the vector database
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filter (dict)
        
        Returns:
            List of results with documents, metadata, and distances
        """
        top_k = top_k or Config.TOP_K_RETRIEVAL
        
        # Generate query embedding
        query_embedding = self.generate_embeddings(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results and results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'similarity': 1 - results['distances'][0][i] if 'distances' in results else None
                }
                
                # Filter by similarity threshold
                if result['similarity'] and result['similarity'] >= Config.SIMILARITY_THRESHOLD:
                    formatted_results.append(result)
        
        return formatted_results
    
    def delete_document(self, doc_id=None, filename=None):
        """Delete a document by ID or filename"""
        if doc_id:
            # Delete by doc_id
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                return len(results['ids'])
        
        if filename:
            # Delete by filename
            results = self.collection.get(
                where={"filename": filename}
            )
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                return len(results['ids'])
        
        return 0
    
    def get_all_documents(self):
        """Get list of all unique documents"""
        all_data = self.collection.get()
        
        if not all_data or not all_data['metadatas']:
            return []
        
        # Group by doc_id
        docs = {}
        for metadata in all_data['metadatas']:
            doc_id = metadata.get('doc_id')
            if doc_id and doc_id not in docs:
                docs[doc_id] = {
                    'doc_id': doc_id,
                    'filename': metadata.get('filename'),
                    'timestamp': metadata.get('timestamp'),
                    'total_chunks': metadata.get('total_chunks', 0)
                }
        
        return list(docs.values())
    
    def get_stats(self):
        """Get RAG engine statistics"""
        return {
            'total_chunks': self.collection.count(),
            'total_documents': len(self.get_all_documents()),
            'embedding_model': Config.EMBEDDING_MODEL,
            'collection_name': Config.COLLECTION_NAME
        }


if __name__ == "__main__":
    # Test RAG engine
    print("Testing RAG Engine...\n")
    
    rag = RAGEngine()
    
    # Test adding a document
    test_text = """
    This is a test document about artificial intelligence.
    AI is transforming many industries including healthcare, finance, and education.
    Machine learning models can process vast amounts of data.
    """
    
    rag.add_document("test.txt", test_text, {"type": "test"})
    
    # Test search
    results = rag.semantic_search("What is AI doing?", top_k=3)
    print(f"\nSearch results: {len(results)}")
    for r in results:
        print(f"- {r['document'][:100]}... (similarity: {r['similarity']:.3f})")
    
    # Stats
    print(f"\nStats: {rag.get_stats()}")
