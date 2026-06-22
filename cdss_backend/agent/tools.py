"""
Clinical Decision Support Tools for AI Agent.
Simple tools using @tool decorator for easy understanding.
"""

import json
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cdss_backend.settings')
django.setup()

from langchain_core.tools import tool
from patient_management.models import Patient, MedicalHistory, LabReport, Prediction, SHAPExplanation
from rag.vector_store import VectorStore
from rag.rag_retriever import RAGRetriever


@tool
def PatientDataTool(patient_id: int) -> str:
    """
    Get patient demographics, medical history, and lab reports.
    
    Use this tool to retrieve complete patient information including:
    - Demographics (name, age, gender, contact)
    - Medical history (diagnoses, medications, allergies)
    - Lab reports (recent test results)
    
    Args:
        patient_id: The patient's ID number
        
    Returns:
        JSON string with patient data or error message
    """
    try:
        # Get patient
        patient = Patient.objects.get(id=patient_id)
        
        # Calculate age from date of birth
        from datetime import date
        today = date.today()
        age = today.year - patient.date_of_birth.year - (
            (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
        )
        
        # Get medical history
        medical_histories = MedicalHistory.objects.filter(patient=patient).order_by('-timestamp')
        history_data = []
        for history in medical_histories[:3]:  # Last 3 entries
            history_data.append({
                'date': history.timestamp.strftime('%Y-%m-%d'),
                'diagnoses': history.diagnoses,
                'medications': history.medications,
                'allergies': history.allergies,
                'notes': history.notes
            })
        
        # Get lab reports
        lab_reports = LabReport.objects.filter(patient=patient).order_by('-timestamp')
        lab_data = []
        for lab in lab_reports[:3]:  # Last 3 entries
            lab_data.append({
                'date': lab.timestamp.strftime('%Y-%m-%d'),
                'lab_values': lab.lab_data
            })
        
        # Build response
        patient_data = {
            'patient_id': patient.id,
            'name': patient.name,
            'age': age,
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'gender': patient.gender,
            'phone': patient.phone,
            'email': patient.email,
            'medical_history': history_data,
            'lab_reports': lab_data
        }
        
        return json.dumps(patient_data, indent=2)
        
    except Patient.DoesNotExist:
        return json.dumps({'error': f'Patient with ID {patient_id} not found'})
    except Exception as e:
        return json.dumps({'error': f'Failed to retrieve patient data: {str(e)}'})


@tool
def PredictionTool(patient_id: int) -> str:
    """
    Get latest risk predictions and SHAP explanations for a patient.
    
    Use this tool to retrieve:
    - Disease risk scores (Diabetes, Heart Disease, Stroke)
    - Risk categories (Low, Moderate, High)
    - SHAP feature importance explanations
    
    Args:
        patient_id: The patient's ID number
        
    Returns:
        JSON string with predictions and explanations or error message
    """
    try:
        # Get patient
        patient = Patient.objects.get(id=patient_id)
        
        # Get latest predictions for each disease
        predictions = Prediction.objects.filter(patient=patient).order_by('-timestamp')
        
        if not predictions.exists():
            return json.dumps({
                'error': 'No predictions found for this patient',
                'message': 'Please run risk prediction first'
            })
        
        # Group predictions by disease (get most recent for each)
        disease_predictions = {}
        for pred in predictions:
            if pred.disease_type not in disease_predictions:
                # Get SHAP explanations for this prediction
                shap_explanations = SHAPExplanation.objects.filter(prediction=pred)
                
                shap_data = []
                for shap in shap_explanations[:10]:  # Top 10 features
                    shap_data.append({
                        'feature': shap.feature_name,
                        'shap_value': round(shap.shap_value, 4),
                        'direction': shap.direction
                    })
                
                disease_predictions[pred.disease_type] = {
                    'risk_score': round(pred.risk_score, 4),
                    'risk_category': pred.risk_category,
                    'date': pred.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'shap_explanations': shap_data
                }
        
        prediction_data = {
            'patient_id': patient.id,
            'patient_name': patient.name,
            'predictions': disease_predictions
        }
        
        return json.dumps(prediction_data, indent=2)
        
    except Patient.DoesNotExist:
        return json.dumps({'error': f'Patient with ID {patient_id} not found'})
    except Exception as e:
        return json.dumps({'error': f'Failed to retrieve predictions: {str(e)}'})


@tool
def KnowledgeTool(query: str) -> str:
    """
    Search medical guidelines for relevant clinical information.
    
    Use this tool to retrieve evidence-based medical guidelines for:
    - Disease management protocols
    - Treatment recommendations
    - Clinical best practices
    
    Args:
        query: Clinical question or topic (e.g., "diabetes management", "hypertension treatment")
        
    Returns:
        JSON string with top 5 relevant guideline excerpts and sources
    """
    try:
        # Initialize RAG system
        vector_store = VectorStore(persist_directory="./chroma_db")
        vector_store.initialize_collection("medical_guidelines")
        retriever = RAGRetriever(vector_store)
        
        # Retrieve relevant guidelines
        results = retriever.retrieve(query, top_k=5)
        
        if not results:
            return json.dumps({
                'query': query,
                'guidelines': [],
                'message': 'No relevant guidelines found for this query'
            })
        
        # Format guidelines
        guidelines = []
        for i, result in enumerate(results, 1):
            guidelines.append({
                'rank': i,
                'source': result['source_filename'].replace('.txt', '').replace('_', ' ').title(),
                'text': result['text'],
                'relevance': round(1.0 / (1.0 + result['distance']), 4)
            })
        
        knowledge_data = {
            'query': query,
            'guidelines_found': len(guidelines),
            'guidelines': guidelines
        }
        
        return json.dumps(knowledge_data, indent=2)
        
    except Exception as e:
        return json.dumps({'error': f'Failed to retrieve guidelines: {str(e)}'})


@tool
def FinalAnswerTool(answer: str) -> str:
    """
    Return the final clinical recommendation to the doctor.
    
    Use this tool ONLY after gathering all necessary information from other tools.
    Provide comprehensive clinical recommendations including:
    - Patient summary
    - Risk assessment
    - Evidence-based recommendations
    - Suggested next actions
    - Disclaimer
    
    Args:
        answer: Complete clinical recommendation text
        
    Returns:
        The final answer text
    """
    return answer


# List of all tools for the agent
ALL_TOOLS = [
    PatientDataTool,
    PredictionTool,
    KnowledgeTool,
    FinalAnswerTool
]
