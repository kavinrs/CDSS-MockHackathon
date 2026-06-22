"""
Unit tests for ML Model Loading
Tests that models load correctly at startup and are accessible
"""
from django.test import TestCase
from .model_loader import ModelLoader


class ModelLoaderTests(TestCase):
    """Test cases for the ModelLoader class"""
    
    def test_models_are_loaded_at_startup(self):
        """Test that models are loaded and accessible"""
        # Models should be loaded by apps.py ready() method
        diabetes_model = ModelLoader.get_diabetes_model()
        heart_model = ModelLoader.get_heart_model()
        heart_features = ModelLoader.get_heart_features()
        stroke_model = ModelLoader.get_stroke_model()
        
        # Diabetes model should be loaded
        self.assertIsNotNone(diabetes_model, "Diabetes model should be loaded")
        
        # Heart disease model should be loaded
        self.assertIsNotNone(heart_model, "Heart disease model should be loaded")
        
        # Heart features should be loaded
        self.assertIsNotNone(heart_features, "Heart features should be loaded")
        self.assertIsInstance(heart_features, list, "Heart features should be a list")
        self.assertGreater(len(heart_features), 0, "Heart features should not be empty")
        
        # Stroke model may be None (graceful handling)
        # This is expected and acceptable
        if stroke_model is None:
            print("Note: Stroke model is None (expected - user will add later)")
    
    def test_diabetes_model_type(self):
        """Test that diabetes model is correct type"""
        diabetes_model = ModelLoader.get_diabetes_model()
        if diabetes_model is not None:
            # Should be an XGBoost classifier
            self.assertTrue(
                hasattr(diabetes_model, 'predict_proba'),
                "Diabetes model should have predict_proba method"
            )
    
    def test_heart_model_type(self):
        """Test that heart disease model is correct type"""
        heart_model = ModelLoader.get_heart_model()
        if heart_model is not None:
            # Should be an XGBoost classifier
            self.assertTrue(
                hasattr(heart_model, 'predict_proba'),
                "Heart model should have predict_proba method"
            )
    
    def test_graceful_handling_of_missing_stroke_model(self):
        """Test that missing stroke model returns None gracefully"""
        stroke_model = ModelLoader.get_stroke_model()
        # Should be None or a valid model - both are acceptable
        # No exception should be raised
        self.assertTrue(
            stroke_model is None or hasattr(stroke_model, 'predict_proba'),
            "Stroke model should be None or a valid model"
        )
    
    def test_models_stored_as_class_variables(self):
        """Test that models are stored as class variables for reuse"""
        # Check that class variables exist
        self.assertTrue(hasattr(ModelLoader, 'diabetes_model'))
        self.assertTrue(hasattr(ModelLoader, 'heart_model'))
        self.assertTrue(hasattr(ModelLoader, 'heart_features'))
        self.assertTrue(hasattr(ModelLoader, 'stroke_model'))
        
        # Check that getter methods return class variables
        self.assertEqual(ModelLoader.get_diabetes_model(), ModelLoader.diabetes_model)
        self.assertEqual(ModelLoader.get_heart_model(), ModelLoader.heart_model)
        self.assertEqual(ModelLoader.get_heart_features(), ModelLoader.heart_features)
        self.assertEqual(ModelLoader.get_stroke_model(), ModelLoader.stroke_model)
