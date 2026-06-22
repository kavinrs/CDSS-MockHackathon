from django.contrib import admin
from .models import Patient, MedicalHistory, LabReport, Prediction, SHAPExplanation


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth', 'gender', 'phone', 'email', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-created_at',)


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'timestamp', 'get_diagnoses_preview')
    list_filter = ('timestamp',)
    search_fields = ('patient__name', 'diagnoses', 'medications')
    ordering = ('-timestamp',)

    def get_diagnoses_preview(self, obj):
        return obj.diagnoses[:50] + '...' if len(obj.diagnoses) > 50 else obj.diagnoses
    get_diagnoses_preview.short_description = 'Diagnoses Preview'


@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = ('patient', 'timestamp', 'get_lab_data_preview')
    list_filter = ('timestamp',)
    search_fields = ('patient__name',)
    ordering = ('-timestamp',)

    def get_lab_data_preview(self, obj):
        data_str = str(obj.lab_data)
        return data_str[:50] + '...' if len(data_str) > 50 else data_str
    get_lab_data_preview.short_description = 'Lab Data Preview'


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'disease_type', 'risk_score', 'risk_category', 'timestamp')
    list_filter = ('disease_type', 'risk_category', 'timestamp')
    search_fields = ('patient__name', 'disease_type')
    ordering = ('-timestamp',)


@admin.register(SHAPExplanation)
class SHAPExplanationAdmin(admin.ModelAdmin):
    list_display = ('prediction', 'feature_name', 'shap_value', 'direction')
    list_filter = ('direction', 'prediction__disease_type')
    search_fields = ('feature_name', 'prediction__patient__name')
    ordering = ('-shap_value',)
