"""
Test script for Lumina RAG Backend
Tests all major components and endpoints
"""

import requests
import os
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70 + "\n")

def test_health():
    """Test health endpoint"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        print(f"Status: {data.get('status')}")
        print(f"Model Loaded: {data.get('model_loaded')}")
        print(f"GPU Available: {data.get('gpu_available')}")
        print(f"GPU Name: {data.get('gpu_name')}")
        print(f"RAG Documents: {data.get('rag_documents')}")
        
        if data.get('status') == 'ok':
            print("\n✓ Health check passed!")
            return True
        else:
            print("\n✗ Health check failed!")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("Make sure the server is running: python app.py")
        return False

def test_chat():
    """Test chat endpoint"""
    print_section("TEST 2: Chat Endpoint")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": "Hello! Can you explain what you are in one sentence?",
                "mode": "chat"
            }
        )
        data = response.json()
        
        print(f"Response: {data.get('response')[:200]}...")
        print(f"Mode: {data.get('mode')}")
        print(f"Used RAG: {data.get('used_rag')}")
        
        print("\n✓ Chat test passed!")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_upload():
    """Test document upload"""
    print_section("TEST 3: Document Upload")
    
    # Create a test file
    test_content = """
    Artificial Intelligence and Machine Learning
    
    Artificial Intelligence (AI) is the simulation of human intelligence by machines.
    Machine Learning (ML) is a subset of AI that enables systems to learn from data.
    
    Key concepts:
    - Supervised Learning: Training with labeled data
    - Unsupervised Learning: Finding patterns in unlabeled data
    - Deep Learning: Neural networks with multiple layers
    - Natural Language Processing: Understanding human language
    - Computer Vision: Understanding images and video
    
    Applications:
    - Healthcare: Disease diagnosis, drug discovery
    - Finance: Fraud detection, algorithmic trading
    - Transportation: Autonomous vehicles
    - Education: Personalized learning
    """
    
    test_file = "test_ai_document.txt"
    with open(test_file, "w") as f:
        f.write(test_content)
    
    try:
        with open(test_file, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/api/upload",
                files={"file": f}
            )
        
        data = response.json()
        
        print(f"Message: {data.get('message')}")
        print(f"Filename: {data.get('filename')}")
        print(f"Chunks Added: {data.get('chunks_added')}")
        print(f"Word Count: {data.get('word_count')}")
        print(f"File Type: {data.get('file_type')}")
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        
        print("\n✓ Upload test passed!")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def test_rag_search():
    """Test RAG search"""
    print_section("TEST 4: RAG Search")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={
                "query": "What is machine learning?",
                "top_k": 3
            }
        )
        data = response.json()
        
        print(f"Query: {data.get('query')}")
        print(f"Results Found: {data.get('count')}")
        
        for i, result in enumerate(data.get('results', [])[:2], 1):
            print(f"\nResult {i}:")
            print(f"  Filename: {result.get('filename')}")
            print(f"  Similarity: {result.get('similarity'):.3f}")
            print(f"  Text: {result.get('text')[:100]}...")
        
        print("\n✓ RAG search test passed!")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_rag_chat():
    """Test chat with RAG context"""
    print_section("TEST 5: RAG-Enhanced Chat")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": "What are some applications of AI mentioned in the documents?",
                "mode": "chat",
                "use_rag": True
            }
        )
        data = response.json()
        
        print(f"Response: {data.get('response')[:300]}...")
        print(f"\nUsed RAG: {data.get('used_rag')}")
        print(f"Context Sources: {len(data.get('context_sources', []))}")
        
        for source in data.get('context_sources', []):
            print(f"  - {source.get('filename')} (similarity: {source.get('similarity'):.3f})")
        
        print("\n✓ RAG-enhanced chat test passed!")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_summarize():
    """Test summarization"""
    print_section("TEST 6: Summarization")
    
    text_to_summarize = """
    Climate change is one of the most pressing challenges facing humanity today. 
    It refers to long-term shifts in global temperatures and weather patterns. 
    While climate change is a natural phenomenon, human activities have been the 
    primary driver since the 1800s, mainly due to burning fossil fuels like coal, 
    oil, and gas. This produces greenhouse gases that trap heat in the atmosphere.
    
    The effects of climate change include rising sea levels, more frequent extreme 
    weather events, changes in precipitation patterns, and impacts on ecosystems 
    and biodiversity. Scientists worldwide agree that immediate action is needed 
    to limit global warming to 1.5°C above pre-industrial levels.
    
    Solutions include transitioning to renewable energy, improving energy efficiency, 
    protecting and restoring forests, and developing sustainable agricultural practices. 
    Both individual actions and systemic changes are necessary to address this challenge.
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/summarize",
            json={"text": text_to_summarize}
        )
        data = response.json()
        
        print(f"Original Length: {data.get('original_length')} characters")
        print(f"Summary Length: {data.get('summary_length')} characters")
        print(f"\nSummary:\n{data.get('summary')}")
        
        print("\n✓ Summarization test passed!")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_documents_list():
    """Test getting documents list"""
    print_section("TEST 7: List Documents")
    
    try:
        response = requests.get(f"{BASE_URL}/api/documents")
        data = response.json()
        
        print(f"Total Documents: {len(data.get('documents', []))}")
        print(f"Total Chunks: {data.get('stats', {}).get('total_chunks')}")
        print(f"Embedding Model: {data.get('stats', {}).get('embedding_model')}")
        
        for doc in data.get('documents', [])[:3]:
            print(f"\n  Document: {doc.get('filename')}")
            print(f"    ID: {doc.get('doc_id')}")
            print(f"    Chunks: {doc.get('total_chunks')}")
        
        print("\n✓ Documents list test passed!")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "LUMINA RAG BACKEND TEST SUITE" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    
    if not results[0][1]:
        print("\n❌ Server not responding. Please start the server first:")
        print("   python app.py\n")
        return
    
    results.append(("Chat", test_chat()))
    results.append(("Document Upload", test_upload()))
    results.append(("RAG Search", test_rag_search()))
    results.append(("RAG-Enhanced Chat", test_rag_chat()))
    results.append(("Summarization", test_summarize()))
    results.append(("Documents List", test_documents_list()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is working perfectly!")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
    
    print()

if __name__ == "__main__":
    main()
