from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (DOB: {self.date_of_birth})"

    class Meta:
        ordering = ['-created_at']


class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnoses = models.TextField()
    medications = models.TextField()
    allergies = models.TextField()
    notes = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medical History for {self.patient.name} - {self.timestamp.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Medical Histories"


class LabReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    lab_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # NEW FIELDS for PDF upload feature
    pdf_file_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Relative path to uploaded PDF file from MEDIA_ROOT"
    )
    pdf_upload_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the PDF file was uploaded"
    )

    def __str__(self):
        return f"Lab Report for {self.patient.name} - {self.timestamp.strftime('%Y-%m-%d')}"
    
    def has_pdf(self):
        """Check if this lab report has an associated PDF file."""
        return bool(self.pdf_file_path)
    
    def get_pdf_url(self):
        """Get URL for accessing the PDF file."""
        if self.pdf_file_path:
            return f"/api/lab-reports/{self.id}/pdf/"
        return None

    class Meta:
        ordering = ['-timestamp']


class Prediction(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    disease_type = models.CharField(max_length=50)  # Diabetes, Heart Disease, Stroke
    risk_score = models.FloatField()  # 0.00-1.00
    risk_category = models.CharField(max_length=20)  # Low, Moderate, High
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.disease_type} Prediction for {self.patient.name} - {self.risk_category} ({self.risk_score:.2f})"

    class Meta:
        ordering = ['-timestamp']


class SHAPExplanation(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='shap_explanations')
    feature_name = models.CharField(max_length=100)
    shap_value = models.FloatField()
    direction = models.CharField(max_length=20)  # increases_risk, decreases_risk

    def __str__(self):
        return f"{self.feature_name}: {self.shap_value:.4f} ({self.direction})"

    class Meta:
        ordering = []  # Will be sorted in queries using abs(shap_value)
