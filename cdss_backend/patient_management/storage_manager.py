"""
Storage Manager - Handle PDF file storage and path generation.
Simple implementation for academic presentation.
"""

from django.core.files.storage import FileSystemStorage
from datetime import datetime
import os


class LabReportStorageManager:
    """
    Manages PDF file storage and path generation.
    Uses static methods (no instance state needed).
    """
    
    STORAGE_DIR = 'media/lab_reports/'
    
    @staticmethod
    def generate_unique_filename(patient_id, original_filename):
        """
        Generate a unique filename for uploaded PDF.
        Format: patient_{id}_{timestamp}_{original_name}
        
        Args:
            patient_id: Patient's ID number
            original_filename: Original name of uploaded file
            
        Returns:
            Unique filename string
            
        Example:
            >>> LabReportStorageManager.generate_unique_filename(123, 'report.pdf')
            'patient_123_20240315_143022_report.pdf'
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(original_filename)[0]
        extension = os.path.splitext(original_filename)[1]
        return f"patient_{patient_id}_{timestamp}_{base_name}{extension}"
    
    @staticmethod
    def get_storage_location():
        """
        Return the storage directory path.
        Default: media/lab_reports/
        """
        return LabReportStorageManager.STORAGE_DIR
    
    @staticmethod
    def save_pdf_file(pdf_file, patient_id):
        """
        Save uploaded PDF file and return relative path.
        
        Args:
            pdf_file: Uploaded file object from request.FILES
            patient_id: Patient's ID number
            
        Returns:
            Relative path from MEDIA_ROOT (e.g., 'lab_reports/patient_1_20240315_report.pdf')
        """
        # Generate unique filename
        unique_filename = LabReportStorageManager.generate_unique_filename(
            patient_id, pdf_file.name
        )
        
        # Save to storage
        fs = FileSystemStorage(location=LabReportStorageManager.STORAGE_DIR)
        filename = fs.save(unique_filename, pdf_file)
        
        # Return relative path from MEDIA_ROOT
        return os.path.join('lab_reports', filename)
    
    @staticmethod
    def get_full_path(relative_path):
        """
        Convert relative path to absolute filesystem path.
        
        Args:
            relative_path: Path relative to MEDIA_ROOT
            
        Returns:
            Absolute filesystem path
        """
        return os.path.join('media', relative_path)
