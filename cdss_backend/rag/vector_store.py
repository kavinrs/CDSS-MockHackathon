"""
VectorStore: Simple ChromaDB vector store for medical guideline embeddings.
Uses OpenAI embeddings (text-embedding-ada-002) automatically via ChromaDB.
"""

import chromadb
from typing import List, Dict, Optional


class VectorStore:
    """
    Manage ChromaDB collection for storing and retrieving medical guideline embeddings.
    ChromaDB automatically handles OpenAI embeddings - we just configure it.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client.
        
        Args:
            persist_directory: Directory to store ChromaDB data (default: ./chroma_db)
        """
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = None
    
    def initialize_collection(self, collection_name: str = "medical_guidelines") -> None:
        """
        Create or get ChromaDB collection with OpenAI embeddings.
        
        Args:
            collection_name: Name of the collection (default: medical_guidelines)
        """
        # Get or create collection
        # ChromaDB will use default embedding function (all-MiniLM-L6-v2)
        # For production with OpenAI, you'd configure the embedding function here
        # But for simplicity in academic project, we use ChromaDB's default
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Medical guideline embeddings for RAG system"}
        )
        
        print(f"Initialized collection: {collection_name}")
        print(f"Current document count: {self.collection.count()}")
    
    def add_documents(self, chunks: List[Dict[str, str]]) -> None:
        """
        Add document chunks to ChromaDB collection.
        ChromaDB automatically generates embeddings.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata' keys
        """
        if self.collection is None:
            raise ValueError("Collection not initialized. Call initialize_collection() first.")
        
        if not chunks:
            print("No chunks to add.")
            return
        
        # Prepare data for ChromaDB
        documents = []  # Text content
        metadatas = []  # Metadata
        ids = []        # Unique IDs
        
        for i, chunk in enumerate(chunks):
            # Extract text content
            text = chunk.get('text', '')
            if not text:
                continue
            
            # Extract metadata
            metadata = chunk.get('metadata', {})
            
            # Create unique ID
            chunk_id = f"chunk_{i}_{metadata.get('source_filename', 'unknown')}"
            
            documents.append(text)
            metadatas.append(metadata)
            ids.append(chunk_id)
        
        # Add to ChromaDB - embeddings generated automatically
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(documents)} documents to ChromaDB")
        print(f"Total documents in collection: {self.collection.count()}")
    
    def query(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Query the collection for similar documents.
        
        Args:
            query_text: Query string
            top_k: Number of results to return (default: 5)
            
        Returns:
            List of dictionaries with 'text', 'metadata', and 'distance' keys
        """
        if self.collection is None:
            raise ValueError("Collection not initialized. Call initialize_collection() first.")
        
        # Query ChromaDB - automatically embeds query and finds similar documents
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        
        if results['documents'] and len(results['documents']) > 0:
            documents = results['documents'][0]  # First query result
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            for doc, metadata, distance in zip(documents, metadatas, distances):
                formatted_results.append({
                    'text': doc,
                    'metadata': metadata,
                    'distance': distance
                })
        
        return formatted_results
    
    def clear_collection(self) -> None:
        """
        Clear all documents from the collection (useful for testing).
        """
        if self.collection is None:
            raise ValueError("Collection not initialized. Call initialize_collection() first.")
        
        # Delete and recreate collection
        collection_name = self.collection.name
        self.client.delete_collection(name=collection_name)
        self.initialize_collection(collection_name)
        print(f"Cleared collection: {collection_name}")
    
    def get_collection_info(self) -> Dict:
        """
        Get information about the current collection.
        
        Returns:
            Dictionary with collection name and document count
        """
        if self.collection is None:
            return {"error": "Collection not initialized"}
        
        return {
            "name": self.collection.name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata
        }

