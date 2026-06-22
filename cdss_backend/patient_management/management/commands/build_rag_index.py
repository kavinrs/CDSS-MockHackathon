"""
Django Management Command: build_rag_index

This command loads medical guideline documents from data/guidelines/,
chunks them, and adds them to a ChromaDB collection for RAG retrieval.

Usage:
    python manage.py build_rag_index

Purpose:
    - Academic demonstration of offline RAG index building
    - One-time setup to populate ChromaDB with medical guidelines
    - Prints clear progress messages for educational purposes

Requirements: 6.1-6.5, 16.1
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from rag.document_loader import DocumentLoader
from rag.document_chunker import DocumentChunker
from rag.vector_store import VectorStore


class Command(BaseCommand):
    help = 'Build RAG index by loading medical guidelines and adding them to ChromaDB'

    def add_arguments(self, parser):
        """Add optional command-line arguments."""
        parser.add_argument(
            '--guidelines-dir',
            type=str,
            default='data/guidelines',
            help='Path to directory containing guideline files (default: data/guidelines)'
        )
        parser.add_argument(
            '--collection-name',
            type=str,
            default='medical_guidelines',
            help='ChromaDB collection name (default: medical_guidelines)'
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=500,
            help='Chunk size in characters (default: 500)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing collection before adding new documents'
        )

    def handle(self, *args, **options):
        """Execute the command to build the RAG index."""
        
        # Print header
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('Building RAG Index for Clinical Decision Support System'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        # Get command options
        guidelines_dir = options['guidelines_dir']
        collection_name = options['collection_name']
        chunk_size = options['chunk_size']
        clear_collection = options['clear']
        
        # Resolve path relative to project root
        if not os.path.isabs(guidelines_dir):
            # Assume path is relative to project root (one level up from cdss_backend)
            project_root = os.path.dirname(settings.BASE_DIR)
            guidelines_dir = os.path.join(project_root, guidelines_dir)
        
        self.stdout.write(f"📁 Guidelines Directory: {guidelines_dir}")
        self.stdout.write(f"📦 Collection Name: {collection_name}")
        self.stdout.write(f"✂️  Chunk Size: {chunk_size} characters")
        self.stdout.write(f"🗑️  Clear Existing: {clear_collection}\n")
        
        # Step 1: Load documents
        self.stdout.write(self.style.WARNING('Step 1: Loading Medical Guidelines'))
        self.stdout.write('-' * 70)
        
        try:
            documents = DocumentLoader.load_documents(guidelines_dir)
            
            if not documents:
                self.stdout.write(self.style.ERROR(f"\n❌ No documents found in {guidelines_dir}"))
                self.stdout.write(self.style.ERROR("Please ensure .txt guideline files exist in the directory."))
                return
            
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded {len(documents)} documents\n"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error loading documents: {str(e)}"))
            return
        
        # Step 2: Chunk documents
        self.stdout.write(self.style.WARNING('Step 2: Chunking Documents'))
        self.stdout.write('-' * 70)
        
        try:
            chunks = DocumentChunker.chunk_documents(documents, chunk_size=chunk_size)
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(chunks)} chunks from {len(documents)} documents\n"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error chunking documents: {str(e)}"))
            return
        
        # Step 3: Initialize ChromaDB
        self.stdout.write(self.style.WARNING('Step 3: Initializing ChromaDB Collection'))
        self.stdout.write('-' * 70)
        
        try:
            # Initialize vector store with default path
            vector_store = VectorStore(persist_directory="./chroma_db")
            
            # Initialize or get collection
            vector_store.initialize_collection(collection_name=collection_name)
            
            # Clear collection if requested
            if clear_collection:
                self.stdout.write("🗑️  Clearing existing collection...")
                vector_store.clear_collection()
            
            self.stdout.write(self.style.SUCCESS(f"✅ Collection '{collection_name}' initialized\n"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error initializing ChromaDB: {str(e)}"))
            return
        
        # Step 4: Add documents to ChromaDB
        self.stdout.write(self.style.WARNING('Step 4: Adding Documents to ChromaDB'))
        self.stdout.write('-' * 70)
        self.stdout.write("⏳ Generating embeddings and storing documents...")
        self.stdout.write("(This may take a few seconds...)\n")
        
        try:
            vector_store.add_documents(chunks)
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully added {len(chunks)} chunks to ChromaDB\n"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error adding documents to ChromaDB: {str(e)}"))
            return
        
        # Step 5: Display statistics
        self.stdout.write(self.style.WARNING('Step 5: Final Statistics'))
        self.stdout.write('-' * 70)
        
        try:
            collection_info = vector_store.get_collection_info()
            
            self.stdout.write(f"📊 Collection Name: {collection_info['name']}")
            self.stdout.write(f"📊 Total Documents: {collection_info['count']}")
            self.stdout.write(f"📊 Source Files Processed: {len(documents)}")
            self.stdout.write(f"📊 Total Chunks Created: {len(chunks)}")
            self.stdout.write(f"📊 Average Chunks per File: {len(chunks) / len(documents):.1f}")
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Could not retrieve statistics: {str(e)}"))
        
        # Success message
        self.stdout.write('\n' + self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('✨ RAG Index Built Successfully!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('\nThe RAG system is now ready to retrieve medical guidelines.'))
        self.stdout.write(self.style.SUCCESS('You can test retrieval with the RAGRetriever class.\n'))
