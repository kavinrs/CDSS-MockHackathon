"""
SHAP Explanation Generator for Clinical Decision Support System

This module generates SHAP (SHapley Additive exPlanations) values
to explain ML model predictions. SHAP values show which features
contribute most to the prediction and in which direction.
"""

import shap
import numpy as np
from .model_loader import ModelLoader


class SHAPExplainer:
    """
    Simple SHAP explanation generator for tree-based models.
    Uses TreeExplainer for XGBoost models.
    """
    
    def __init__(self):
        """Initialize the SHAP explainer."""
        pass
    
    def explain_prediction(self, model, features, feature_names=None):
        """
        Generate SHAP explanations for a prediction.
        
        Args:
            model: Loaded ML model (XGBoost)
            features: numpy array of feature values used for prediction
            feature_names: list of feature names (optional)
        
        Returns:
            list of dicts: [
                {
                    'feature_name': 'glucose',
                    'shap_value': 0.15,
                    'direction': 'increases_risk'
                },
                ...
            ]
            Sorted by absolute SHAP value (descending)
        """
        if model is None:
            return []
        
        try:
            # Create TreeExplainer for XGBoost models
            explainer = shap.TreeExplainer(model)
            
            # Calculate SHAP values
            shap_values = explainer.shap_values(features)
            
            # If shap_values is a list (for multi-class), take the positive class
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # Class 1 (has disease)
            
            # Get SHAP values for the single prediction (first row)
            if len(shap_values.shape) > 1:
                shap_values_single = shap_values[0]
            else:
                shap_values_single = shap_values
            
            # Create feature names if not provided
            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(len(shap_values_single))]
            
            # Build explanation list
            explanations = []
            for i, (feature_name, shap_value) in enumerate(zip(feature_names, shap_values_single)):
                # Determine direction
                direction = "increases_risk" if shap_value > 0 else "decreases_risk"
                
                explanations.append({
                    'feature_name': feature_name,
                    'shap_value': float(shap_value),
                    'direction': direction
                })
            
            # Sort by absolute SHAP value (descending)
            explanations.sort(key=lambda x: abs(x['shap_value']), reverse=True)
            
            # Return top 10 most important features
            return explanations[:10]
        
        except Exception as e:
            print(f"Error generating SHAP explanation: {e}")
            return []
    
    def explain_diabetes_prediction(self, features, feature_names=None):
        """
        Generate SHAP explanation for diabetes prediction.
        
        Args:
            features: numpy array of features used for prediction
            feature_names: list of feature names
        
        Returns:
            list of SHAP explanations
        """
        model = ModelLoader.get_diabetes_model()
        
        if feature_names is None:
            # Default diabetes feature names
            feature_names = ['glucose', 'hba1c', 'bmi', 'age']
        
        return self.explain_prediction(model, features, feature_names)
    
    def explain_heart_disease_prediction(self, features, feature_names=None):
        """
        Generate SHAP explanation for heart disease prediction.
        
        Args:
            features: numpy array of features used for prediction
            feature_names: list of feature names (from heart_features.pkl)
        
        Returns:
            list of SHAP explanations
        """
        model = ModelLoader.get_heart_model()
        
        if feature_names is None:
            # Try to get feature names from loaded heart_features
            heart_features = ModelLoader.get_heart_features()
            if heart_features is not None:
                feature_names = heart_features
            else:
                # Default heart disease feature names
                feature_names = ['age', 'cholesterol', 'blood_pressure_systolic', 
                                'blood_pressure_diastolic', 'heart_rate']
        
        return self.explain_prediction(model, features, feature_names)
    
    def explain_stroke_prediction(self, features, feature_names=None):
        """
        Generate SHAP explanation for stroke prediction.
        (Placeholder for when stroke model is available)
        
        Args:
            features: numpy array of features used for prediction
            feature_names: list of feature names
        
        Returns:
            list of SHAP explanations
        """
        model = ModelLoader.get_stroke_model()
        
        if feature_names is None:
            # Default stroke feature names
            feature_names = ['age', 'blood_pressure_systolic', 'blood_pressure_diastolic',
                            'cholesterol', 'glucose']
        
        return self.explain_prediction(model, features, feature_names)
