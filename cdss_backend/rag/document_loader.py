"""
DocumentLoader: Simple class to load medical guideline documents from the file system.
Supports TXT files for simplicity (academic project focus).
"""

import os
from typing import List, Dict


class DocumentLoader:
    """
    Load medical guideline documents from a directory.
    Keeps it simple - just reads TXT files.
    """
    
    @staticmethod
    def load_documents(directory: str) -> List[Dict[str, str]]:
        """
        Load all TXT files from the specified directory.
        
        Args:
            directory: Path to directory containing guideline files
            
        Returns:
            List of dictionaries with 'content' and 'metadata' keys
            metadata includes 'source_filename'
        """
        documents = []
        
        # Check if directory exists
        if not os.path.exists(directory):
            print(f"Warning: Directory {directory} does not exist")
            return documents
        
        # Load all TXT files
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                filepath = os.path.join(directory, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source_filename': filename,
                            'filepath': filepath
                        }
                    })
                    print(f"Loaded: {filename} ({len(content)} characters)")
                    
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
        
        print(f"\nTotal documents loaded: {len(documents)}")
        return documents
