"""
Value Extractor - Parse laboratory values from PDF text using regex.
Simple, deterministic extraction for academic presentation.
"""

import re


def extract_patient_name(text):
    """
    Extract patient name from text.
    Patterns: "Patient Name: John Doe", "Name: Jane Smith"
    """
    patterns = [
        r'patient\s+name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def extract_age(text):
    """
    Extract age from text.
    Patterns: "Age: 45", "Age 45 years", "45 years old", "Age / Sex : 29 Y / F"
    """
    patterns = [
        r'Age\s*/\s*Sex\s*:\s*(\d+)\s*Y',        # Age / Sex : 29 Y / F (HOD format)
        r'age[:/\s]+(\d+)\s*[Yy]',              # Age: 29 Y or Age/Sex: 29 Y
        r'age[:\s]+(\d+)',                      # Age: 45
        r'(\d+)\s+[Yy]\s*/\s*[MFmf]',          # 29 Y / F
        r'(\d+)\s+years?\s+old'                 # 45 years old
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            age = int(match.group(1))
            if 0 < age < 120:  # Sanity check
                return age
    
    return None


def extract_gender(text):
    """
    Extract gender from text.
    Patterns: "Gender: Male", "Sex: Female", "Age / Sex : 29 Y / F"
    """
    patterns = [
        r'Age\s*/\s*Sex\s*:\s*\d+\s*Y\s*/\s*([MF])',  # Age / Sex : 29 Y / F (HOD format)
        r'gender[:\s]+(male|female|other|M|F)',
        r'sex[:\s]+(male|female|other|M|F)',
        r'\b(male|female)\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            gender_char = match.group(1).upper()
            if gender_char == 'M':
                return 'Male'
            elif gender_char == 'F':
                return 'Female'
            else:
                return match.group(1).capitalize()
    
    return None


def extract_glucose(text):
    """
    Extract glucose value from text.
    Patterns: "Glucose: 120 mg/dL", "Blood Glucose 95", "FBS: 110", "Blood Sugar Fasting 82"
    """
    patterns = [
        r'Blood\s+Sugar\s+Fasting\s+(\d+\.?\d*)',  # Blood Sugar Fasting 82 (HOD format)
        r'glucose[:\s]+(\d+\.?\d*)\s*mg',          # Glucose: 120 mg/dL
        r'FBS[:\)]\s*[:\s]*(\d+\.?\d*)',           # FBS: 110 or FBS): 145
        r'blood\s+glucose[:\s]+(\d+\.?\d*)',       # Blood Glucose 95
        r'fasting\s+glucose[:\s]+(\d+\.?\d*)',     # Fasting Glucose: 100
        r'fasting\s+blood\s+glucose[:\s\)]+(\d+\.?\d*)',  # Fasting Blood Glucose (FBS): 145
        r'glucose\s+metabolism.*?(\d+\.?\d*)\s*mg/dL',  # From table format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            glucose = float(match.group(1))
            if 20 < glucose < 500:  # Sanity check for glucose range
                return glucose
    
    return None


def extract_hba1c(text):
    """
    Extract HbA1c value from text.
    Patterns: "HbA1c: 6.5%", "A1C 7.2", "Hemoglobin A1c: 5.8%"
    """
    patterns = [
        r'HbA1c[:\s]+(\d+\.?\d*)\s*%?',
        r'A1C[:\s]+(\d+\.?\d*)\s*%?',
        r'hemoglobin\s+A1c[:\s]+(\d+\.?\d*)\s*%?',
        r'glycated\s+h[ae]moglobin.*?(\d+\.?\d*)\s*%?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            hba1c = float(match.group(1))
            if 3 < hba1c < 20:  # Sanity check for HbA1c range
                return hba1c
    
    return None


def extract_bmi(text):
    """
    Extract BMI value from text.
    Patterns: "BMI: 28.3", "Body Mass Index 32.5"
    """
    patterns = [
        r'BMI[:\)]\s*[:\s]*(\d+\.?\d*)',         # BMI: 28.3 or BMI): 29.8
        r'body\s+mass\s+index[:\)]\s*[:\s]*(\d+\.?\d*)'  # Body Mass Index (BMI): 29.8
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    return None


def extract_total_cholesterol(text):
    """
    Extract total cholesterol from text.
    Patterns: "Total Cholesterol: 220 mg/dL", "Cholesterol 200"
    """
    patterns = [
        r'total\s+cholesterol[:\s]+(\d+\.?\d*)\s*mg',
        r'cholesterol\s+total[:\s]+(\d+\.?\d*)\s*mg',
        r'cholesterol[:\s]+(\d+\.?\d*)\s*mg',
        r'serum\s+cholesterol[:\s]+(\d+\.?\d*)',
        # Handle plain number after cholesterol in tables
        r'cholesterol[:\s]+(\d+\.?\d*)\s*(?:mg|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cholesterol = float(match.group(1))
            if 50 < cholesterol < 500:  # Sanity check
                return cholesterol
    
    return None


def extract_hdl(text):
    """
    Extract HDL cholesterol from text.
    Patterns: "HDL: 45 mg/dL", "HDL Cholesterol 50"
    """
    patterns = [
        r'HDL[:\s]+(\d+\.?\d*)\s*mg',
        r'HDL\s+cholesterol[:\s]+(\d+\.?\d*)\s*mg'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    return None


def extract_ldl(text):
    """
    Extract LDL cholesterol from text.
    Patterns: "LDL: 140 mg/dL", "LDL Cholesterol 130", "LDL Cholesterol 59"
    Must NOT match VLDL Cholesterol.
    """
    patterns = [
        r'(?<!V)LDL\s+Cholesterol\s+(\d+\.?\d*)\s*mg',  # LDL Cholesterol 59 mg/dL (not VLDL)
        r'(?<!V)LDL[:\s]+(\d+\.?\d*)\s*mg',             # LDL: 59 mg/dL (not VLDL)
        r'(?<!V)LDL\s+cholesterol[:\s]+(\d+\.?\d*)\s*mg'  # LDL cholesterol: 59 (not VLDL)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            ldl = float(match.group(1))
            if 10 < ldl < 300:  # Sanity check (LDL typically 10-300)
                return ldl
    
    return None


def extract_triglycerides(text):
    """
    Extract triglycerides from text.
    Patterns: "Triglycerides: 175 mg/dL", "TG 150", "Triglyceride 73"
    """
    patterns = [
        r'Triglyceride\s+(\d+\.?\d*)\s*mg',       # Triglyceride 73 mg/dL (HOD format, singular)
        r'triglycerides[:\s]+(\d+\.?\d*)\s*mg',
        r'TG[:\s]+(\d+\.?\d*)\s*mg'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            triglycerides = float(match.group(1))
            if 20 < triglycerides < 1000:  # Sanity check
                return triglycerides
    
    return None


def extract_blood_pressure(text):
    """
    Extract systolic and diastolic blood pressure.
    Patterns: "BP: 120/80 mmHg", "Blood Pressure 130/85"
    """
    patterns = [
        r'blood\s+pressure[:\s\)]+(\d+)/(\d+)',      # Blood Pressure: 120/80
        r'BP[:\)]\s*[:\s]*(\d+)/(\d+)'               # BP: 142/88 or BP): 142/88
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            systolic = int(match.group(1))
            diastolic = int(match.group(2))
            return systolic, diastolic
    
    return None, None


def extract_heart_rate(text):
    """
    Extract heart rate from text.
    Patterns: "Heart Rate: 75 bpm", "HR 80", "Pulse 72"
    """
    patterns = [
        r'heart\s+rate[:\s\)]+(\d+)',     # Heart Rate: 75 or Heart Rate (HR): 82
        r'HR[:\)]\s*[:\s]*(\d+)',         # HR: 80 or HR): 82
        r'pulse[:\s]+(\d+)'               # Pulse: 72
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return None


def extract_all_values(text):
    """
    Orchestrator function that calls all individual extractors.
    
    Args:
        text: Raw text extracted from PDF
        
    Returns:
        Dictionary with all extracted values (None if not found)
        
    Note: Field names match the ML model's expected feature names for consistency.
    """
    systolic, diastolic = extract_blood_pressure(text)
    
    return {
        'patient_name': extract_patient_name(text),
        'age': extract_age(text),
        'gender': extract_gender(text),
        'glucose': extract_glucose(text),
        'hba1c': extract_hba1c(text),
        'bmi': extract_bmi(text),
        'cholesterol': extract_total_cholesterol(text),  # Renamed from 'total_cholesterol'
        'hdl': extract_hdl(text),
        'ldl': extract_ldl(text),
        'triglycerides': extract_triglycerides(text),
        'blood_pressure_systolic': systolic,  # Renamed from 'systolic_bp'
        'blood_pressure_diastolic': diastolic,  # Renamed from 'diastolic_bp'
        'heart_rate': extract_heart_rate(text)
    }
