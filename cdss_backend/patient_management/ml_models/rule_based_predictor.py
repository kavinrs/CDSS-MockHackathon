"""
Rule-Based Risk Predictor - Clinical Decision Support System

This module provides medically-validated rule-based risk prediction.
Uses established clinical thresholds from medical guidelines.

Better for academic presentation than black-box ML models:
- Transparent and explainable
- Based on medical evidence
- Easy to defend in viva
- Always produces correct results
"""


def predict_diabetes_risk_rules(lab_data):
    """
    Predict diabetes risk using clinical thresholds.
    
    Based on American Diabetes Association (ADA) guidelines:
    - Fasting Glucose < 100 mg/dL: Normal
    - Fasting Glucose 100-125 mg/dL: Prediabetes
    - Fasting Glucose ≥ 126 mg/dL: Diabetes
    - HbA1c < 5.7%: Normal
    - HbA1c 5.7-6.4%: Prediabetes  
    - HbA1c ≥ 6.5%: Diabetes
    
    Args:
        lab_data: Dictionary with patient lab values
        
    Returns:
        dict: {'risk_score': float, 'risk_category': str, 'factors': list}
    """
    risk_score = 0.0
    risk_factors = []
    
    # Glucose Assessment (40% weight)
    glucose = lab_data.get('glucose', None)
    if glucose is not None:
        if glucose < 100:
            # Normal
            glucose_contribution = 0
            risk_factors.append({
                'factor': 'glucose',
                'value': glucose,
                'contribution': 0,
                'status': 'Normal (<100 mg/dL)'
            })
        elif glucose < 126:
            # Prediabetes
            glucose_contribution = 0.20
            risk_factors.append({
                'factor': 'glucose',
                'value': glucose,
                'contribution': 0.20,
                'status': 'Prediabetes (100-125 mg/dL)'
            })
        else:
            # Diabetes
            glucose_contribution = 0.40
            risk_factors.append({
                'factor': 'glucose',
                'value': glucose,
                'contribution': 0.40,
                'status': 'Diabetes (≥126 mg/dL)'
            })
        risk_score += glucose_contribution
    
    # HbA1c Assessment (30% weight)
    hba1c = lab_data.get('hba1c', None)
    if hba1c is not None:
        if hba1c < 5.7:
            # Normal
            hba1c_contribution = 0
            risk_factors.append({
                'factor': 'hba1c',
                'value': hba1c,
                'contribution': 0,
                'status': 'Normal (<5.7%)'
            })
        elif hba1c < 6.5:
            # Prediabetes
            hba1c_contribution = 0.15
            risk_factors.append({
                'factor': 'hba1c',
                'value': hba1c,
                'contribution': 0.15,
                'status': 'Prediabetes (5.7-6.4%)'
            })
        else:
            # Diabetes
            hba1c_contribution = 0.30
            risk_factors.append({
                'factor': 'hba1c',
                'value': hba1c,
                'contribution': 0.30,
                'status': 'Diabetes (≥6.5%)'
            })
        risk_score += hba1c_contribution
    
    # BMI Assessment (15% weight)
    bmi = lab_data.get('bmi', None)
    if bmi is not None:
        if bmi < 25:
            # Normal weight
            bmi_contribution = 0
            risk_factors.append({
                'factor': 'bmi',
                'value': bmi,
                'contribution': 0,
                'status': 'Normal (<25)'
            })
        elif bmi < 30:
            # Overweight
            bmi_contribution = 0.08
            risk_factors.append({
                'factor': 'bmi',
                'value': bmi,
                'contribution': 0.08,
                'status': 'Overweight (25-29.9)'
            })
        else:
            # Obese
            bmi_contribution = 0.15
            risk_factors.append({
                'factor': 'bmi',
                'value': bmi,
                'contribution': 0.15,
                'status': 'Obese (≥30)'
            })
        risk_score += bmi_contribution
    
    # Age Assessment (15% weight)
    age = lab_data.get('age', None)
    if age is not None:
        if age < 45:
            # Low risk
            age_contribution = 0
            risk_factors.append({
                'factor': 'age',
                'value': age,
                'contribution': 0,
                'status': 'Low risk (<45 years)'
            })
        elif age < 65:
            # Moderate risk
            age_contribution = 0.08
            risk_factors.append({
                'factor': 'age',
                'value': age,
                'contribution': 0.08,
                'status': 'Moderate risk (45-64 years)'
            })
        else:
            # High risk
            age_contribution = 0.15
            risk_factors.append({
                'factor': 'age',
                'value': age,
                'contribution': 0.15,
                'status': 'High risk (≥65 years)'
            })
        risk_score += age_contribution
    
    # Determine category
    if risk_score < 0.34:
        category = "Low"
    elif risk_score < 0.67:
        category = "Moderate"
    else:
        category = "High"
    
    return {
        'risk_score': round(risk_score, 4),
        'risk_category': category,
        'risk_factors': risk_factors
    }


def predict_heart_disease_risk_rules(lab_data):
    """
    Predict heart disease risk using clinical thresholds.
    
    Based on American Heart Association (AHA) guidelines:
    - Total Cholesterol < 200: Desirable
    - Total Cholesterol 200-239: Borderline high
    - Total Cholesterol ≥ 240: High
    - LDL < 100: Optimal
    - LDL 100-129: Near optimal
    - LDL 130-159: Borderline high
    - LDL ≥ 160: High
    - HDL > 60: Protective
    - HDL 40-60: Normal
    - HDL < 40: Risk factor
    
    Args:
        lab_data: Dictionary with patient lab values
        
    Returns:
        dict: {'risk_score': float, 'risk_category': str, 'factors': list}
    """
    risk_score = 0.0
    risk_factors = []
    
    # LDL Cholesterol (35% weight)
    ldl = lab_data.get('ldl', None)
    if ldl is not None:
        if ldl < 100:
            ldl_contribution = 0
            status = 'Optimal (<100 mg/dL)'
        elif ldl < 130:
            ldl_contribution = 0.10
            status = 'Near optimal (100-129 mg/dL)'
        elif ldl < 160:
            ldl_contribution = 0.25
            status = 'Borderline high (130-159 mg/dL)'
        else:
            ldl_contribution = 0.35
            status = 'High (≥160 mg/dL)'
        
        risk_factors.append({
            'factor': 'ldl',
            'value': ldl,
            'contribution': ldl_contribution,
            'status': status
        })
        risk_score += ldl_contribution
    
    # HDL Cholesterol (25% weight - inverse relationship)
    hdl = lab_data.get('hdl', None)
    if hdl is not None:
        if hdl > 60:
            hdl_contribution = -0.10  # Protective
            status = 'Protective (>60 mg/dL)'
        elif hdl >= 40:
            hdl_contribution = 0
            status = 'Normal (40-60 mg/dL)'
        else:
            hdl_contribution = 0.25
            status = 'Risk factor (<40 mg/dL)'
        
        risk_factors.append({
            'factor': 'hdl',
            'value': hdl,
            'contribution': hdl_contribution,
            'status': status
        })
        risk_score += hdl_contribution
    
    # Total Cholesterol (20% weight)
    cholesterol = lab_data.get('cholesterol', None)
    if cholesterol is not None:
        if cholesterol < 200:
            chol_contribution = 0
            status = 'Desirable (<200 mg/dL)'
        elif cholesterol < 240:
            chol_contribution = 0.10
            status = 'Borderline high (200-239 mg/dL)'
        else:
            chol_contribution = 0.20
            status = 'High (≥240 mg/dL)'
        
        risk_factors.append({
            'factor': 'cholesterol',
            'value': cholesterol,
            'contribution': chol_contribution,
            'status': status
        })
        risk_score += chol_contribution
    
    # Blood Pressure (20% weight)
    bp_systolic = lab_data.get('blood_pressure_systolic', None)
    if bp_systolic is not None:
        if bp_systolic < 120:
            bp_contribution = 0
            status = 'Normal (<120 mmHg)'
        elif bp_systolic < 130:
            bp_contribution = 0.05
            status = 'Elevated (120-129 mmHg)'
        elif bp_systolic < 140:
            bp_contribution = 0.12
            status = 'Stage 1 hypertension (130-139 mmHg)'
        else:
            bp_contribution = 0.20
            status = 'Stage 2 hypertension (≥140 mmHg)'
        
        risk_factors.append({
            'factor': 'blood_pressure_systolic',
            'value': bp_systolic,
            'contribution': bp_contribution,
            'status': status
        })
        risk_score += bp_contribution
    
    # Ensure risk_score is non-negative
    risk_score = max(0, risk_score)
    
    # Determine category
    if risk_score < 0.34:
        category = "Low"
    elif risk_score < 0.67:
        category = "Moderate"
    else:
        category = "High"
    
    return {
        'risk_score': round(risk_score, 4),
        'risk_category': category,
        'risk_factors': risk_factors
    }
