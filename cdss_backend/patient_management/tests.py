from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token


class AuthenticationTestCase(APITestCase):
    """Test cases for Django authentication system"""
    
    def setUp(self):
        """Create test user for authentication tests"""
        self.username = 'testdoctor'
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email='test@doctor.com'
        )
    
    def test_login_with_valid_credentials(self):
        """Test login with valid username and password"""
        response = self.client.post('/api/auth/login/', {
            'username': self.username,
            'password': self.password
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], self.username)
        
        # Verify token was created
        token_exists = Token.objects.filter(user=self.user).exists()
        self.assertTrue(token_exists)
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials returns generic error"""
        response = self.client.post('/api/auth/login/', {
            'username': self.username,
            'password': 'wrongpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertIn('Authentication failed', response.data['error'])
    
    def test_login_with_missing_credentials(self):
        """Test login with missing username or password"""
        # Missing password
        response = self.client.post('/api/auth/login/', {
            'username': self.username
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing username
        response = self.client.post('/api/auth/login/', {
            'password': self.password
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_with_valid_token(self):
        """Test logout with valid authentication token"""
        # First login to get token
        login_response = self.client.post('/api/auth/login/', {
            'username': self.username,
            'password': self.password
        }, format='json')
        
        token = login_response.data['token']
        
        # Now logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post('/api/auth/logout/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify token was deleted
        token_exists = Token.objects.filter(key=token).exists()
        self.assertFalse(token_exists)
    
    def test_logout_without_authentication(self):
        """Test logout without authentication token"""
        response = self.client.post('/api/auth/logout/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_session_management(self):
        """Test Django session is created on login"""
        response = self.client.post('/api/auth/login/', {
            'username': self.username,
            'password': self.password
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Session should be active after login
        self.assertTrue(self.client.session.session_key is not None)
    
    def test_token_authentication_for_protected_endpoint(self):
        """Test token can be used to access protected endpoints"""
        # Login to get token
        login_response = self.client.post('/api/auth/login/', {
            'username': self.username,
            'password': self.password
        }, format='json')
        
        token = login_response.data['token']
        
        # Use token to access protected endpoint (logout endpoint as example)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post('/api/auth/logout/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


from .models import Patient, MedicalHistory, LabReport
from rest_framework.test import APIClient


class PatientViewSetTestCase(TestCase):
    """Test cases for PatientViewSet CRUD operations."""
    
    def setUp(self):
        # Create a test user and authenticate
        self.user = User.objects.create_user(username='testdoctor', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_create_patient(self):
        """Test creating a new patient."""
        data = {
            'name': 'Test Patient',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'phone': '555-0100',
            'email': 'test@example.com'
        }
        response = self.client.post('/api/patients/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Patient.objects.get().name, 'Test Patient')
        
    def test_create_patient_missing_required_fields(self):
        """Test creating a patient with missing required fields."""
        data = {
            'name': 'Test Patient'
        }
        response = self.client.post('/api/patients/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date_of_birth', response.data)
        self.assertIn('gender', response.data)
        
    def test_list_patients(self):
        """Test listing all patients."""
        Patient.objects.create(
            name='Patient 1',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='555-0100',
            email='patient1@example.com'
        )
        Patient.objects.create(
            name='Patient 2',
            date_of_birth='1985-05-15',
            gender='Female',
            phone='555-0101',
            email='patient2@example.com'
        )
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_retrieve_patient(self):
        """Test retrieving a specific patient."""
        patient = Patient.objects.create(
            name='Test Patient',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='555-0100',
            email='test@example.com'
        )
        response = self.client.get(f'/api/patients/{patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Patient')
        
    def test_update_patient(self):
        """Test updating a patient."""
        patient = Patient.objects.create(
            name='Test Patient',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='555-0100',
            email='test@example.com'
        )
        data = {
            'name': 'Updated Patient',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'phone': '555-9999',
            'email': 'updated@example.com'
        }
        response = self.client.put(f'/api/patients/{patient.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient.refresh_from_db()
        self.assertEqual(patient.name, 'Updated Patient')
        self.assertEqual(patient.phone, '555-9999')
        
    def test_authentication_required(self):
        """Test that authentication is required for patient endpoints."""
        client = APIClient()  # Unauthenticated client
        response = client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MedicalHistoryViewSetTestCase(TestCase):
    """Test cases for MedicalHistoryViewSet operations."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testdoctor', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.patient = Patient.objects.create(
            name='Test Patient',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='555-0100',
            email='test@example.com'
        )
        
    def test_create_medical_history(self):
        """Test creating medical history for a patient."""
        data = {
            'patient': self.patient.id,
            'diagnoses': 'Hypertension',
            'medications': 'Lisinopril 10mg',
            'allergies': 'None',
            'notes': 'Patient doing well'
        }
        response = self.client.post('/api/medical-history/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalHistory.objects.count(), 1)
        self.assertEqual(MedicalHistory.objects.get().diagnoses, 'Hypertension')
        
    def test_list_medical_history(self):
        """Test listing all medical history records."""
        MedicalHistory.objects.create(
            patient=self.patient,
            diagnoses='Hypertension',
            medications='Lisinopril 10mg',
            allergies='None',
            notes='First visit'
        )
        MedicalHistory.objects.create(
            patient=self.patient,
            diagnoses='Hypertension, Diabetes',
            medications='Lisinopril 10mg, Metformin 500mg',
            allergies='None',
            notes='Follow-up visit'
        )
        response = self.client.get('/api/medical-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_filter_medical_history_by_patient(self):
        """Test filtering medical history by patient_id."""
        patient2 = Patient.objects.create(
            name='Patient 2',
            date_of_birth='1985-05-15',
            gender='Female',
            phone='555-0101',
            email='patient2@example.com'
        )
        MedicalHistory.objects.create(
            patient=self.patient,
            diagnoses='Hypertension',
            medications='Lisinopril 10mg',
            allergies='None',
            notes='Patient 1 history'
        )
        MedicalHistory.objects.create(
            patient=patient2,
            diagnoses='Diabetes',
            medications='Metformin 500mg',
            allergies='Penicillin',
            notes='Patient 2 history'
        )
        response = self.client.get(f'/api/medical-history/?patient_id={self.patient.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['notes'], 'Patient 1 history')
        
    def test_retrieve_medical_history(self):
        """Test retrieving a specific medical history record."""
        history = MedicalHistory.objects.create(
            patient=self.patient,
            diagnoses='Hypertension',
            medications='Lisinopril 10mg',
            allergies='None',
            notes='Test notes'
        )
        response = self.client.get(f'/api/medical-history/{history.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['diagnoses'], 'Hypertension')


class LabReportViewSetTestCase(TestCase):
    """Test cases for LabReportViewSet operations."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testdoctor', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.patient = Patient.objects.create(
            name='Test Patient',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='555-0100',
            email='test@example.com'
        )
        
    def test_create_lab_report(self):
        """Test creating a lab report for a patient."""
        data = {
            'patient': self.patient.id,
            'lab_data': {
                'glucose': 120,
                'hba1c': 6.5,
                'cholesterol': 190,
                'blood_pressure': '130/85'
            }
        }
        response = self.client.post('/api/lab-reports/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LabReport.objects.count(), 1)
        self.assertEqual(LabReport.objects.get().lab_data['glucose'], 120)
        
    def test_list_lab_reports(self):
        """Test listing all lab reports."""
        LabReport.objects.create(
            patient=self.patient,
            lab_data={'glucose': 120, 'cholesterol': 190}
        )
        LabReport.objects.create(
            patient=self.patient,
            lab_data={'glucose': 145, 'cholesterol': 210}
        )
        response = self.client.get('/api/lab-reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_filter_lab_reports_by_patient(self):
        """Test filtering lab reports by patient_id."""
        patient2 = Patient.objects.create(
            name='Patient 2',
            date_of_birth='1985-05-15',
            gender='Female',
            phone='555-0101',
            email='patient2@example.com'
        )
        LabReport.objects.create(
            patient=self.patient,
            lab_data={'glucose': 120}
        )
        LabReport.objects.create(
            patient=patient2,
            lab_data={'glucose': 145}
        )
        response = self.client.get(f'/api/lab-reports/?patient_id={self.patient.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['lab_data']['glucose'], 120)
        
    def test_retrieve_lab_report(self):
        """Test retrieving a specific lab report."""
        report = LabReport.objects.create(
            patient=self.patient,
            lab_data={'glucose': 120, 'hba1c': 6.5}
        )
        response = self.client.get(f'/api/lab-reports/{report.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['lab_data']['glucose'], 120)
        self.assertEqual(response.data['lab_data']['hba1c'], 6.5)


class ForeignKeyConstraintTestCase(TestCase):
    """Test cases for verifying Django ORM foreign key constraints."""
    
    def setUp(self):
        self.patient = Patient.objects.create(
            name='Test Patient',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='555-0100',
            email='test@example.com'
        )
    
    def test_medical_history_cascades_on_patient_deletion(self):
        """Test that medical history records are deleted when patient is deleted."""
        # Create medical history for the patient
        MedicalHistory.objects.create(
            patient=self.patient,
            diagnoses='Hypertension',
            medications='Lisinopril 10mg',
            allergies='None',
            notes='Test notes'
        )
        self.assertEqual(MedicalHistory.objects.count(), 1)
        
        # Delete the patient
        self.patient.delete()
        
        # Medical history should be deleted due to CASCADE
        self.assertEqual(MedicalHistory.objects.count(), 0)
    
    def test_lab_report_cascades_on_patient_deletion(self):
        """Test that lab reports are deleted when patient is deleted."""
        # Create lab report for the patient
        LabReport.objects.create(
            patient=self.patient,
            lab_data={'glucose': 120, 'cholesterol': 190}
        )
        self.assertEqual(LabReport.objects.count(), 1)
        
        # Delete the patient
        self.patient.delete()
        
        # Lab report should be deleted due to CASCADE
        self.assertEqual(LabReport.objects.count(), 0)
    
    def test_multiple_records_cascade_on_patient_deletion(self):
        """Test that all related records are deleted when patient is deleted."""
        # Create multiple medical history and lab report records
        MedicalHistory.objects.create(
            patient=self.patient,
            diagnoses='Hypertension',
            medications='Lisinopril 10mg',
            allergies='None',
            notes='First visit'
        )
        MedicalHistory.objects.create(
            patient=self.patient,
            diagnoses='Diabetes',
            medications='Metformin 500mg',
            allergies='None',
            notes='Second visit'
        )
        LabReport.objects.create(
            patient=self.patient,
            lab_data={'glucose': 120}
        )
        LabReport.objects.create(
            patient=self.patient,
            lab_data={'glucose': 145}
        )
        
        self.assertEqual(MedicalHistory.objects.count(), 2)
        self.assertEqual(LabReport.objects.count(), 2)
        
        # Delete the patient
        self.patient.delete()
        
        # All related records should be deleted
        self.assertEqual(MedicalHistory.objects.count(), 0)
        self.assertEqual(LabReport.objects.count(), 0)


class AutoTimestampTestCase(TestCase):
    """Test cases for verifying auto_now_add timestamps are created."""
    
    def test_patient_created_at_timestamp(self):
        """Test that Patient model auto-generates created_at timestamp."""
        from django.utils import timezone
        before_creation = timezone.now()
        
        patient = Patient.objects.create(
            name='Test Patient',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='555-0100',
            email='test@example.com'
        )
        
        after_creation = timezone.now()
        
        # Verify timestamp was created
        self.assertIsNotNone(patient.created_at)
        
        # Verify timestamp is between before and after creation
        self.assertGreaterEqual(patient.created_at, before_creation)
        self.assertLessEqual(patient.created_at, after_creation)
    
    def test_medical_history_timestamp(self):
        """Test that MedicalHistory model auto-generates timestamp."""
        from django.utils import timezone
        
        patient = Patient.objects.create(
            name='Test Patient',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='555-0100',
            email='test@example.com'
        )
        
        before_creation = timezone.now()
        
        history = MedicalHistory.objects.create(
            patient=patient,
            diagnoses='Hypertension',
            medications='Lisinopril 10mg',
            allergies='None',
            notes='Test notes'
        )
        
        after_creation = timezone.now()
        
        # Verify timestamp was created
        self.assertIsNotNone(history.timestamp)
        
        # Verify timestamp is between before and after creation
        self.assertGreaterEqual(history.timestamp, before_creation)
        self.assertLessEqual(history.timestamp, after_creation)
    
    def test_lab_report_timestamp(self):
        """Test that LabReport model auto-generates timestamp."""
        from django.utils import timezone
        
        patient = Patient.objects.create(
            name='Test Patient',
            date_of_birth='1990-01-01',
            gender='Male',
            phone='555-0100',
            email='test@example.com'
        )
        
        before_creation = timezone.now()
        
        report = LabReport.objects.create(
            patient=patient,
            lab_data={'glucose': 120, 'cholesterol': 190}
        )
        
        after_creation = timezone.now()
        
        # Verify timestamp was created
        self.assertIsNotNone(report.timestamp)
        
        # Verify timestamp is between before and after creation
        self.assertGreaterEqual(report.timestamp, before_creation)
        self.assertLessEqual(report.timestamp, after_creation)
    
    def test_timestamps_are_readonly_via_api(self):
        """Test that timestamps cannot be modified via API."""
        from django.utils import timezone
        import datetime
        
        user = User.objects.create_user(username='testdoctor', password='testpass123')
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Try to create patient with custom created_at
        custom_time = timezone.now() - datetime.timedelta(days=30)
        data = {
            'name': 'Test Patient',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'phone': '555-0100',
            'email': 'test@example.com',
            'created_at': custom_time.isoformat()
        }
        
        response = client.post('/api/patients/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that the created_at was auto-generated and not set to custom time
        patient = Patient.objects.get(id=response.data['id'])
        # The timestamp should be recent, not 30 days ago
        self.assertGreater(patient.created_at, custom_time + datetime.timedelta(days=29))


from .models import Prediction, SHAPExplanation
from unittest.mock import patch, MagicMock


class RecommendationEndpointTestCase(TestCase):
    """Test cases for the recommendation API endpoint (Task 20)."""
    
    def setUp(self):
        """Set up test data for recommendation endpoint tests."""
        self.user = User.objects.create_user(username='testdoctor', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create a test patient
        self.patient = Patient.objects.create(
            name='Test Patient for Recommendations',
            date_of_birth='1975-01-01',
            gender='Male',
            phone='555-0200',
            email='rec_test@example.com'
        )
        
        # Create lab report
        self.lab_report = LabReport.objects.create(
            patient=self.patient,
            lab_data={
                'glucose': 140,
                'hba1c': 7.0,
                'bmi': 30,
                'cholesterol': 220,
                'blood_pressure_systolic': 140,
                'blood_pressure_diastolic': 90
            }
        )
        
        # Create predictions (required for recommendations)
        self.diabetes_prediction = Prediction.objects.create(
            patient=self.patient,
            disease_type='diabetes',
            risk_score=0.85,
            risk_category='High'
        )
        
        self.heart_prediction = Prediction.objects.create(
            patient=self.patient,
            disease_type='heart_disease',
            risk_score=0.45,
            risk_category='Moderate'
        )
        
        # Create SHAP explanations
        SHAPExplanation.objects.create(
            prediction=self.diabetes_prediction,
            feature_name='glucose',
            shap_value=0.35,
            direction='increases_risk'
        )
        
        SHAPExplanation.objects.create(
            prediction=self.diabetes_prediction,
            feature_name='hba1c',
            shap_value=0.28,
            direction='increases_risk'
        )
    
    @patch('agent.clinical_agent.ClinicalAgent.invoke')
    def test_recommend_endpoint_success(self, mock_agent_invoke):
        """Test successful recommendation generation."""
        # Mock the agent's response
        mock_agent_invoke.return_value = {
            'output': (
                "**PATIENT SUMMARY:**\n"
                "Patient is a 49-year-old male with high diabetes risk.\n\n"
                "**RISK ASSESSMENT:**\n"
                "Diabetes: High risk (0.85)\n"
                "Heart Disease: Moderate risk (0.45)\n\n"
                "**CLINICAL RECOMMENDATIONS:**\n"
                "1. Start lifestyle modifications\n"
                "2. Consider Metformin\n\n"
                "**NEXT ACTIONS:**\n"
                "Schedule follow-up in 3 months\n\n"
                "**IMPORTANT DISCLAIMER:**\n"
                "These are AI-generated recommendations for clinical decision support."
            ),
            'steps': [
                {'tool': 'PatientDataTool', 'tool_input': {'patient_id': self.patient.id}, 'observation': '...'},
                {'tool': 'PredictionTool', 'tool_input': {'patient_id': self.patient.id}, 'observation': '...'},
                {'tool': 'KnowledgeTool', 'tool_input': {'query': 'diabetes management'}, 'observation': '...'},
                {'tool': 'FinalAnswerTool', 'tool_input': {'answer': '...'}, 'observation': '...'}
            ]
        }
        
        # Make the request
        response = self.client.post(f'/api/patients/{self.patient.id}/recommend/')
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('patient_id', response.data)
        self.assertIn('patient_name', response.data)
        self.assertIn('recommendation', response.data)
        self.assertIn('tools_used', response.data)
        self.assertIn('steps_count', response.data)
        self.assertIn('message', response.data)
        
        # Verify content
        self.assertEqual(response.data['patient_id'], self.patient.id)
        self.assertEqual(response.data['patient_name'], 'Test Patient for Recommendations')
        self.assertIn('disclaimer', response.data['recommendation'].lower())
        self.assertEqual(len(response.data['tools_used']), 4)
        self.assertEqual(response.data['steps_count'], 4)
        
        # Verify tools used
        self.assertIn('PatientDataTool', response.data['tools_used'])
        self.assertIn('PredictionTool', response.data['tools_used'])
        self.assertIn('KnowledgeTool', response.data['tools_used'])
        self.assertIn('FinalAnswerTool', response.data['tools_used'])
    
    def test_recommend_endpoint_patient_not_found(self):
        """Test recommendation for non-existent patient."""
        response = self.client.post('/api/patients/99999/recommend/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Patient with ID 99999 not found', response.data['error'])
    
    def test_recommend_endpoint_no_predictions(self):
        """Test recommendation for patient without predictions."""
        # Create a patient without predictions
        patient_no_pred = Patient.objects.create(
            name='Patient Without Predictions',
            date_of_birth='1980-01-01',
            gender='Female',
            phone='555-0201',
            email='nopred@example.com'
        )
        
        response = self.client.post(f'/api/patients/{patient_no_pred.id}/recommend/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('No risk predictions found', response.data['error'])
    
    @patch('agent.clinical_agent.ClinicalAgent.invoke')
    def test_recommend_endpoint_agent_error(self, mock_agent_invoke):
        """Test recommendation when agent encounters an error."""
        # Mock the agent to raise an exception
        mock_agent_invoke.side_effect = Exception('AI agent connection failed')
        
        response = self.client.post(f'/api/patients/{self.patient.id}/recommend/')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertIn('Failed to generate recommendations', response.data['error'])
    
    @patch('agent.clinical_agent.ClinicalAgent.invoke')
    def test_recommend_endpoint_adds_disclaimer(self, mock_agent_invoke):
        """Test that disclaimer is added if not present in agent response."""
        # Mock response without disclaimer
        mock_agent_invoke.return_value = {
            'output': (
                "**PATIENT SUMMARY:**\n"
                "Patient needs lifestyle changes.\n\n"
                "**RECOMMENDATIONS:**\n"
                "1. Diet\n"
                "2. Exercise"
            ),
            'steps': [
                {'tool': 'PatientDataTool', 'tool_input': {}, 'observation': '...'},
                {'tool': 'FinalAnswerTool', 'tool_input': {}, 'observation': '...'}
            ]
        }
        
        response = self.client.post(f'/api/patients/{self.patient.id}/recommend/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify disclaimer was added
        self.assertIn('disclaimer', response.data['recommendation'].lower())
        self.assertIn('AI-generated recommendations', response.data['recommendation'])
        self.assertIn('doctor retains final', response.data['recommendation'])
    
    def test_recommend_endpoint_requires_authentication(self):
        """Test that recommendation endpoint requires authentication."""
        client = APIClient()  # Unauthenticated client
        response = client.post(f'/api/patients/{self.patient.id}/recommend/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('agent.clinical_agent.ClinicalAgent.invoke')
    def test_recommend_endpoint_response_structure(self, mock_agent_invoke):
        """Test that recommendation response has correct structure."""
        mock_agent_invoke.return_value = {
            'output': 'Test recommendation with disclaimer',
            'steps': [
                {'tool': 'PatientDataTool', 'tool_input': {}, 'observation': 'data'},
                {'tool': 'PredictionTool', 'tool_input': {}, 'observation': 'pred'},
                {'tool': 'KnowledgeTool', 'tool_input': {}, 'observation': 'knowledge'},
                {'tool': 'FinalAnswerTool', 'tool_input': {}, 'observation': 'answer'}
            ]
        }
        
        response = self.client.post(f'/api/patients/{self.patient.id}/recommend/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all required fields are present
        required_fields = ['patient_id', 'patient_name', 'recommendation', 'tools_used', 'steps_count', 'message']
        for field in required_fields:
            self.assertIn(field, response.data)
        
        # Verify data types
        self.assertIsInstance(response.data['patient_id'], int)
        self.assertIsInstance(response.data['patient_name'], str)
        self.assertIsInstance(response.data['recommendation'], str)
        self.assertIsInstance(response.data['tools_used'], list)
        self.assertIsInstance(response.data['steps_count'], int)
        self.assertIsInstance(response.data['message'], str)
