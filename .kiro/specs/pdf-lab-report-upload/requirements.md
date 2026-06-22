# Requirements Document

## Introduction

This document specifies requirements for the PDF-based Laboratory Report Upload feature for the Clinical Decision Support System. The feature replaces manual laboratory value entry with automated PDF upload and data extraction, enabling doctors to upload laboratory report PDFs, automatically extract clinical values, verify the extracted data, and save patient information efficiently.

The system will use PyMuPDF (fitz) for deterministic text extraction from PDF files containing selectable text (no OCR), apply simple regex-based parsing to extract required laboratory values, and preserve original PDF files for future reference.

## Glossary

- **CDSS**: Clinical Decision Support System - the Django-based web application
- **Doctor**: The authenticated medical professional using the system
- **Lab_Report**: A PDF document containing patient laboratory test results
- **PDF_Processor**: The backend component responsible for extracting text from PDF files using PyMuPDF
- **Value_Extractor**: The backend component responsible for parsing extracted text and identifying clinical values
- **Patient_Form**: The web form interface where doctors view and edit patient and laboratory data
- **LabReport_Model**: The Django database model storing laboratory report data and metadata
- **Media_Storage**: The /media/lab_reports/ directory where PDF files are stored
- **Required_Values**: Patient Name, Age, Gender, Glucose, HbA1c, BMI, Total Cholesterol, HDL, LDL, Triglycerides, Blood Pressure (Systolic/Diastolic), Heart Rate
- **Extraction_Success_Threshold**: A minimum of 80% of Required_Values successfully extracted
- **Verification_Step**: The required doctor review process before saving extracted data
- **Predict_Risk_Action**: The existing ML model prediction triggered by doctor after saving patient data

## Requirements

### Requirement 1: PDF File Upload

**User Story:** As a doctor, I want to upload a laboratory report PDF file from my computer, so that the system can extract patient data automatically without manual entry.

#### Acceptance Criteria

1. WHEN a doctor selects a file for upload, THE CDSS SHALL validate that the file format is PDF
2. IF the selected file is not a PDF format, THEN THE CDSS SHALL display an error message "Invalid file format. Please upload a PDF file" and prevent upload
3. WHEN a valid PDF file is selected, THE CDSS SHALL upload the file to the backend server
4. WHEN the upload completes successfully, THE CDSS SHALL display a confirmation message indicating upload success
5. THE CDSS SHALL support PDF files up to 10 megabytes in size
6. IF the PDF file exceeds 10 megabytes, THEN THE CDSS SHALL display an error message "File too large. Maximum size is 10MB" and prevent upload

### Requirement 2: PDF File Storage

**User Story:** As a doctor, I want the system to preserve original laboratory report PDFs, so that I can view or download the original documents later for verification or record-keeping.

#### Acceptance Criteria

1. WHEN a PDF file is uploaded, THE Media_Storage SHALL store the file in the /media/lab_reports/ directory
2. THE Media_Storage SHALL generate a unique filename for each uploaded PDF to prevent filename collisions
3. THE LabReport_Model SHALL store the file path to the uploaded PDF in the pdf_file_path field
4. THE LabReport_Model SHALL store the upload timestamp in the pdf_upload_timestamp field
5. THE CDSS SHALL never delete uploaded PDF files from Media_Storage
6. WHEN a doctor views a patient record with an associated lab report, THE CDSS SHALL provide a download link to the original PDF file
7. WHEN a doctor clicks the download link, THE CDSS SHALL serve the original PDF file for viewing or download

### Requirement 3: Text Extraction from PDF

**User Story:** As a doctor, I want the system to extract text from uploaded PDF laboratory reports, so that clinical values can be parsed and populated automatically.

#### Acceptance Criteria

1. WHEN a PDF file is uploaded, THE PDF_Processor SHALL extract text from all pages using PyMuPDF (fitz) library
2. THE PDF_Processor SHALL extract selectable text content from the PDF without using OCR
3. IF the PDF contains no extractable text, THEN THE PDF_Processor SHALL return an empty string and THE CDSS SHALL notify the doctor "No text found in PDF. Please enter values manually"
4. WHEN text extraction completes, THE PDF_Processor SHALL return the complete extracted text to the Value_Extractor
5. THE PDF_Processor SHALL handle multi-page PDF documents and extract text from all pages

### Requirement 4: Laboratory Value Extraction

**User Story:** As a doctor, I want the system to automatically identify and extract required laboratory values from the PDF text, so that I can verify pre-filled data instead of entering everything manually.

#### Acceptance Criteria

1. WHEN extracted text is received from PDF_Processor, THE Value_Extractor SHALL parse the text using deterministic regex patterns to identify Required_Values
2. THE Value_Extractor SHALL extract Patient Name from the text
3. THE Value_Extractor SHALL extract Age from the text
4. THE Value_Extractor SHALL extract Gender from the text
5. THE Value_Extractor SHALL extract Glucose level from the text
6. THE Value_Extractor SHALL extract HbA1c percentage from the text
7. THE Value_Extractor SHALL extract BMI value from the text
8. THE Value_Extractor SHALL extract Total Cholesterol level from the text
9. THE Value_Extractor SHALL extract HDL cholesterol level from the text
10. THE Value_Extractor SHALL extract LDL cholesterol level from the text
11. THE Value_Extractor SHALL extract Triglycerides level from the text
12. THE Value_Extractor SHALL extract Systolic Blood Pressure from the text
13. THE Value_Extractor SHALL extract Diastolic Blood Pressure from the text
14. THE Value_Extractor SHALL extract Heart Rate from the text
15. IF a Required_Value is not found in the extracted text, THEN THE Value_Extractor SHALL leave that field empty without generating fake data
16. THE Value_Extractor SHALL return all extracted values to the Patient_Form for display

### Requirement 5: Auto-Population of Patient Form

**User Story:** As a doctor, I want extracted laboratory values to automatically populate the patient form fields, so that I can quickly review and verify the data without retyping.

#### Acceptance Criteria

1. WHEN laboratory values are extracted, THE Patient_Form SHALL automatically populate all form fields with the corresponding extracted values
2. THE Patient_Form SHALL leave fields empty when corresponding values were not extracted
3. THE Patient_Form SHALL keep all form fields editable after auto-population
4. WHEN auto-population completes, THE Patient_Form SHALL display a success message showing the count of successfully extracted values (e.g., "Extracted 12 of 14 values")
5. IF fewer than Extraction_Success_Threshold of Required_Values are extracted, THEN THE Patient_Form SHALL display a warning message "Only X of 14 values extracted. Please verify and complete missing values"
6. THE Patient_Form SHALL visually distinguish auto-populated fields from empty fields that require manual entry

### Requirement 6: Doctor Verification and Editing

**User Story:** As a doctor, I want to review and edit all extracted laboratory values before saving, so that I can correct any extraction errors and ensure data accuracy.

#### Acceptance Criteria

1. WHEN the Patient_Form displays extracted values, THE CDSS SHALL require the doctor to complete the Verification_Step before saving
2. THE Patient_Form SHALL allow the doctor to edit any auto-populated field value
3. THE Patient_Form SHALL allow the doctor to fill in any empty field manually
4. THE Patient_Form SHALL validate that all Required_Values are present before enabling the save button
5. IF any Required_Value is missing, THEN THE Patient_Form SHALL display validation errors indicating which fields are required
6. WHEN all Required_Values are present, THE Patient_Form SHALL enable the "Save Patient" button

### Requirement 7: Saving Patient Data with Lab Report

**User Story:** As a doctor, I want to save verified patient data along with laboratory values and PDF metadata, so that the complete patient record is stored for future risk prediction and recommendations.

#### Acceptance Criteria

1. WHEN the doctor clicks "Save Patient", THE LabReport_Model SHALL store patient details in the PostgreSQL database
2. THE LabReport_Model SHALL store laboratory values in the lab_data JSONField
3. THE LabReport_Model SHALL store the pdf_file_path referencing the uploaded PDF file
4. THE LabReport_Model SHALL store the pdf_upload_timestamp indicating when the PDF was uploaded
5. WHEN the save operation completes successfully, THE CDSS SHALL display a success message "Patient data saved successfully"
6. WHEN the save operation fails, THE CDSS SHALL display an error message with details about the failure
7. THE CDSS SHALL not automatically trigger Predict_Risk_Action after saving patient data

### Requirement 8: Risk Prediction Workflow Control

**User Story:** As a doctor, I want to manually trigger risk prediction after verifying and saving patient data, so that I maintain control over the clinical workflow and ensure data accuracy before analysis.

#### Acceptance Criteria

1. WHEN patient data is saved after PDF upload, THE CDSS SHALL not automatically execute Predict_Risk_Action
2. THE CDSS SHALL display a "Predict Risk" button on the patient detail page after saving
3. WHEN the doctor clicks "Predict Risk", THE CDSS SHALL execute the ML model prediction using the saved laboratory values
4. THE CDSS SHALL display prediction results only after the doctor explicitly requests them
5. WHEN prediction completes, THE CDSS SHALL enable the "AI Recommendation" button for further clinical decision support

### Requirement 9: Parser and Pretty Printer for Laboratory Values

**User Story:** As a developer, I want to parse laboratory value text and format it back to text, so that I can verify the parsing logic is correct through round-trip testing.

#### Acceptance Criteria

1. WHEN laboratory value text is provided, THE Value_Extractor SHALL parse it into a structured LaboratoryValues object
2. WHEN an invalid laboratory value format is provided, THE Value_Extractor SHALL return a descriptive error indicating which value failed validation
3. THE Value_Extractor SHALL provide a pretty_print function that formats LaboratoryValues objects back into readable text format
4. FOR ALL valid LaboratoryValues objects, parsing the pretty_print output SHALL produce an equivalent LaboratoryValues object (round-trip property)

### Requirement 10: Error Handling for PDF Processing

**User Story:** As a doctor, I want clear error messages when PDF processing fails, so that I understand what went wrong and can take appropriate action.

#### Acceptance Criteria

1. IF PyMuPDF fails to open the PDF file, THEN THE CDSS SHALL display an error message "Unable to read PDF file. The file may be corrupted"
2. IF text extraction fails during processing, THEN THE CDSS SHALL display an error message "Failed to extract text from PDF. Please try a different file or enter values manually"
3. IF the PDF file is password-protected, THEN THE CDSS SHALL display an error message "Cannot process password-protected PDFs. Please remove password protection and try again"
4. IF file upload fails due to network issues, THEN THE CDSS SHALL display an error message "Upload failed. Please check your connection and try again"
5. WHEN any error occurs during PDF processing, THE CDSS SHALL preserve any already-entered manual data in the form

### Requirement 11: Database Schema Extensions

**User Story:** As a developer, I want to extend the LabReport model with PDF-related fields, so that the system can store and retrieve PDF metadata alongside laboratory values.

#### Acceptance Criteria

1. THE LabReport_Model SHALL include a pdf_file_path field of type CharField with max_length 500
2. THE LabReport_Model SHALL allow pdf_file_path to be null for laboratory reports entered manually without PDF upload
3. THE LabReport_Model SHALL include a pdf_upload_timestamp field of type DateTimeField
4. THE LabReport_Model SHALL allow pdf_upload_timestamp to be null for laboratory reports entered manually without PDF upload
5. THE LabReport_Model SHALL maintain backward compatibility with existing laboratory reports that have no associated PDF file

### Requirement 12: Simple and Maintainable Code

**User Story:** As a student, I want the PDF extraction and parsing code to be simple and beginner-friendly, so that I can explain the implementation clearly during viva examination.

#### Acceptance Criteria

1. THE PDF_Processor SHALL implement text extraction in a single function with no more than 30 lines of code
2. THE Value_Extractor SHALL implement each value extraction as a separate small function following single responsibility principle
3. THE Value_Extractor SHALL use only standard Python regex module without complex NLP libraries
4. THE CDSS SHALL include inline comments explaining regex patterns used for value extraction
5. THE CDSS SHALL avoid unnecessary abstractions and keep the code structure flat and readable
6. THE CDSS SHALL use descriptive variable and function names that clearly indicate purpose

### Requirement 13: Testing and Validation

**User Story:** As a developer, I want to test PDF processing and value extraction with sample laboratory reports, so that I can verify the system meets Extraction_Success_Threshold before deployment.

#### Acceptance Criteria

1. THE CDSS SHALL provide test cases for PDF upload validation
2. THE CDSS SHALL provide test cases for text extraction using sample PDF files
3. THE CDSS SHALL provide test cases verifying each Required_Value extraction pattern
4. THE CDSS SHALL provide test cases verifying round-trip property for parser and pretty printer
5. THE CDSS SHALL provide test cases for error handling scenarios
6. WHEN tests are executed, THE CDSS SHALL achieve at least Extraction_Success_Threshold success rate on sample laboratory reports

### Requirement 14: Frontend Upload Interface

**User Story:** As a doctor, I want an intuitive file upload interface on the patient form, so that I can easily select and upload laboratory report PDFs.

#### Acceptance Criteria

1. THE Patient_Form SHALL display a file upload button labeled "Upload Lab Report (PDF)"
2. WHEN the doctor clicks the upload button, THE Patient_Form SHALL open a file selection dialog
3. THE Patient_Form SHALL restrict the file selection dialog to PDF files only
4. WHEN a file is selected, THE Patient_Form SHALL display the filename below the upload button
5. THE Patient_Form SHALL display an upload progress indicator while the file is uploading
6. WHEN extraction is in progress, THE Patient_Form SHALL display a loading message "Extracting values from PDF..."
7. THE Patient_Form SHALL position the upload button prominently at the top of the form above manual entry fields

### Requirement 15: Access to Original PDF Files

**User Story:** As a doctor, I want to view the original laboratory report PDF from a patient's record, so that I can verify extracted values against the source document.

#### Acceptance Criteria

1. WHEN a patient record has an associated PDF file, THE CDSS SHALL display a "View Lab Report PDF" link on the patient detail page
2. WHEN the doctor clicks "View Lab Report PDF", THE CDSS SHALL open the PDF file in a new browser tab
3. IF a patient record has no associated PDF file, THEN THE CDSS SHALL hide the "View Lab Report PDF" link
4. THE CDSS SHALL serve PDF files with appropriate Content-Type header (application/pdf)
5. THE CDSS SHALL implement access control ensuring only authenticated doctors can access PDF files
