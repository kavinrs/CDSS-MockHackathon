from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (PatientViewSet, MedicalHistoryViewSet, LabReportViewSet,
                    PredictionViewSet, predict_risk_view, recommend_view,
                    upload_lab_report_view)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'medical-history', MedicalHistoryViewSet, basename='medical-history')
router.register(r'lab-reports', LabReportViewSet, basename='lab-report')
router.register(r'predictions', PredictionViewSet, basename='prediction')

urlpatterns = [
    path('', include(router.urls)),
    path('patients/<int:patient_id>/predict/', predict_risk_view, name='predict-risk'),
    path('patients/<int:patient_id>/recommend/', recommend_view, name='recommend'),
    path('patients/<int:patient_id>/upload-lab-report/', upload_lab_report_view, name='upload-lab-report'),
]
