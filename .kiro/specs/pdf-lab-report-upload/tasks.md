# Implementation Plan: PDF-based Laboratory Report Upload Feature

## Overview

This implementation adds PDF upload capability to the Clinical Decision Support System, enabling doctors to upload laboratory report PDFs and automatically extract patient data. The feature follows **8 discrete implementation steps** with **mandatory checkpoints** after each step.

**Key Design Principles:**
- **Stop after each step** - Get approval before proceeding
- **Small, focused tasks** - Each function does one thing
- **Beginner-friendly code** - Easy to explain during viva
- **No complex abstractions** - Flat, readable structure
- **Simple regex parsing** - No ML/NLP complexity

**Technology Stack:**
- **PDF Processing**: PyMuPDF (fitz) library
- **Backend**: Django + Django REST Framework
- **Storage**: Local filesystem at `/media/lab_reports/`
- **Database**: PostgreSQL with JSONField
- **Parsing**: Python standard `re` module (regex)

**Implementation Language:** Python (Django framework)

**User Workflow:**
1. Doctor uploads PDF → System saves to /media/lab_reports/
2. System extracts text using PyMuPDF
3. System parses text with regex to find 14 values
4. System auto-populates form fields
5. Doctor reviews and edits values
6. Doctor clicks "Save Patient"
7. Doctor manually triggers "Predict Risk"
8. Doctor requests "AI Recommendation"

## 8-Step Implementation Order

**CRITICAL: Follow this order strictly. Stop after each step for approval.**


1. **Step 1: PDF Upload** - Add endpoint to receive PDF files (checkpoint)
2. **Step 2: PDF Text Extraction** - Use PyMuPDF to extract text (checkpoint)
3. **Step 3: Regex Value Extraction** - Parse clinical values from text (checkpoint)
4. **Step 4: Populate Form** - Auto-fill patient form (checkpoint)
5. **Step 5: Save Patient** - Store patient data + PDF path (checkpoint)
6. **Step 6: Predict Risk** - Run ML models (already working, test integration)
7. **Step 7: SHAP** - Generate explanations (already working, test integration)
8. **Step 8: AI Recommendation** - Call agent (already working, test integration)

## Tasks

### 📤 STEP 1: PDF Upload Endpoint

**Goal**: Create API endpoint that accepts PDF file uploads, validates format and size, saves to filesystem.

- [ ] 1.1 Install PyMuPDF library
  - Add `PyMuPDF>=1.23.0` to requirements.txt
  - Run `pip install PyMuPDF`
  - Verify installation: `python -c "import fitz; print(fitz.__doc__)"`
  - _Requirements: 3.1, 3.2_

- [ ] 1.2 Configure Django media storage settings
  - Open `cdss_backend/settings.py`
  - Add `MEDIA_ROOT = os.path.join(BASE_DIR, 'media')`
  - Add `MEDIA_URL = '/media/'`
  - Create `/media/lab_reports/` directory
  - Verify directory permissions (read/write)
  - _Requirements: 2.1_

- [ ] 1.3 Extend LabReport model with PDF fields
  - Open `patient_management/models.py`
  - Add `pdf_file_path = models.CharField(max_length=500, null=True, blank=True)`
  - Add `pdf_upload_timestamp = models.DateTimeField(null=True, blank=True)`
  - Run `python manage.py makemigrations`
  - Run `python manage.py migrate`
  - Verify new fields in Django admin
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 1.4 Create PDF upload API endpoint
  - Open `patient_management/views.py`
  - Create `UploadLabReportView` class inheriting from `APIView`
  - Add `permission_classes = [IsAuthenticated]`
  - Implement `post(self, request, patient_id)` method
  - Validate patient exists: `Patient.objects.get(id=patient_id)`
  - Get uploaded file: `pdf_file = request.FILES.get('pdf_file')`
  - Return 400 if no file uploaded
  - _Requirements: 1.3, 1.4_

- [ ] 1.5 Implement file validation logic
  - Check file extension: `if not pdf_file.name.endswith('.pdf')`
  - Return error: "Invalid file format. Please upload a PDF file"
  - Check file size: `if pdf_file.size > 10 * 1024 * 1024` (10MB)
  - Return error: "File too large. Maximum size is 10MB"
  - _Requirements: 1.1, 1.2, 1.5, 1.6_

- [ ] 1.6 Implement unique filename generation
  - Import `datetime` module
  - Generate timestamp: `timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')`
  - Create unique filename: `f"patient_{patient_id}_{timestamp}_{pdf_file.name}"`
  - This prevents filename collisions
  - _Requirements: 2.2_

- [ ] 1.7 Save PDF file to media directory
  - Import `FileSystemStorage` from `django.core.files.storage`
  - Create storage: `fs = FileSystemStorage(location='media/lab_reports/')`
  - Save file: `filename = fs.save(unique_filename, pdf_file)`
  - Get full path: `file_path = fs.path(filename)`
  - Return success response with filename
  - _Requirements: 2.1, 2.3_

- [ ] 1.8 Register upload endpoint in URLs
  - Open `patient_management/urls.py`
  - Add URL pattern: `path('patients/<int:patient_id>/upload-lab-report/', UploadLabReportView.as_view())`
  - Import `UploadLabReportView`
  - Full endpoint: `POST /api/patients/{patient_id}/upload-lab-report/`
  - _Requirements: 1.3_

- [ ] 1.9 Test Step 1 manually with Postman or curl
  - Create test patient in database
  - Find a sample PDF file (any PDF works for testing upload)
  - Send POST request with PDF file
  - Verify file saved in `/media/lab_reports/` directory
  - Verify unique filename format: `patient_{id}_{timestamp}_{original_name}.pdf`
  - Test error cases: no file, non-PDF file, >10MB file
  - _Requirements: 1.1-1.6, 2.1-2.3_

---

### ✋ CHECKPOINT 1: PDF Upload Working - STOP HERE

**Before proceeding to Step 2:**
- ✅ PyMuPDF installed successfully
- ✅ Media directory configured and created
- ✅ LabReport model extended with PDF fields
- ✅ Upload endpoint accepts PDF files
- ✅ File validation working (format, size)
- ✅ Files saved with unique filenames
- ✅ Can see uploaded files in /media/lab_reports/ directory

**DO NOT PROCEED TO STEP 2 WITHOUT APPROVAL**

---

### 📄 STEP 2: PDF Text Extraction

**Goal**: Extract raw text from uploaded PDF files using PyMuPDF library.

- [ ] 2.1 Create pdf_processor.py module
  - Create new file: `patient_management/pdf_processor.py`
  - Add docstring: "PDF text extraction using PyMuPDF (fitz) library"
  - Import fitz: `import fitz`
  - Keep this module simple - single purpose
  - _Requirements: 3.1, 12.1_

- [ ] 2.2 Implement extract_text_from_pdf function
  - Define function: `def extract_text_from_pdf(pdf_file_path: str) -> str:`
  - Add docstring explaining: takes file path, returns extracted text
  - Open PDF: `doc = fitz.open(pdf_file_path)`
  - Initialize empty string: `text = ""`
  - Loop through pages: `for page in doc:`
  - Extract text: `text += page.get_text()`
  - Close document: `doc.close()`
  - Return text
  - Function should be < 15 lines (very simple)
  - _Requirements: 3.1, 3.2, 3.5, 12.1, 12.3_

- [ ] 2.3 Add error handling for PDF processing
  - Wrap PDF opening in try-except block
  - Catch generic `Exception` (keep it simple for now)
  - If error: return empty string (graceful degradation)
  - Add comment explaining error is logged but doesn't crash
  - _Requirements: 10.1, 10.2_

- [ ] 2.4 Handle empty PDFs gracefully
  - After extracting text, check: `if not text.strip():`
  - Return empty string (not an error condition)
  - This allows system to notify user later
  - _Requirements: 3.3_

- [ ] 2.5 Integrate text extraction in upload endpoint
  - Open `patient_management/views.py`
  - Import: `from .pdf_processor import extract_text_from_pdf`
  - After saving PDF file, call: `text = extract_text_from_pdf(file_path)`
  - Check if text empty: `if not text:`
  - If empty, return message: "No text found in PDF. Please enter values manually"
  - If text found, include in response: `{'text': text[:500]}` (first 500 chars for debugging)
  - _Requirements: 3.3, 3.4_

- [ ] 2.6 Test Step 2 with sample lab report PDFs
  - Create 2-3 sample PDF files with laboratory values (can be simple text in Word → Save as PDF)
  - Sample content: "Patient Name: John Doe, Age: 45, Glucose: 120 mg/dL"
  - Upload each PDF through the API
  - Verify text extraction returns content
  - Print extracted text to console for verification
  - Test with empty PDF (blank page)
  - Test with scanned image PDF (should return empty - no OCR)
  - _Requirements: 3.1-3.5, 13.2_

---

### ✋ CHECKPOINT 2: Text Extraction Working - STOP HERE

**Before proceeding to Step 3:**
- ✅ pdf_processor.py module created
- ✅ extract_text_from_pdf function implemented
- ✅ Text extraction handles multi-page PDFs
- ✅ Error handling in place
- ✅ Empty PDFs handled gracefully
- ✅ Can see extracted text in API response
- ✅ Sample PDFs successfully extracted

**DO NOT PROCEED TO STEP 3 WITHOUT APPROVAL**

---

### 🔍 STEP 3: Regex Value Extraction

**Goal**: Parse extracted text using regex patterns to identify 14 required laboratory values.

- [ ] 3.1 Create value_extractor.py module
  - Create new file: `patient_management/value_extractor.py`
  - Add docstring: "Laboratory value extraction using regex patterns"
  - Import re: `import re`
  - This module will have 14+ small functions (one per value)
  - _Requirements: 4.1, 12.2, 12.3_

- [ ] 3.2 Implement extract_patient_name function
  - Define: `def extract_patient_name(text: str) -> str | None:`
  - Pattern 1: `r'patient\s+name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)'`
  - Pattern 2: `r'name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)'`
  - Loop through patterns with `re.search(pattern, text, re.IGNORECASE)`
  - If match found: `return match.group(1)`
  - If no match: `return None`
  - Add inline comment explaining pattern
  - Function should be ~10 lines
  - _Requirements: 4.2, 12.2, 12.4_

- [ ] 3.3 Implement extract_age function
  - Define: `def extract_age(text: str) -> int | None:`
  - Pattern 1: `r'age[:\s]+(\d+)'`
  - Pattern 2: `r'(\d+)\s+years'`
  - Use same loop structure as extract_patient_name
  - Convert to int: `return int(match.group(1))`
  - Return None if not found
  - _Requirements: 4.3, 12.2_

- [ ] 3.4 Implement extract_gender function
  - Define: `def extract_gender(text: str) -> str | None:`
  - Pattern 1: `r'gender[:\s]+(male|female|M|F)'`
  - Pattern 2: `r'sex[:\s]+(male|female|M|F)'`
  - Normalize result: convert "M" to "Male", "F" to "Female"
  - Return None if not found
  - _Requirements: 4.4, 12.2_

- [ ] 3.5 Implement extract_glucose function
  - Define: `def extract_glucose(text: str) -> float | None:`
  - Pattern 1: `r'glucose[:\s]+(\d+\.?\d*)\s*mg'`
  - Pattern 2: `r'FBS[:\s]+(\d+\.?\d*)'` (Fasting Blood Sugar)
  - Pattern 3: `r'blood\s+glucose[:\s]+(\d+\.?\d*)'`
  - Convert to float: `return float(match.group(1))`
  - Add comment: "Matches: Glucose: 120 mg/dL, FBS: 110, Blood Glucose 95"
  - _Requirements: 4.5, 12.4_

- [ ] 3.6 Implement extract_hba1c function
  - Define: `def extract_hba1c(text: str) -> float | None:`
  - Pattern 1: `r'HbA1c[:\s]+(\d+\.?\d*)\s*%'`
  - Pattern 2: `r'A1C[:\s]+(\d+\.?\d*)'`
  - Convert to float
  - _Requirements: 4.6_

- [ ] 3.7 Implement extract_bmi function
  - Define: `def extract_bmi(text: str) -> float | None:`
  - Pattern: `r'BMI[:\s]+(\d+\.?\d*)'`
  - Convert to float
  - _Requirements: 4.7_

- [ ] 3.8 Implement cholesterol extraction functions
  - `extract_total_cholesterol(text: str) -> float | None`
  - Pattern: `r'total\s+cholesterol[:\s]+(\d+\.?\d*)'`
  - `extract_hdl(text: str) -> float | None`
  - Pattern: `r'HDL[:\s]+(\d+\.?\d*)'`
  - `extract_ldl(text: str) -> float | None`
  - Pattern: `r'LDL[:\s]+(\d+\.?\d*)'`
  - All return float or None
  - _Requirements: 4.8, 4.9, 4.10_

- [ ] 3.9 Implement extract_triglycerides function
  - Define: `def extract_triglycerides(text: str) -> float | None:`
  - Pattern 1: `r'triglycerides[:\s]+(\d+\.?\d*)'`
  - Pattern 2: `r'TG[:\s]+(\d+\.?\d*)'`
  - Convert to float
  - _Requirements: 4.11_

- [ ] 3.10 Implement blood pressure extraction function
  - Define: `def extract_blood_pressure(text: str) -> tuple[int | None, int | None]:`
  - Pattern 1: `r'blood\s+pressure[:\s]+(\d+)/(\d+)'`
  - Pattern 2: `r'BP[:\s]+(\d+)/(\d+)'`
  - Return tuple: `(int(match.group(1)), int(match.group(2)))`
  - If not found: `return (None, None)`
  - Extracts both systolic and diastolic in one function
  - _Requirements: 4.12, 4.13_

- [ ] 3.11 Implement extract_heart_rate function
  - Define: `def extract_heart_rate(text: str) -> int | None:`
  - Pattern 1: `r'heart\s+rate[:\s]+(\d+)'`
  - Pattern 2: `r'pulse[:\s]+(\d+)'`
  - Pattern 3: `r'HR[:\s]+(\d+)'`
  - Convert to int
  - _Requirements: 4.14_

- [ ] 3.12 Implement extract_all_values orchestrator function
  - Define: `def extract_all_values(text: str) -> dict:`
  - Call extract_blood_pressure first: `systolic, diastolic = extract_blood_pressure(text)`
  - Build and return dictionary with all 14 values
  - Keys: patient_name, age, gender, glucose, hba1c, bmi, total_cholesterol, hdl, ldl, triglycerides, systolic_bp, diastolic_bp, heart_rate
  - Values are None if not extracted (NEVER generate fake data)
  - _Requirements: 4.1, 4.15, 4.16_

- [ ] 3.13 Integrate value extraction in upload endpoint
  - Open `patient_management/views.py`
  - Import: `from .value_extractor import extract_all_values`
  - After text extraction, call: `extracted_values = extract_all_values(text)`
  - Count successes: `non_null_count = sum(1 for v in extracted_values.values() if v is not None)`
  - Calculate rate: `success_rate = non_null_count / 14`
  - Include in response: extracted_values, success count, success rate
  - _Requirements: 4.16_

- [ ] 3.14 Test Step 3 with sample lab reports
  - Create 3 sample PDF files with different formats
  - Sample 1: "Patient Name: John Doe\nAge: 45\nGlucose: 120 mg/dL\n..."
  - Sample 2: "Name: Jane Smith, Age 52, FBS 105, BP 130/85..."
  - Sample 3: Mix of formats
  - Upload each PDF
  - Verify extracted values in response
  - Check that unmatched fields are None (not fake data)
  - Aim for >80% extraction success on well-formatted PDFs
  - _Requirements: 4.1-4.16, 13.3_

---

### ✋ CHECKPOINT 3: Value Extraction Working - STOP HERE

**Before proceeding to Step 4:**
- ✅ value_extractor.py module created
- ✅ All 14 extraction functions implemented
- ✅ extract_all_values orchestrator working
- ✅ Regex patterns tested with sample PDFs
- ✅ Extraction integrated into upload endpoint
- ✅ API returns extracted values
- ✅ Achieving >80% success rate on formatted PDFs
- ✅ Missing values return None (no fake data)

**DO NOT PROCEED TO STEP 4 WITHOUT APPROVAL**

---

### 📝 STEP 4: Auto-Populate Patient Form

**Goal**: Frontend receives extracted values and auto-fills form fields for doctor review.

**Note**: This step involves frontend work (React). If frontend is not ready yet, document the API contract and move to Step 5.

- [ ] 4.1 Document API response format
  - Open `patient_management/views.py`
  - Ensure UploadLabReportView returns clear JSON structure
  - Response format:
    ```json
    {
      "message": "Extracted 12 of 14 values",
      "pdf_file_path": "lab_reports/patient_1_20240315_abc123.pdf",
      "pdf_upload_timestamp": "2024-03-15T10:30:00Z",
      "extracted_values": {
        "patient_name": "John Doe",
        "age": 45,
        "gender": "Male",
        "glucose": 120.5,
        ...
      },
      "extraction_success_rate": 0.86,
      "non_null_count": 12,
      "total_count": 14
    }
    ```
  - _Requirements: 5.4_

- [ ] 4.2 Add success message logic
  - If `non_null_count >= 11` (80% threshold): success message
  - If `non_null_count < 11`: warning message
  - Include count in message: "Extracted X of 14 values"
