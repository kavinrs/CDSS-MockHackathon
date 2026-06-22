from django.apps import AppConfig


class PatientManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patient_management'
    
    def ready(self):
        """
        Load ML models once at Django app startup.
        This ensures models are loaded into memory and ready for predictions.
        """
        from .ml_models.model_loader import ModelLoader
        
        # Load all models at startup
        ModelLoader.load_models()
