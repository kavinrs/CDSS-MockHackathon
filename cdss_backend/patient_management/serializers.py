from rest_framework import serializers
from .models import Patient, MedicalHistory, LabReport, Prediction, SHAPExplanation


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient model with all fields.
    """
    class Meta:
        model = Patient
        fields = ['id', 'name', 'date_of_birth', 'gender', 'phone', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']


class MedicalHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for MedicalHistory model with patient foreign key.
    """
    class Meta:
        model = MedicalHistory
        fields = ['id', 'patient', 'diagnoses', 'medications', 'allergies', 'notes', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class LabReportSerializer(serializers.ModelSerializer):
    """
    Serializer for LabReport model with patient foreign key.
    """
    class Meta:
        model = LabReport
        fields = ['id', 'patient', 'lab_data', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class SHAPExplanationSerializer(serializers.ModelSerializer):
    """
    Serializer for SHAP explanation with feature importance details.
    """
    class Meta:
        model = SHAPExplanation
        fields = ['id', 'feature_name', 'shap_value', 'direction']
        read_only_fields = ['id']


class PredictionSerializer(serializers.ModelSerializer):
    """
    Serializer for Prediction model with nested SHAP explanations.
    """
    shap_explanations = SHAPExplanationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Prediction
        fields = ['id', 'patient', 'disease_type', 'risk_score', 'risk_category', 
                  'timestamp', 'shap_explanations']
        read_only_fields = ['id', 'timestamp']
