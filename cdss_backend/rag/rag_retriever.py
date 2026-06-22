"""
RAGRetriever: Simple retriever for medical guideline retrieval.
Uses ChromaDB vector store to find similar documents for clinical queries.
"""

from typing import List, Dict, Optional
from .vector_store import VectorStore


class RAGRetriever:
    """
    Retrieve relevant medical guideline chunks using ChromaDB similarity search.
    Simple wrapper around VectorStore that focuses on clinical query formatting.
    """
    
    def __init__(self, vector_store: VectorStore):
        """
        Initialize retriever with a VectorStore instance.
        
        Args:
            vector_store: Initialized VectorStore instance with loaded collection
        """
        self.vector_store = vector_store
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve top-k most relevant medical guideline chunks for a clinical query.
        
        Args:
            query: Clinical query string (e.g., "diabetes management guidelines")
            top_k: Number of results to return (default: 5)
            
        Returns:
            List of dictionaries with 'text', 'source_filename', and 'distance' keys.
            Returns empty list if no results found.
            
        Example:
            >>> retriever = RAGRetriever(vector_store)
            >>> results = retriever.retrieve("hypertension treatment", top_k=5)
            >>> for result in results:
            ...     print(f"Source: {result['source_filename']}")
            ...     print(f"Text: {result['text'][:100]}...")
        """
        # Handle empty or invalid query
        if not query or not query.strip():
            print("Warning: Empty query provided to retrieve()")
            return []
        
        # Query the vector store
        try:
            results = self.vector_store.query(query_text=query, top_k=top_k)
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []
        
        # Handle empty results gracefully
        if not results:
            print(f"No results found for query: '{query}'")
            return []
        
        # Format results for clinical use
        formatted_results = []
        for result in results:
            formatted_results.append({
                'text': result.get('text', ''),
                'source_filename': result.get('metadata', {}).get('source_filename', 'unknown'),
                'distance': result.get('distance', 0.0)
            })
        
        print(f"Retrieved {len(formatted_results)} chunks for query: '{query}'")
        return formatted_results
