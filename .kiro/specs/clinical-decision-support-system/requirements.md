# Requirements Document

## Introduction

The AI-Powered Clinical Decision Support System (CDSS) is a doctor-side application designed to assist healthcare professionals in clinical decision-making. The system combines Machine Learning risk prediction models, explainable AI techniques, Retrieval-Augmented Generation (RAG) for medical knowledge retrieval, and an AI Agent for generating evidence-based clinical recommendations. 

**This is a Final Year Engineering Project** with emphasis on:
- **Readability over optimization**
- **Simplicity over complexity**
- **Modularity for easy explanation**
- **Academic presentation focus**

**Technology Stack:**
- Backend: **Django + Django REST Framework** (NOT Flask)
- Frontend: React
- Database: PostgreSQL
- ML: XGBoost, SHAP
- AI: LangChain, OpenAI Embeddings, FAISS, GPT-4/Claude

**Development Approach:**
- Build **module by module** with mandatory checkpoints
- Complete one module, STOP, wait for review
- Use Django built-in features (authentication, ORM, sessions)
- Avoid unnecessary complexity (no retry frameworks, connection pooling, advanced logging, property-based testing, etc.)

## Glossary

- **CDSS**: The Clinical Decision Support System being developed
- **Doctor**: A healthcare professional user of the system
- **Patient**: An individual whose medical information is stored and analyzed
- **Risk_Predictor**: The ML component that calculates disease risk scores using XGBoost models
- **SHAP_Explainer**: The component that generates explanations for ML predictions
- **RAG_System**: The Retrieval-Augmented Generation system for medical knowledge retrieval
- **AI_Agent**: The LangChain-based agent that orchestrates tool calls and generates recommendations
- **Patient_Data_Tool**: Agent tool that retrieves patient details from the database
- **Prediction_Tool**: Agent tool that retrieves risk scores and SHAP explanations
- **Knowledge_Tool**: Agent tool that retrieves clinical guidelines using RAG
- **Risk_Score**: A numerical value indicating disease probability
- **Risk_Category**: A classification of risk (e.g., Low, Moderate, High)
- **FAISS_Index**: The vector database storing medical guideline embeddings
- **Clinical_Guideline**: Evidence-based medical documentation used for decision support

## Requirements

### Requirement 1: Doctor Authentication

**User Story:** As a doctor, I want to securely authenticate into the system, so that I can access patient data and clinical tools.

#### Acceptance Criteria

1. THE CDSS SHALL use Django's built-in authentication system for doctor login
2. THE CDSS SHALL provide a login interface accepting username and password fields
3. WHEN a doctor submits valid credentials, THE CDSS SHALL authenticate the doctor and grant access to patient data and clinical tools
4. WHEN authentication fails, THE CDSS SHALL display a generic error message indicating authentication failure
5. THE CDSS SHALL use Django's default session management for maintaining login state

### Requirement 2: Patient Registration and Management

**User Story:** As a doctor, I want to register new patients and manage their information, so that I can maintain accurate medical records.

#### Acceptance Criteria

1. THE CDSS SHALL allow doctors to create new patient records with demographic information including name, date of birth, gender, phone number, and email, where name and date of birth are required fields
2. THE CDSS SHALL validate that required fields are present before storing
3. THE CDSS SHALL store patient information in the PostgreSQL database using Django ORM
4. THE CDSS SHALL allow doctors to view existing patient records
5. THE CDSS SHALL allow doctors to update patient information
6. THE CDSS SHALL use Django's auto-generated primary key as the unique patient identifier
7. IF a patient record fails validation, THEN THE CDSS SHALL display an error message identifying which fields are invalid

### Requirement 3: Medical History Storage

**User Story:** As a doctor, I want to store patient medical history and laboratory reports, so that I have complete clinical context for decision-making.

#### Acceptance Criteria

1. THE CDSS SHALL allow doctors to input medical history for a patient including past diagnoses, current medications, known allergies, and clinical notes
2. THE CDSS SHALL allow doctors to input laboratory report data for a patient as structured fields containing numeric or text values
3. THE CDSS SHALL store medical history in the PostgreSQL database linked to the patient record using Django ORM foreign keys
4. THE CDSS SHALL store laboratory data in the PostgreSQL database linked to the patient record
5. THE CDSS SHALL automatically timestamp entries using Django's auto_now_add field
6. IF the patient identifier is invalid, THEN THE CDSS SHALL display an error message indicating the patient was not found
7. IF medical data fails validation, THEN THE CDSS SHALL display an error message identifying which fields are invalid
8. WHEN medical data is stored successfully, THE CDSS SHALL display a confirmation message

### Requirement 4: Clinical Risk Prediction

**User Story:** As a doctor, I want to predict disease risk for patients, so that I can assess their health status and plan interventions.

#### Acceptance Criteria

1. THE CDSS SHALL load trained XGBoost models for Diabetes, Heart Disease, and Stroke prediction
2. WHEN a doctor requests risk prediction, THE Risk_Predictor SHALL calculate risk scores as probabilities between 0.00 and 1.00 for all three diseases (Diabetes, Heart Disease, Stroke)
3. WHEN risk scores are calculated, THE Risk_Predictor SHALL classify risk into categories using thresholds: Low (0.00-0.33), Moderate (0.34-0.66), High (0.67-1.00)
4. WHEN predictions are calculated, THE CDSS SHALL store prediction results in the PostgreSQL database linked to the patient record
5. WHEN predictions are stored, THE CDSS SHALL timestamp the prediction with the current date and time
6. WHEN predictions are completed, THE CDSS SHALL display risk scores and risk categories to the doctor
7. IF required patient features are missing, THEN THE CDSS SHALL display an error message indicating which features are required for prediction
8. IF a prediction computation fails for any disease, THEN THE CDSS SHALL store predictions for successfully computed diseases and display an error message indicating which disease predictions failed
9. WHEN a prediction error occurs, THE CDSS SHALL indicate to the doctor which disease predictions are unavailable

### Requirement 5: Explainable AI for Predictions

**User Story:** As a doctor, I want to understand why the system made a particular prediction, so that I can trust and validate the AI recommendations.

#### Acceptance Criteria

1. WHEN a risk prediction is generated, THE SHAP_Explainer SHALL generate feature importance explanations for all input features used in that prediction
2. WHEN a risk prediction is generated, THE SHAP_Explainer SHALL identify the top 10 patient features with highest absolute SHAP values as primary contributors to the prediction
3. WHEN SHAP explanations are generated, THE CDSS SHALL store all SHAP explanation values in the PostgreSQL database linked to the prediction
4. WHEN a doctor views a risk prediction, THE CDSS SHALL display SHAP explanations showing the feature name, the SHAP contribution value with 4 decimal places, and a direction indicator for each feature
5. WHEN SHAP explanations are displayed, THE CDSS SHALL indicate whether each feature increased risk (positive SHAP value), decreased risk (negative SHAP value), or had negligible impact (absolute SHAP value less than 0.0001)
6. IF SHAP explanation generation fails, THEN THE CDSS SHALL store the risk prediction without explanations and display an error message indicating that explanations are unavailable for this prediction

### Requirement 6: Medical Knowledge Document Ingestion

**User Story:** As a system administrator, I want to load medical guidelines into the system, so that the RAG system can retrieve relevant clinical knowledge.

#### Acceptance Criteria

1. THE RAG_System SHALL load medical guideline documents from the file system (PDF or TXT formats)
2. THE RAG_System SHALL split documents into chunks for processing
3. THE RAG_System SHALL generate embeddings using OpenAI Embeddings
4. THE RAG_System SHALL store embeddings in the FAISS_Index
5. THE RAG_System SHALL preserve document metadata including source information

### Requirement 7: Medical Knowledge Retrieval

**User Story:** As a doctor, I want the system to retrieve relevant clinical guidelines, so that my decisions are based on evidence-based medicine.

#### Acceptance Criteria

1. WHEN a clinical query is submitted, THE RAG_System SHALL perform similarity search on the FAISS_Index
2. THE RAG_System SHALL return the top 5 most relevant Clinical_Guideline excerpts
3. THE RAG_System SHALL include source metadata with retrieved guidelines
4. THE CDSS SHALL display retrieved guidelines to the doctor

### Requirement 8: AI Agent Tool Architecture

**User Story:** As a system, I want the AI Agent to use structured tools instead of generating direct answers, so that recommendations are grounded in actual patient data and medical knowledge.

#### Acceptance Criteria

1. THE AI_Agent SHALL be implemented using LangChain with simple tool-calling capabilities
2. THE AI_Agent SHALL have access to exactly three tools: Patient_Data_Tool, Prediction_Tool, and Knowledge_Tool
3. THE AI_Agent SHALL call at least one tool before generating recommendations
4. THE CDSS SHALL log which tools were called for each recommendation

### Requirement 9: Patient Data Tool

**User Story:** As an AI Agent, I want to retrieve patient demographic and medical data, so that I can provide personalized clinical recommendations.

#### Acceptance Criteria

1. WHEN the Patient_Data_Tool is invoked with a patient identifier, THE Patient_Data_Tool SHALL retrieve patient demographics from the database using Django ORM
2. THE Patient_Data_Tool SHALL retrieve medical history associated with the patient
3. THE Patient_Data_Tool SHALL retrieve laboratory report data associated with the patient
4. THE Patient_Data_Tool SHALL return structured data to the AI_Agent in JSON format
5. IF the patient identifier is invalid or the patient does not exist, THEN THE Patient_Data_Tool SHALL return an error message

### Requirement 10: Prediction Tool

**User Story:** As an AI Agent, I want to retrieve risk predictions and explanations, so that I can incorporate risk assessment into clinical recommendations.

#### Acceptance Criteria

1. WHEN the Prediction_Tool is invoked with a patient identifier, THE Prediction_Tool SHALL retrieve the most recent risk prediction for that patient using Django ORM
2. THE Prediction_Tool SHALL retrieve Risk_Score values for all predicted diseases
3. THE Prediction_Tool SHALL retrieve Risk_Category classifications
4. THE Prediction_Tool SHALL retrieve SHAP explanation values
5. THE Prediction_Tool SHALL return structured data to the AI_Agent in JSON format
6. IF no predictions exist for the patient, THEN THE Prediction_Tool SHALL return a message indicating predictions are unavailable

### Requirement 11: Knowledge Tool

**User Story:** As an AI Agent, I want to retrieve relevant medical guidelines, so that I can generate evidence-based recommendations.

#### Acceptance Criteria

1. WHEN the Knowledge_Tool is invoked with a clinical query, THE Knowledge_Tool SHALL call the RAG_System to retrieve relevant guidelines
2. THE Knowledge_Tool SHALL return the top 5 most relevant Clinical_Guideline excerpts with source citations
3. THE Knowledge_Tool SHALL return structured data to the AI_Agent in JSON format
4. IF no relevant guidelines are found, THEN THE Knowledge_Tool SHALL return a message indicating no guidelines were retrieved

### Requirement 12: AI Clinical Recommendation Generation

**User Story:** As a doctor, I want AI-generated clinical recommendations based on patient data and medical evidence, so that I have decision support for patient care.

#### Acceptance Criteria

1. WHEN a doctor requests AI recommendations, THE AI_Agent SHALL call the Patient_Data_Tool to retrieve patient information
2. THE AI_Agent SHALL call the Prediction_Tool to retrieve risk assessments and explanations
3. THE AI_Agent SHALL call the Knowledge_Tool to retrieve relevant clinical guidelines
4. THE AI_Agent SHALL generate a clinical summary based on retrieved data
5. THE AI_Agent SHALL generate a risk explanation interpreting the SHAP values
6. THE AI_Agent SHALL generate evidence-based recommendations citing retrieved guidelines
7. THE AI_Agent SHALL suggest next best actions for the doctor
8. THE CDSS SHALL display the generated recommendations to the doctor
9. THE CDSS SHALL clearly indicate that final clinical decisions remain with the doctor

### Requirement 13: Interactive AI Consultation

**User Story:** As a doctor, I want to ask follow-up questions to the AI Agent, so that I can explore specific clinical concerns in depth.

#### Acceptance Criteria

1. THE CDSS SHALL allow doctors to submit follow-up questions after initial recommendations
2. WHEN a follow-up question is submitted, THE AI_Agent SHALL call relevant tools based on the question context
3. THE AI_Agent SHALL maintain simple conversation context for follow-up questions
4. THE CDSS SHALL display follow-up responses to the doctor

### Requirement 14: Prediction Result Persistence

**User Story:** As a doctor, I want prediction results stored permanently, so that I can track patient risk over time.

#### Acceptance Criteria

1. WHEN a risk prediction is generated, THE CDSS SHALL store the prediction results in the PostgreSQL database using Django ORM
2. THE CDSS SHALL automatically timestamp predictions using Django's auto_now_add field
3. THE CDSS SHALL link predictions to patients using foreign keys
4. THE CDSS SHALL allow retrieval of historical predictions for a patient

### Requirement 15: Model Loading and Management

**User Story:** As a system, I want to load pre-trained ML models at startup, so that predictions can be generated efficiently without repeated loading.

#### Acceptance Criteria

1. THE CDSS SHALL load XGBoost models from the file system using Joblib during initialization
2. THE CDSS SHALL load Diabetes prediction model
3. THE CDSS SHALL load Heart Disease prediction model
4. THE CDSS SHALL load Stroke prediction model
5. IF a model file is missing or corrupted, THEN THE CDSS SHALL log an error and disable the corresponding prediction feature
6. THE CDSS SHALL keep loaded models in memory for the duration of the application runtime

### Requirement 16: FAISS Index Management

**User Story:** As a system, I want to load the FAISS index at startup, so that medical knowledge retrieval is efficient.

#### Acceptance Criteria

1. THE RAG_System SHALL load the FAISS_Index from the file system during initialization
2. THE RAG_System SHALL keep the FAISS_Index in memory for the duration of the application runtime
3. IF the FAISS_Index file is missing or corrupted, THEN THE RAG_System SHALL log an error and disable knowledge retrieval
4. THE RAG_System SHALL support index updates without requiring system restart

### Requirement 17: API Endpoint Design

**User Story:** As a frontend developer, I want simple and focused API endpoints built with Django REST Framework, so that I can easily integrate the backend with the React frontend.

#### Acceptance Criteria

1. THE CDSS SHALL provide Django REST Framework API endpoints for doctor authentication
2. THE CDSS SHALL provide REST API endpoints for patient CRUD operations
3. THE CDSS SHALL provide a REST API endpoint for medical history storage
4. THE CDSS SHALL provide a REST API endpoint for risk prediction
5. THE CDSS SHALL provide a REST API endpoint for AI recommendation generation
6. THE CDSS SHALL provide a REST API endpoint for follow-up questions
7. ALL API endpoints SHALL return responses in JSON format using Django REST Framework serializers

### Requirement 18: Database Schema Design

**User Story:** As a system, I want a clear database schema using Django Models, so that data integrity is maintained.

#### Acceptance Criteria

1. THE CDSS SHALL use Django's built-in User model or extend it for doctor authentication
2. THE CDSS SHALL define Django Models for Patient, MedicalHistory, LabReport, Prediction, and SHAPExplanation
3. THE CDSS SHALL use Django ORM foreign keys to link related data
4. THE CDSS SHALL use Django's automatic timestamp fields (auto_now_add, auto_now) where appropriate

### Requirement 19: Frontend User Workflow

**User Story:** As a doctor, I want a clear step-by-step workflow in the UI, so that I can easily navigate through patient assessment and AI consultation.

#### Acceptance Criteria

1. THE CDSS SHALL provide a login page as the entry point
2. WHEN logged in, THE CDSS SHALL display a patient management interface
3. THE CDSS SHALL provide a patient registration form
4. THE CDSS SHALL provide a medical history input form
5. THE CDSS SHALL provide a risk prediction button that triggers the Risk_Predictor
6. WHEN predictions are displayed, THE CDSS SHALL provide an AI recommendation button
7. WHEN AI recommendations are displayed, THE CDSS SHALL provide an input field for follow-up questions
8. THE CDSS SHALL guide doctors through the workflow: Login → Patient Management → Data Entry → Prediction → AI Consultation

### Requirement 20: Error Handling and User Feedback

**User Story:** As a doctor, I want clear error messages and feedback, so that I understand what went wrong and how to proceed.

#### Acceptance Criteria

1. WHEN an error occurs, THE CDSS SHALL display a user-friendly error message
2. THE CDSS SHALL log technical error details for debugging
3. IF a prediction fails, THEN THE CDSS SHALL explain why and suggest corrective actions
4. IF the AI_Agent fails to generate recommendations, THEN THE CDSS SHALL display an error and allow retry
5. THE CDSS SHALL provide loading indicators during operations that take more than 1 second
6. WHEN an operation succeeds, THE CDSS SHALL display a success confirmation message

### Requirement 21: Code Simplicity and Readability

**User Story:** As a student presenting this project, I want simple and readable code, so that I can easily explain the implementation to evaluators.

#### Acceptance Criteria

1. THE CDSS SHALL use descriptive variable and function names without abbreviations
2. THE CDSS SHALL organize code into modules corresponding to the four project modules
3. THE CDSS SHALL limit function length to focus on single responsibilities
4. THE CDSS SHALL avoid complex abstractions, design patterns, and nested structures
5. THE CDSS SHALL use minimal comments explaining what the code does (code should be self-explanatory)
6. THE CDSS SHALL maintain a clean folder structure with only necessary files
7. THE CDSS SHALL avoid premature optimization and complex async patterns

### Requirement 22: Module Independence

**User Story:** As a developer, I want each module to be independently functional, so that I can build and test one module at a time.

#### Acceptance Criteria

1. THE CDSS SHALL implement Module 1 (Patient Management) without dependencies on AI or ML components
2. THE CDSS SHALL implement Module 2 (Risk Prediction) without dependencies on RAG or AI Agent
3. THE CDSS SHALL implement Module 3 (RAG) without dependencies on the AI Agent
4. THE CDSS SHALL implement Module 4 (AI Agent) using tools that integrate with previous modules
5. WHEN a module is completed, THE CDSS SHALL allow testing that module independently

### Requirement 23: Clinical Decision Responsibility

**User Story:** As a doctor, I want clear indication that AI recommendations are advisory only, so that I understand the final clinical decision is mine.

#### Acceptance Criteria

1. THE CDSS SHALL display a disclaimer that the doctor retains final decision-making authority
2. THE CDSS SHALL label AI-generated content as "AI Recommendation" or "AI-Generated"
3. THE CDSS SHALL NOT use language implying the AI makes final decisions
4. THE CDSS SHALL present recommendations as suggestions requiring doctor validation
5. THE CDSS SHALL include the disclaimer on all AI recommendation screens

### Requirement 24: Academic Project Documentation

**User Story:** As a student, I want clear documentation of system architecture and data flow, so that I can present the project effectively.

#### Acceptance Criteria

1. THE CDSS SHALL include a README documenting system architecture
2. THE CDSS SHALL include documentation of the four module structure
3. THE CDSS SHALL include documentation of the technology stack
4. THE CDSS SHALL include documentation of the user workflow
5. THE CDSS SHALL include documentation of API endpoints
6. THE CDSS SHALL include documentation explaining the AI Agent tool-calling mechanism
