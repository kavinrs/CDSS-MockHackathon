"""
Unit tests for VectorStore class.
Simple tests to verify ChromaDB integration works correctly.
"""

import unittest
import os
import sys
from vector_store import VectorStore


class TestVectorStore(unittest.TestCase):
    """Test cases for VectorStore class."""
    
    # Class variable to generate unique collection names
    _test_counter = 0
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_db_path = "./test_chroma_db_unit"
        self.vector_store = VectorStore(persist_directory=self.test_db_path)
        
        # Generate unique collection name for each test
        TestVectorStore._test_counter += 1
        self.collection_name = f"test_collection_{TestVectorStore._test_counter}"
        
        # Sample test data
        self.sample_chunks = [
            {
                'text': 'Diabetes management includes blood glucose monitoring and medication.',
                'metadata': {'source_filename': 'diabetes.txt', 'chunk_index': 0}
            },
            {
                'text': 'Heart disease prevention involves regular exercise and healthy diet.',
                'metadata': {'source_filename': 'heart.txt', 'chunk_index': 0}
            },
            {
                'text': 'Hypertension treatment requires lifestyle changes and antihypertensive drugs.',
                'metadata': {'source_filename': 'hypertension.txt', 'chunk_index': 0}
            }
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Note: ChromaDB may have file locks on Windows, so we don't force cleanup
        pass
    
    def test_initialize_collection(self):
        """Test collection initialization."""
        self.vector_store.initialize_collection(self.collection_name)
        self.assertIsNotNone(self.vector_store.collection)
        self.assertEqual(self.vector_store.collection.name, self.collection_name)
    
    def test_add_documents(self):
        """Test adding documents to collection."""
        self.vector_store.initialize_collection(self.collection_name)
        self.vector_store.add_documents(self.sample_chunks)
        
        # Verify documents were added
        info = self.vector_store.get_collection_info()
        self.assertEqual(info['count'], 3)
    
    def test_add_documents_without_initialization(self):
        """Test that adding documents without initialization raises error."""
        with self.assertRaises(ValueError):
            self.vector_store.add_documents(self.sample_chunks)
    
    def test_query(self):
        """Test querying for similar documents."""
        self.vector_store.initialize_collection(self.collection_name)
        self.vector_store.add_documents(self.sample_chunks)
        
        # Query for diabetes-related content
        results = self.vector_store.query("diabetes treatment", top_k=2)
        
        # Verify results
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 2)
        
        # Verify result structure
        result = results[0]
        self.assertIn('text', result)
        self.assertIn('metadata', result)
        self.assertIn('distance', result)
    
    def test_query_without_initialization(self):
        """Test that querying without initialization raises error."""
        with self.assertRaises(ValueError):
            self.vector_store.query("test query")
    
    def test_clear_collection(self):
        """Test clearing collection."""
        self.vector_store.initialize_collection(self.collection_name)
        self.vector_store.add_documents(self.sample_chunks)
        
        # Verify documents added
        info = self.vector_store.get_collection_info()
        self.assertEqual(info['count'], 3)
        
        # Clear collection
        self.vector_store.clear_collection()
        
        # Verify collection is empty
        info = self.vector_store.get_collection_info()
        self.assertEqual(info['count'], 0)
    
    def test_get_collection_info(self):
        """Test getting collection information."""
        self.vector_store.initialize_collection(self.collection_name)
        self.vector_store.add_documents(self.sample_chunks)
        
        info = self.vector_store.get_collection_info()
        
        # Verify info structure
        self.assertIn('name', info)
        self.assertIn('count', info)
        self.assertIn('metadata', info)
        
        self.assertEqual(info['name'], self.collection_name)
        self.assertEqual(info['count'], 3)
    
    def test_get_collection_info_without_initialization(self):
        """Test getting info without initialization."""
        info = self.vector_store.get_collection_info()
        self.assertIn('error', info)
    
    def test_add_empty_chunks(self):
        """Test adding empty chunks list."""
        self.vector_store.initialize_collection(self.collection_name)
        self.vector_store.add_documents([])
        
        # Should not raise error, collection should remain empty
        info = self.vector_store.get_collection_info()
        self.assertEqual(info['count'], 0)


def run_tests():
    """Run all tests."""
    print("Running VectorStore Unit Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVectorStore)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

