"""
Web Search Module
Integrates with Tavily API for live web search capabilities
"""

import os
import requests
from typing import List, Dict, Optional
import traceback
from config import Config


class WebSearch:
    """Handles web search using Tavily API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.WEB_SEARCH_API_KEY
        self.provider = Config.WEB_SEARCH_PROVIDER
        self.max_results = Config.MAX_SEARCH_RESULTS
        
        # Tavily API endpoint
        self.tavily_url = "https://api.tavily.com/search"
    
    def is_available(self) -> bool:
        """Check if web search is available (API key configured)"""
        return bool(self.api_key and self.api_key.strip())
    
    def search_web(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        Search the web using Tavily API
        
        Args:
            query: Search query
            max_results: Maximum number of results (defaults to config value)
            
        Returns:
            List of search result dicts with url, title, content, score
        """
        if not self.is_available():
            print("⚠️ Web search API key not configured")
            return []
        
        try:
            max_results = max_results or self.max_results
            
            # Prepare request
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",  # Use advanced search for better results
                "include_answer": True,  # Get AI-generated answer summary
                "include_raw_content": False,  # Don't need full HTML
                "include_images": False
            }
            
            print(f"🔍 Searching web for: '{query}'")
            
            # Make request
            response = requests.post(
                self.tavily_url,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract results
            results = []
            for result in data.get('results', []):
                results.append({
                    'url': result.get('url'),
                    'title': result.get('title'),
                    'content': result.get('content'),
                    'score': result.get('score', 0)
                })
            
            # Add AI answer if available
            ai_answer = data.get('answer')
            if ai_answer:
                results.insert(0, {
                    'url': None,
                    'title': 'AI Summary',
                    'content': ai_answer,
                    'score': 1.0,
                    'is_summary': True
                })
            
            print(f"✓ Found {len(results)} web results")
            return results
            
        except requests.exceptions.Timeout:
            print("❌ Web search request timed out")
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Web search API error: {str(e)}")
            traceback.print_exc()
            return []
        except Exception as e:
            print(f"❌ Unexpected error in web search: {str(e)}")
            traceback.print_exc()
            return []
    
    def format_results_for_context(self, results: List[Dict]) -> str:
        """
        Format search results into context string for LLM
        
        Args:
            results: List of search result dicts
            
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        context_parts = []
        context_parts.append("=== WEB SEARCH RESULTS ===\n")
        
        for idx, result in enumerate(results, 1):
            if result.get('is_summary'):
                context_parts.append(f"AI Summary:\n{result['content']}\n")
            else:
                title = result.get('title', 'Untitled')
                content = result.get('content', '')
                url = result.get('url', '')
                
                context_parts.append(f"{idx}. {title}")
                if url:
                    context_parts.append(f"   URL: {url}")
                context_parts.append(f"   {content}\n")
        
        context_parts.append("=== END WEB SEARCH RESULTS ===\n")
        
        return "\n".join(context_parts)


def synthesize_web_results(query: str, web_results: List[Dict], rag_results: List[Dict], model_manager) -> str:
    """
    Use LLM to synthesize web search results and RAG results into comprehensive answer
    
    Args:
        query: User's query
        web_results: Results from web search
        rag_results: Results from RAG retrieval
        model_manager: Model manager instance for generation
        
    Returns:
        Synthesized answer
    """
    try:
        # Build context from both sources
        context_parts = []
        
        # Add web search results
        if web_results:
            web_searcher = WebSearch()
            context_parts.append(web_searcher.format_results_for_context(web_results))
        
        # Add RAG results
        if rag_results:
            context_parts.append("\n=== KNOWLEDGE BASE DOCUMENTS ===\n")
            for idx, doc in enumerate(rag_results, 1):
                filename = doc['metadata'].get('filename', 'Unknown')
                content = doc['document']
                context_parts.append(f"{idx}. From {filename}:\n{content}\n")
            context_parts.append("=== END KNOWLEDGE BASE DOCUMENTS ===\n")
        
        full_context = "\n".join(context_parts)
        
        # Build synthesis prompt
        prompt = f"""You are a research assistant conducting deep research. You have access to both live web search results and knowledge base documents.

{full_context}

User Query: {query}

Instructions:
1. Synthesize information from BOTH web sources and knowledge base documents
2. Provide a comprehensive, well-structured answer
3. Cross-reference multiple sources when possible
4. Cite your sources using [Source: title/filename]
5. If sources conflict, mention the different perspectives
6. Structure your answer with clear sections if appropriate
7. Be thorough but concise

Provide your comprehensive research answer:"""
        
        # Generate response
        response = model_manager.generate(
            prompt,
            max_new_tokens=2048,
            temperature=0.6
        )
        
        return response
        
    except Exception as e:
        print(f"❌ Error synthesizing results: {str(e)}")
        traceback.print_exc()
        return "Error: Could not synthesize research results"
