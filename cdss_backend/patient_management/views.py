from django.contrib.auth import authenticate, login, logout
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Patient, MedicalHistory, LabReport, Prediction, SHAPExplanation
from .serializers import (PatientSerializer, MedicalHistorySerializer, LabReportSerializer,
                          PredictionSerializer, SHAPExplanationSerializer)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Doctor registration endpoint.
    Creates a new user account for doctors.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    # Validation
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(password) < 6:
        return Response(
            {'error': 'Password must be at least 6 characters long'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if username already exists
    from django.contrib.auth.models import User
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if email already exists (if provided)
    if email and User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already registered'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Registration successful',
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Registration failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Doctor login endpoint using Django authentication.
    Accepts username and password, returns authentication token.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Use Django's built-in authenticate()
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        # Authentication successful
        login(request, user)
        
        # Get or create token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_200_OK)
    else:
        # Authentication failed - generic error message
        return Response(
            {'error': 'Authentication failed. Please check your username and password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Doctor logout endpoint.
    Requires authentication token.
    """
    try:
        # Delete the user's token to logout
        request.user.auth_token.delete()
        logout(request)
        return Response(
            {'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': 'Logout failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Patient model with all CRUD operations.
    Supports: list, create, retrieve, update, partial_update, destroy
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MedicalHistory model.
    Supports: list, create, retrieve operations
    """
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally filter medical history by patient_id query parameter.
        """
        queryset = MedicalHistory.objects.all()
        patient_id = self.request.query_params.get('patient_id', None)
        if patient_id is not None:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


class LabReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LabReport model.
    Supports: list, create, retrieve operations
    """
    queryset = LabReport.objects.all()
    serializer_class = LabReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally filter lab reports by patient_id query parameter.
        """
        queryset = LabReport.objects.all()
        patient_id = self.request.query_params.get('patient_id', None)
        if patient_id is not None:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_risk_view(request, patient_id):
    """
    Generate risk predictions for a patient based on their latest lab report.
    
    Endpoint: POST /api/patients/{patient_id}/predict/
    
    Returns risk predictions and SHAP explanations for:
    - Diabetes (if model available)
    - Heart Disease (if model available)
    - Stroke (if model available)
    
    Predictions and SHAP explanations are saved to the database.
    """
    from .models import Prediction, SHAPExplanation
    from .ml_models import RiskPredictor, SHAPExplainer, ModelLoader
    
    # Check if patient exists
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response(
            {'error': f'Patient with ID {patient_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get latest lab report for the patient
    try:
        lab_report = LabReport.objects.filter(patient=patient).latest('timestamp')
    except LabReport.DoesNotExist:
        return Response(
            {'error': 'No lab reports found for this patient. Please add lab data first.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Initialize predictor and explainer
    predictor = RiskPredictor()
    explainer = SHAPExplainer()
    
    # Get predictions for all available models
    predictions_data = predictor.predict_risk(lab_report.lab_data)
    
    # Store results for response
    results = []
    highest_risk = None
    highest_risk_score = 0
    
    # Process each disease prediction
    for disease_type, prediction_result in predictions_data.items():
        if prediction_result is None:
            continue
        
        # Save Prediction to database
        prediction = Prediction.objects.create(
            patient=patient,
            disease_type=disease_type,
            risk_score=prediction_result['risk_score'],
            risk_category=prediction_result['risk_category']
        )
        
        # Generate SHAP explanations
        shap_explanations = []
        
        if disease_type == 'diabetes' and ModelLoader.is_model_available('diabetes'):
            # Use rule-based explanations for diabetes (more transparent and reliable)
            from patient_management.ml_models.rule_based_predictor import predict_diabetes_risk_rules
            rule_result = predict_diabetes_risk_rules(lab_report.lab_data)
            
            # Convert rule-based factors to SHAP-like format for consistency
            for factor in rule_result.get('risk_factors', []):
                shap_explanations.append({
                    'feature_name': factor['factor'],
                    'shap_value': factor['contribution'],
                    'direction': 'increases_risk' if factor['contribution'] > 0 else 'decreases_risk'
                })
        
        elif disease_type == 'heart_disease' and ModelLoader.is_model_available('heart'):
            # Use ML model with SHAP for heart disease
            features = predictor._extract_heart_features(lab_report.lab_data, ModelLoader.get_heart_features())
            feature_names = ModelLoader.get_heart_features()
            if feature_names is None:
                feature_names = ['age', 'cholesterol', 'blood_pressure_systolic', 
                               'blood_pressure_diastolic', 'heart_rate']
            shap_results = explainer.explain_heart_disease_prediction(features, feature_names)
            shap_explanations = shap_results
        
        elif disease_type == 'stroke' and ModelLoader.is_model_available('stroke'):
            # Get the features used for prediction
            features = predictor._extract_stroke_features(lab_report.lab_data)
            feature_names = ['age', 'blood_pressure_systolic', 'blood_pressure_diastolic',
                            'cholesterol', 'glucose']
            shap_results = explainer.explain_stroke_prediction(features, feature_names)
            shap_explanations = shap_results
        
        # Save SHAP explanations to database
        for shap_exp in shap_explanations:
            SHAPExplanation.objects.create(
                prediction=prediction,
                feature_name=shap_exp['feature_name'],
                shap_value=shap_exp['shap_value'],
                direction=shap_exp['direction']
            )
        
        # Build response for this disease
        result_data = {
            'disease_type': disease_type,
            'available': True,
            'risk_score': prediction_result['risk_score'],
            'risk_category': prediction_result['risk_category'],
            'prediction_id': prediction.id,
            'shap_explanations': shap_explanations[:10],  # Top 10 features
            'timestamp': prediction.timestamp
        }
        results.append(result_data)
        
        # Track highest risk
        if prediction_result['risk_score'] > highest_risk_score:
            highest_risk_score = prediction_result['risk_score']
            highest_risk = result_data
    
    # Extract PDF filename if available
    pdf_filename = None
    if lab_report.pdf_file_path:
        import os
        pdf_filename = os.path.basename(lab_report.pdf_file_path)
    
    return Response({
        'patient_id': patient_id,
        'patient_name': patient.name,
        'lab_report_id': lab_report.id,
        'lab_report_date': lab_report.timestamp,
        'pdf_filename': pdf_filename,
        'pdf_upload_timestamp': lab_report.pdf_upload_timestamp,
        'all_predictions': results,
        'highest_risk': highest_risk,
        'message': 'Risk predictions generated successfully'
    }, status=status.HTTP_200_OK)


class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing Prediction records.
    Read-only: Predictions are created via predict_risk_view endpoint.
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally filter predictions by patient_id query parameter.
        """
        queryset = Prediction.objects.all()
        patient_id = self.request.query_params.get('patient_id', None)
        if patient_id is not None:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_view(request, patient_id):
    """
    Generate AI clinical recommendations for a patient using the ClinicalAgent.
    
    Endpoint: POST /api/patients/{patient_id}/recommend/
    
    The AI agent automatically:
    1. Retrieves patient data from the database
    2. Retrieves risk predictions and SHAP explanations
    3. Queries medical guidelines from RAG system
    4. Generates comprehensive clinical recommendations
    
    Returns AI-generated recommendations with mandatory disclaimer.
    """
    from agent.clinical_agent import ClinicalAgent
    
    # Check if patient exists
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response(
            {'error': f'Patient with ID {patient_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if patient has predictions
    predictions_exist = Prediction.objects.filter(patient=patient).exists()
    if not predictions_exist:
        return Response(
            {'error': 'No risk predictions found for this patient. Please run predictions first.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Initialize the clinical AI agent
        agent = ClinicalAgent(max_iterations=10)
        
        # Generate query for the agent
        query = f"Provide clinical recommendations for patient {patient_id}"
        
        # Invoke the agent
        result = agent.invoke(query)
        
        # Extract recommendation and steps
        recommendation = result['output']
        steps = result['steps']
        
        # Add disclaimer if not present
        disclaimer = (
            "\n\n**IMPORTANT DISCLAIMER:**\n"
            "These are AI-generated recommendations for clinical decision support. "
            "The doctor retains final clinical decision-making authority. "
            "Always verify recommendations with current medical guidelines and clinical judgment."
        )
        
        if 'disclaimer' not in recommendation.lower():
            recommendation += disclaimer
        
        return Response({
            'patient_id': patient_id,
            'patient_name': patient.name,
            'recommendation': recommendation,
            'tools_used': [step['tool'] for step in steps],
            'steps_count': len(steps),
            'message': 'Clinical recommendations generated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Recommendation failed for patient {patient_id}:")
        print(error_details)
        return Response(
            {'error': f'Failed to generate recommendations: {str(e)}', 'details': error_details},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_lab_report_view(request, patient_id):
    """
    Upload a PDF laboratory report and extract values.
    
    Endpoint: POST /api/patients/{patient_id}/upload-lab-report/
    
    This view handles:
    1. File validation (type, size)
    2. PDF storage
    3. Text extraction
    4. Value parsing
    5. Return extracted data
    
    Returns extracted values for doctor verification (no auto-save).
    """
    from .pdf_processor import extract_text_from_pdf, PDFProcessingError
    from .value_extractor import extract_all_values
    from .storage_manager import LabReportStorageManager
    
    # Step 1: Check if patient exists
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response(
            {'error': 'Patient not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Step 2: Get uploaded file
    pdf_file = request.FILES.get('pdf_file')
    if not pdf_file:
        return Response(
            {'error': 'No file uploaded'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Step 3: Validate file type
    if not pdf_file.name.endswith('.pdf'):
        return Response(
            {'error': 'Invalid file format. Please upload a PDF file'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Step 4: Validate file size (10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if pdf_file.size > max_size:
        return Response(
            {'error': 'File too large. Maximum size is 10MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Step 5: Save PDF file to storage
    try:
        pdf_file_path = LabReportStorageManager.save_pdf_file(pdf_file, patient_id)
        full_path = LabReportStorageManager.get_full_path(pdf_file_path)
    except Exception as e:
        return Response(
            {'error': f'Failed to save PDF file: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Step 6: Extract text from PDF
    try:
        text = extract_text_from_pdf(full_path)
    except PDFProcessingError as e:
        return Response(
            {'error': f'Failed to extract text from PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': f'Unexpected error during PDF processing: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Step 7: If no text found, return empty result
    if not text or len(text.strip()) == 0:
        return Response({
            'message': 'No text found in PDF. Please enter values manually',
            'extracted_values': {},
            'pdf_file_path': pdf_file_path,
            'extraction_success_rate': 0.0
        }, status=status.HTTP_200_OK)
    
    # Step 8: Extract laboratory values from text
    extracted_values = extract_all_values(text)
    
    # Step 8.5: Log extracted text for debugging (first 500 chars)
    print(f"[PDF DEBUG] Extracted text preview: {text[:500]}")
    print(f"[PDF DEBUG] Extracted values: {extracted_values}")
    
    # Step 9: Calculate extraction success rate
    total_values = len(extracted_values)
    extracted_count = sum(1 for v in extracted_values.values() if v is not None)
    success_rate = extracted_count / total_values if total_values > 0 else 0.0
    
    # Step 10: Return results to frontend
    return Response({
        'message': f'Extracted {extracted_count} of {total_values} values',
        'extracted_values': extracted_values,
        'pdf_file_path': pdf_file_path,
        'extraction_success_rate': success_rate
    }, status=status.HTTP_200_OK)
