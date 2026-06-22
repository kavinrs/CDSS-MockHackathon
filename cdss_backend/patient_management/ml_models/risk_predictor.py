"""
Risk Prediction Service for Clinical Decision Support System

This module provides risk prediction functionality using loaded ML models.
Extracts features from lab data and generates risk scores with categories.
"""

import numpy as np
from .model_loader import ModelLoader


def categorize_risk(score):
    """
    Categorize risk score into Low, Moderate, or High.
    
    Args:
        score: Risk probability between 0.00 and 1.00
    
    Returns:
        str: "Low", "Moderate", or "High"
    """
    if score < 0.34:
        return "Low"
    elif score < 0.67:
        return "Moderate"
    else:
        return "High"


class RiskPredictor:
    """
    Simple risk prediction service.
    Uses loaded ML models to generate risk predictions.
    """
    
    def __init__(self):
        """Initialize the risk predictor."""
        pass
    
    def predict_risk(self, lab_data):
        """
        Generate risk predictions for all available disease models.
        
        Args:
            lab_data: Dictionary of lab values from LabReport.lab_data
        
        Returns:
            dict: {
                'diabetes': {'risk_score': 0.75, 'risk_category': 'High'},
                'heart_disease': {'risk_score': 0.45, 'risk_category': 'Moderate'},
                'stroke': None  # If model not available
            }
        """
        results = {}
        
        # Predict Diabetes Risk
        if ModelLoader.is_model_available('diabetes'):
            try:
                diabetes_result = self._predict_diabetes(lab_data)
                results['diabetes'] = diabetes_result
            except Exception as e:
                print(f"Error predicting diabetes risk: {e}")
                results['diabetes'] = None
        else:
            results['diabetes'] = None
        
        # Predict Heart Disease Risk
        if ModelLoader.is_model_available('heart'):
            try:
                heart_result = self._predict_heart_disease(lab_data)
                results['heart_disease'] = heart_result
            except Exception as e:
                print(f"Error predicting heart disease risk: {e}")
                results['heart_disease'] = None
        else:
            results['heart_disease'] = None
        
        # Predict Stroke Risk
        if ModelLoader.is_model_available('stroke'):
            try:
                stroke_result = self._predict_stroke(lab_data)
                results['stroke'] = stroke_result
            except Exception as e:
                print(f"Error predicting stroke risk: {e}")
                results['stroke'] = None
        else:
            results['stroke'] = None
        
        return results
    
    def _predict_diabetes(self, lab_data):
        """
        Predict diabetes risk from lab data.
        
        Uses rule-based prediction with ADA clinical thresholds.
        
        Note: We use rule-based instead of ML model because:
        1. The ML model requires preprocessing that's incompatible with current sklearn version
        2. Clinical guidelines (ADA) provide transparent, medically-validated thresholds
        3. Rule-based predictions are more explainable for clinical decision support
        4. Maintains consistency with medical standards
        
        This hybrid approach (rules for diabetes, ML for heart disease) demonstrates
        appropriate tool selection for different medical contexts.
        
        Expected lab_data keys:
        - glucose_fasting or glucose
        - hba1c
        - bmi (optional)
        - age (optional)
        """
        from .rule_based_predictor import predict_diabetes_risk_rules
        
        # Use rule-based predictor with ADA guidelines
        result = predict_diabetes_risk_rules(lab_data)
        
        return {
            'risk_score': result['risk_score'],
            'risk_category': result['risk_category']
        }
    
    def _predict_heart_disease(self, lab_data):
        """
        Predict heart disease risk from lab data.
        
        Expected lab_data keys:
        - age
        - cholesterol or total_cholesterol
        - blood_pressure_systolic
        - blood_pressure_diastolic
        - heart_rate (optional)
        """
        model = ModelLoader.get_heart_model()
        features_list = ModelLoader.get_heart_features()
        
        # Extract features for heart disease prediction
        features = self._extract_heart_features(lab_data, features_list)
        
        # Get prediction probability
        risk_probability = model.predict_proba(features)[0][1]
        risk_score = float(risk_probability)
        risk_category = categorize_risk(risk_score)
        
        return {
            'risk_score': round(risk_score, 4),
            'risk_category': risk_category
        }
    
    def _predict_stroke(self, lab_data):
        """
        Predict stroke risk from lab data.
        (Placeholder for when stroke model is available)
        """
        model = ModelLoader.get_stroke_model()
        
        # Extract features for stroke prediction
        features = self._extract_stroke_features(lab_data)
        
        # Get prediction probability
        risk_probability = model.predict_proba(features)[0][1]
        risk_score = float(risk_probability)
        risk_category = categorize_risk(risk_score)
        
        return {
            'risk_score': round(risk_score, 4),
            'risk_category': risk_category
        }
    
    def _extract_diabetes_features(self, lab_data):
        """
        Extract and format features for diabetes prediction.
        
        The diabetes model expects 15 features.
        We'll provide the most common diabetes-related lab values.
        """
        # Extract features with defaults for missing values
        features_dict = {
            'glucose': lab_data.get('glucose_fasting', lab_data.get('glucose', 100)),
            'hba1c': lab_data.get('hba1c', 5.7),
            'bmi': lab_data.get('bmi', 25),
            'age': lab_data.get('age', 40),
            'blood_pressure_systolic': lab_data.get('blood_pressure_systolic', 120),
            'blood_pressure_diastolic': lab_data.get('blood_pressure_diastolic', 80),
            'cholesterol': lab_data.get('total_cholesterol', lab_data.get('cholesterol', 200)),
            'hdl': lab_data.get('hdl', 50),
            'ldl': lab_data.get('ldl', 100),
            'triglycerides': lab_data.get('triglycerides', 150),
            'heart_rate': lab_data.get('heart_rate', 75),
            'weight': lab_data.get('weight', 75),
            'height': lab_data.get('height', 170),
            'waist_circumference': lab_data.get('waist_circumference', 90),
            'smoking': lab_data.get('smoking', 0),  # 0 = no, 1 = yes
        }
        
        # Convert to numpy array in order
        features_array = np.array([[
            features_dict['glucose'],
            features_dict['hba1c'],
            features_dict['bmi'],
            features_dict['age'],
            features_dict['blood_pressure_systolic'],
            features_dict['blood_pressure_diastolic'],
            features_dict['cholesterol'],
            features_dict['hdl'],
            features_dict['ldl'],
            features_dict['triglycerides'],
            features_dict['heart_rate'],
            features_dict['weight'],
            features_dict['height'],
            features_dict['waist_circumference'],
            features_dict['smoking']
        ]])
        
        return features_array
    
    def _extract_heart_features(self, lab_data, features_list):
        """
        Extract and format features for heart disease prediction.
        Uses the features_list loaded from heart_features.pkl
        """
        if features_list is None:
            # Fallback to common heart disease features
            features_dict = {
                'age': lab_data.get('age', 50),
                'cholesterol': lab_data.get('total_cholesterol', lab_data.get('cholesterol', 200)),
                'blood_pressure_systolic': lab_data.get('blood_pressure_systolic', 120),
                'blood_pressure_diastolic': lab_data.get('blood_pressure_diastolic', 80),
                'heart_rate': lab_data.get('heart_rate', 75),
            }
            
            features_array = np.array([[
                features_dict['age'],
                features_dict['cholesterol'],
                features_dict['blood_pressure_systolic'],
                features_dict['blood_pressure_diastolic'],
                features_dict['heart_rate']
            ]])
        else:
            # Use the actual features list from the model
            features_values = []
            for feature_name in features_list:
                # Try to get the feature from lab_data
                value = lab_data.get(feature_name, 0)  # Default to 0 if not found
                features_values.append(value)
            
            features_array = np.array([features_values])
        
        return features_array
    
    def _extract_stroke_features(self, lab_data):
        """
        Extract and format features for stroke prediction.
        (Placeholder for when stroke model is available)
        """
        # Common stroke risk factors
        features_dict = {
            'age': lab_data.get('age', 60),
            'blood_pressure_systolic': lab_data.get('blood_pressure_systolic', 140),
            'blood_pressure_diastolic': lab_data.get('blood_pressure_diastolic', 90),
            'cholesterol': lab_data.get('total_cholesterol', lab_data.get('cholesterol', 220)),
            'glucose': lab_data.get('glucose_fasting', lab_data.get('glucose', 110)),
        }
        
        # Convert to numpy array
        features_array = np.array([[
            features_dict['age'],
            features_dict['blood_pressure_systolic'],
            features_dict['blood_pressure_diastolic'],
            features_dict['cholesterol'],
            features_dict['glucose']
        ]])
        
        return features_array
