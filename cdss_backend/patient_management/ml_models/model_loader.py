"""
Model Loader for Clinical Decision Support System

This module loads pre-trained machine learning models for:
- Diabetes risk prediction
- Heart disease risk prediction
- Stroke risk prediction (when available)

Models are loaded once at Django app startup and stored in memory.
"""

import os
import joblib
from pathlib import Path


class ModelLoader:
    """
    Simple class to load ML models from pickle files.
    Handles missing models gracefully by returning None.
    """
    
    # Class variables to store loaded models (shared across all instances)
    diabetes_model = None
    diabetes_preprocessor = None
    heart_model = None
    heart_features = None
    stroke_model = None
    
    @classmethod
    def load_models(cls):
        """
        Load all ML models from the Models directory.
        Returns None for any models that are not found.
        
        
        Called once at Django app startup.
        """
        # Get the project root directory (go up from this file)
        # Structure: cdss_backend/patient_management/ml_models/model_loader.py
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        models_dir = project_root / 'Models'
        
        print(f"Loading ML models from: {models_dir}")
        
        # Load Diabetes Model
        try:
            diabetes_model_path = models_dir / 'diabetes_model (1).pkl'
            cls.diabetes_model = joblib.load(diabetes_model_path)
            print(f"✓ Diabetes model loaded successfully")
        except FileNotFoundError:
            print(f"✗ Diabetes model not found at {diabetes_model_path}")
            cls.diabetes_model = None
        except Exception as e:
            print(f"✗ Error loading diabetes model: {e}")
            cls.diabetes_model = None
        
        # Load Diabetes Preprocessor
        try:
            preprocessor_path = models_dir / 'preprocessor (1).pkl'
            cls.diabetes_preprocessor = joblib.load(preprocessor_path)
            print(f"✓ Diabetes preprocessor loaded successfully")
        except FileNotFoundError:
            print(f"✗ Diabetes preprocessor not found at {preprocessor_path}")
            cls.diabetes_preprocessor = None
        except Exception as e:
            print(f"✗ Error loading diabetes preprocessor: {e}")
            cls.diabetes_preprocessor = None
        
        # Load Heart Disease Model
        try:
            heart_model_path = models_dir / 'heart_model.pkl'
            cls.heart_model = joblib.load(heart_model_path)
            print(f"✓ Heart disease model loaded successfully")
        except FileNotFoundError:
            print(f"✗ Heart disease model not found at {heart_model_path}")
            cls.heart_model = None
        except Exception as e:
            print(f"✗ Error loading heart disease model: {e}")
            cls.heart_model = None
        
        # Load Heart Disease Features
        try:
            heart_features_path = models_dir / 'heart_features.pkl'
            cls.heart_features = joblib.load(heart_features_path)
            print(f"✓ Heart disease features loaded successfully")
        except FileNotFoundError:
            print(f"✗ Heart disease features not found at {heart_features_path}")
            cls.heart_features = None
        except Exception as e:
            print(f"✗ Error loading heart disease features: {e}")
            cls.heart_features = None
        
        # Load Stroke Model (gracefully handle if not available)
        try:
            stroke_model_path = models_dir / 'stroke_model.pkl'
            cls.stroke_model = joblib.load(stroke_model_path)
            print(f"✓ Stroke model loaded successfully")
        except FileNotFoundError:
            print(f"ℹ Stroke model not available yet (will be added later)")
            cls.stroke_model = None
        except Exception as e:
            print(f"✗ Error loading stroke model: {e}")
            cls.stroke_model = None
        
        # Summary
        print("\n=== Model Loading Summary ===")
        print(f"Diabetes Model: {'✓ Loaded' if cls.diabetes_model else '✗ Not Available'}")
        print(f"Diabetes Preprocessor: {'✓ Loaded' if cls.diabetes_preprocessor else '✗ Not Available'}")
        print(f"Heart Disease Model: {'✓ Loaded' if cls.heart_model else '✗ Not Available'}")
        print(f"Heart Disease Features: {'✓ Loaded' if cls.heart_features else '✗ Not Available'}")
        print(f"Stroke Model: {'✓ Loaded' if cls.stroke_model else '✗ Not Available (expected)'}")
        print("=============================\n")
    
    @classmethod
    def get_diabetes_model(cls):
        """Return the diabetes model (or None if not loaded)"""
        return cls.diabetes_model
    
    @classmethod
    def get_diabetes_preprocessor(cls):
        """Return the diabetes preprocessor (or None if not loaded)"""
        return cls.diabetes_preprocessor
    
    @classmethod
    def get_heart_model(cls):
        """Return the heart disease model (or None if not loaded)"""
        return cls.heart_model
    
    @classmethod
    def get_heart_features(cls):
        """Return the heart disease features list (or None if not loaded)"""
        return cls.heart_features
    
    @classmethod
    def get_stroke_model(cls):
        """Return the stroke model (or None if not loaded)"""
        return cls.stroke_model
    
    @classmethod
    def is_model_available(cls, disease_type):
        """
        Check if a model is available for the given disease type.
        
        Args:
            disease_type: "diabetes", "heart", or "stroke"
        
        Returns:
            True if model is loaded, False otherwise
        """
        if disease_type.lower() == "diabetes":
            return cls.diabetes_model is not None
        elif disease_type.lower() in ["heart", "heart_disease"]:
            return cls.heart_model is not None
        elif disease_type.lower() == "stroke":
            return cls.stroke_model is not None
        else:
            return False
