"""
DocumentChunker: Simple class to split documents into chunks for RAG processing.
Uses character-based chunking with ~500 character chunks (academic project simplicity).
"""

from typing import List, Dict


class DocumentChunker:
    """
    Split documents into chunks for embedding and retrieval.
    Simple character-based splitting - no complex overlap logic.
    """
    
    @staticmethod
    def chunk_documents(documents: List[Dict[str, str]], chunk_size: int = 500) -> List[Dict[str, str]]:
        """
        Split documents into chunks of approximately chunk_size characters.
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'
            chunk_size: Target size for each chunk in characters (default: 500)
            
        Returns:
            List of chunk dictionaries with 'text' and 'metadata' keys
        """
        chunks = []
        
        for doc in documents:
            content = doc['content']
            metadata = doc['metadata']
            
            # Split content into chunks
            doc_chunks = DocumentChunker._split_text(content, chunk_size)
            
            # Create chunk objects with metadata
            for i, chunk_text in enumerate(doc_chunks):
                chunk = {
                    'text': chunk_text,
                    'metadata': {
                        **metadata,  # Include original metadata
                        'chunk_index': i,
                        'total_chunks': len(doc_chunks)
                    }
                }
                chunks.append(chunk)
        
        print(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks
    
    @staticmethod
    def _split_text(text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks of approximately chunk_size characters.
        Tries to split at sentence boundaries for better readability.
        
        Args:
            text: Text content to split
            chunk_size: Target chunk size in characters
            
        Returns:
            List of text chunks
        """
        # If text is smaller than chunk_size, return as single chunk
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by sentences (simple approach - split on '. ')
        sentences = text.split('. ')
        
        for sentence in sentences:
            # Add period back (except for last sentence if it didn't have one)
            if not sentence.endswith('.'):
                sentence = sentence + '.'
            
            # If adding this sentence would exceed chunk_size, save current chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk if it has content
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
