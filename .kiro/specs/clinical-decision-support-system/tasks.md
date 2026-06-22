# Implementation Plan: Clinical Decision Support System

## Overview

**IMPORTANT: This is a Final Year Engineering Project**

This implementation follows a **strict module-by-module approach** with **mandatory STOP checkpoints**. Do NOT proceed to the next module without explicit approval.

**Technology Stack:**
- Backend: **Django + Django REST Framework** (NOT Flask)
- Frontend: React
- Database: PostgreSQL with Django ORM
- ML: XGBoost, SHAP, Joblib
- AI: LangChain (simple), OpenAI/Claude
- RAG: ChromaDB, OpenAI Embeddings

**Development Principles:**
- Use Django built-ins (authentication, ORM, sessions) - NO custom implementations
- Keep code simple and readable - NO unnecessary abstractions
- Build one module at a time with STOP checkpoints
- Focus on functionality, NOT test coverage or optimization
- Avoid: account lockout, retry frameworks, connection pooling, property-based testing, complex error handling

## Module Development Order

**Build in this exact order with STOP checkpoints:**

1. **Module 1: Patient Management** → STOP and wait for approval
2. **Module 2: Risk Prediction** → STOP and wait for approval  
3. **Module 3: RAG System** → STOP and wait for approval
4. **Module 4: AI Agent** → STOP and wait for approval
5. **Integration & Frontend** → Complete

## Tasks

### ✅ CHECKPOINT 0: Project Setup

- [x] 1. Initialize Django project and configure PostgreSQL
  - Create Django project: `django-admin startproject cdss_backend`
  - Create Django app: `python manage.py startapp patient_management`
  - Install dependencies: Django, djangorestframework, psycopg2-binary
  - Configure PostgreSQL connection in settings.py
  - Run initial migrations: `python manage.py migrate`
  - Create superuser for Django admin: `python manage.py createsuperuser`
  - Verify Django admin works at http://localhost:8000/admin
  - _Requirements: 18.1, 18.2, 21.6_

---

### 🏥 MODULE 1: Patient Management (Django-based CRUD)

**Goal**: Build complete patient management using Django built-ins. NO AI, NO ML, NO RAG.

- [x] 2. Create Django models for patients and medical data
  - Define Patient model with fields: name, date_of_birth, gender, phone, email, created_at (auto_now_add)
  - Define MedicalHistory model with FK to Patient: diagnoses, medications, allergies, notes, timestamp (auto_now_add)
  - Define LabReport model with FK to Patient: lab_data (JSONField), timestamp (auto_now_add)
  - Run makemigrations and migrate
  - Register models in Django admin
  - Test CRUD operations in Django admin interface
  - _Requirements: 2.1, 2.3, 3.3, 3.4, 18.2, 18.3, 18.4_

- [x] 3. Implement Django authentication for doctors
  - Use Django's built-in User model for doctors (or extend it)
  - Configure Django REST Framework authentication (SessionAuthentication, TokenAuthentication)
  - Create login endpoint using Django's built-in authenticate()
  - Create logout endpoint
  - Test authentication flow: login → get token → access protected endpoint → logout
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 18.1_

- [x] 4. Create Django REST Framework serializers and viewsets
  - Create PatientSerializer with all fields
  - Create MedicalHistorySerializer with patient FK
  - Create LabReportSerializer with patient FK
  - Create PatientViewSet with all CRUD operations
  - Create MedicalHistoryViewSet with list/create/retrieve operations
  - Create LabReportViewSet with list/create/retrieve operations
  - Register viewsets with Django REST Framework router
  - _Requirements: 2.1-2.7, 3.1-3.8, 17.2, 17.3_

- [x] 5. Test Module 1 API endpoints
  - POST /api/patients/ - Create patient (test with missing required fields)
  - GET /api/patients/ - List patients
  - GET /api/patients/{id}/ - Get patient details
  - PUT /api/patients/{id}/ - Update patient
  - POST /api/patients/{id}/history/ - Add medical history
  - GET /api/patients/{id}/history/ - Get medical history
  - POST /api/patients/{id}/labs/ - Add lab report
  - GET /api/patients/{id}/labs/ - Get lab reports
  - Verify Django ORM foreign key constraints work
  - Verify auto_now_add timestamps are created
  - _Requirements: All Module 1 requirements_

---

### ✋ CHECKPOINT 1: Module 1 Complete - STOP HERE

**Before proceeding to Module 2:**
- ✅ All Module 1 endpoints working
- ✅ Django authentication working
- ✅ Django admin shows all models
- ✅ Can create/read/update patients
- ✅ Can add medical history and lab reports
- ✅ Foreign keys enforced by Django ORM

**DO NOT PROCEED TO MODULE 2 WITHOUT APPROVAL**

---

### 🧠 MODULE 2: Risk Prediction (XGBoost + SHAP)

**Goal**: Load ML models, generate predictions, store results. NO RAG, NO AI Agent yet.

- [x] 6. Create Django models for predictions
  - Define Prediction model with FK to Patient: disease_type, risk_score, risk_category, timestamp (auto_now_add)
  - Define SHAPExplanation model with FK to Prediction: feature_name, shap_value, direction
  - Run makemigrations and migrate
  - Register models in Django admin
  - _Requirements: 18.5, 18.6, 14.1, 14.2_

- [x] 7. Implement simple ML model loading
  - Create `ml_models/` directory in Django app
  - Create ModelLoader class with load_models() method
  - Load diabetes_model.pkl, heart_model.pkl, stroke_model.pkl using joblib
  - Return None for missing models (graceful handling)
  - Load models once at Django app startup (in apps.py ready() method)
  - Store loaded models in memory as class variables
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [x] 8. Implement risk prediction service
  - Create simple categorize_risk(score) function: Low (<0.34), Moderate (0.34-0.67), High (>=0.67)
  - Create RiskPredictor class with predict_risk(feature_dict) method
  - Extract features from lab_data JSON field
  - For each loaded model, call model.predict_proba() to get risk score
  - Categorize risk using categorize_risk()
  - Return dict: {disease: {risk_score, risk_category}}
  - _Requirements: 4.1, 4.2, 4.3, 4.6_

- [x] 9. Implement SHAP explanation generator
  - Create SHAPExplainer class with explain_prediction(model, features) method
  - Use shap.TreeExplainer to generate SHAP values
  - Sort features by absolute SHAP value (descending)
  - Return top 10 features with shap_value and direction (increases_risk/decreases_risk)
  - _Requirements: 5.1, 5.2, 5.4, 5.5_

- [x] 10. Create prediction API endpoint
  - Create PredictionViewSet or APIView
  - POST /api/patients/{id}/predict/ endpoint
  - Get patient's latest lab report
  - Call RiskPredictor.predict_risk()
  - Call SHAPExplainer.explain_prediction() for each disease
  - Save Prediction and SHAPExplanation objects using Django ORM
  - Return prediction results as JSON
  - Handle missing lab data error
  - Handle missing models gracefully (skip that disease)
  - _Requirements: 4.1-4.9, 5.1-5.6, 14.1-14.4, 17.4_

- [x] 11. Test Module 2 predictions
  - Create test patient with lab data
  - POST /api/patients/{id}/predict/
  - Verify Prediction records created in database
  - Verify SHAPExplanation records linked to predictions
  - Verify risk scores between 0.00-1.00
  - Verify risk categories correct (Low/Moderate/High)
  - Verify SHAP values sorted by absolute value
  - Test with missing lab data → verify error message
  - _Requirements: All Module 2 requirements, Property 2, Property 3, Property 4_

---

### ✋ CHECKPOINT 2: Module 2 Complete - STOP HERE

**Before proceeding to Module 3:**
- ✅ XGBoost models load successfully
- ✅ Predictions generate risk scores and categories
- ✅ SHAP explanations generate and save
- ✅ Prediction results stored in database
- ✅ Can view predictions in Django admin

**DO NOT PROCEED TO MODULE 3 WITHOUT APPROVAL**

---

### 📚 MODULE 3: RAG System (ChromaDB + OpenAI Embeddings)

**Goal**: Load medical documents, create ChromaDB collection, implement retrieval. NO AI Agent yet.

- [x] 12. Create sample medical guidelines and document processing
  - Create `data/guidelines/` directory in project root
  - Create 3-5 sample medical guideline TXT files (diabetes, heart disease, hypertension management)
  - Each file: 300-500 words of realistic clinical content
  - Create `rag/` directory in Django project
  - Create DocumentLoader class: load_documents(directory) - supports TXT files
  - Create DocumentChunker class: chunk_documents(docs) - simple character-based chunking (~500 chars)
  - Keep it simple - just split text into chunks with metadata
  - _Requirements: 6.1, 6.2_

- [x] 13. Implement ChromaDB vector store
  - Create VectorStore class using chromadb library
  - initialize_collection(collection_name) - create/get ChromaDB collection
  - Use OpenAI embeddings (text-embedding-ada-002) - ChromaDB handles this automatically
  - add_documents(chunks, metadata) - add documents to collection
  - Keep it simple - use default ChromaDB settings
  - _Requirements: 6.3, 6.4_

- [x] 14. Create RAG retriever
  - Create RAGRetriever class
  - retrieve(query, top_k=5) method
  - Use ChromaDB's query method to find similar documents
  - Return top 5 chunks with metadata (source_filename, text)
  - Handle empty results gracefully
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 15. Create offline RAG setup script
  - Create management command: `python manage.py build_rag_index`
  - Load sample guidelines from data/guidelines/ directory
  - Chunk documents
  - Initialize ChromaDB collection
  - Add documents to ChromaDB (embeddings generated automatically)
  - Print progress and statistics (files loaded, chunks created)
  - Run this script once to test
  - _Requirements: 6.1-6.5, 16.1_

- [x] 16. Create RAG API endpoint
  - POST /api/rag/query/ endpoint
  - Accept clinical query in request body
  - Call RAGRetriever.retrieve(query)
  - Return top 5 guidelines as JSON
  - Test with sample queries: "diabetes management", "hypertension treatment", "heart disease prevention"
  - _Requirements: 7.1-7.4, 17.6_

- [x] 17. Test Module 3 RAG system
  - Run build_rag_index command
  - Verify ChromaDB collection created
  - Test POST /api/rag/query/ with 3-5 different queries
  - Verify relevant chunks returned
  - Verify metadata includes source filename
  - Check retrieval relevance (diabetes query → diabetes guidelines)
  - _Requirements: All Module 3 requirements_

---

### ✋ CHECKPOINT 3: Module 3 Complete - STOP HERE

**Before proceeding to Module 4:**
- ✅ Sample guidelines created
- ✅ Documents load and chunk correctly
- ✅ ChromaDB collection builds successfully
- ✅ RAG retrieval returns relevant chunks
- ✅ Test queries return top 5 results with correct source files

**DO NOT PROCEED TO MODULE 4 WITHOUT APPROVAL**

---

### 🤖 MODULE 4: AI Agent (Simple LangChain + 3 Tools)

**Goal**: Create 3 simple tools, implement LangChain agent, generate recommendations.

- [x] 18. Create three simple LangChain tools
  - Create `agent/tools.py` file
  - **PatientDataTool**: Query Django ORM for Patient, MedicalHistory, LabReport → return JSON
  - **PredictionTool**: Query Django ORM for latest Prediction + SHAPExplanations → return JSON
  - **KnowledgeTool**: Call RAGRetriever.retrieve(query) → return top 5 guidelines as JSON
  - Use LangChain's @tool decorator or Tool class
  - Keep tool implementations simple - just database queries
  - _Requirements: 8.1, 8.2, 9.1-9.5, 10.1-10.6, 11.1-11.4_

- [x] 19. Implement simple LangChain agent
  - Create `agent/clinical_agent.py` file
  - Use create_openai_functions_agent() from LangChain
  - Create simple prompt: "You are a clinical assistant. Use tools to get data. Generate: Summary, Risk Assessment, Recommendations."
  - Initialize agent with OpenAI LLM (gpt-4 or gpt-3.5-turbo)
  - Pass the 3 tools to agent
  - Keep prompt simple - no complex instructions
  - _Requirements: 8.1-8.4, 12.1-12.9_

- [x] 20. Create recommendation API endpoint
  - POST /api/patients/{id}/recommend/ endpoint
  - Get patient_id from URL
  - Call agent with: "Provide clinical recommendations for patient {id}"
  - Agent automatically calls the 3 tools
  - Return agent's response as JSON
  - Add disclaimer: "AI recommendations are advisory. Doctor makes final decisions."
  - **BUG FIXED**: Replaced custom agent loop with proper LangChain tool calling implementation
  - _Requirements: 12.1-12.9, 17.5, 23.1-23.5_

- [ ] 21. Implement simple follow-up questions (optional)
  - POST /api/patients/{id}/followup/ endpoint
  - Accept question in request body
  - Maintain simple conversation context (last few messages)
  - Call agent with question
  - Return response
  - Keep context management simple - no complex memory systems
  - _Requirements: 13.1-13.4, 17.6_

- [ ] 22. Test Module 4 AI Agent
  - Create test patient with predictions
  - POST /api/patients/{id}/recommend/
  - Verify agent calls all 3 tools (check logs)
  - Verify response includes patient summary, risk assessment, recommendations
  - Verify disclaimer present
  - Test follow-up question (if implemented)
  - _Requirements: All Module 4 requirements, Property 6_

---

### ✋ CHECKPOINT 4: Module 4 Complete - STOP HERE

**Before proceeding to frontend:**
- ✅ 3 tools implemented and working
- ✅ LangChain agent calls tools correctly
- ✅ Recommendations generate successfully
- ✅ Response includes disclaimer

**DO NOT PROCEED TO FRONTEND WITHOUT APPROVAL**

---

### 🎨 MODULE 5: React Frontend (Simple UI)

**Goal**: Build simple React UI for the complete workflow. One screen at a time.

- [ ] 23. Setup React project
  - Create React app: `npx create-react-app cdss-frontend`
  - Install axios for API calls
  - Install react-router-dom for routing
  - Configure proxy to Django backend
  - _Requirements: 19.1, 21.2_

- [ ] 24. Create login page
  - Simple login form with username and password
  - Call POST /api/auth/login/
  - Store auth token in localStorage
  - Redirect to patient list on success
  - Display error message on failure
  - _Requirements: 1.1-1.5, 19.1_

- [ ] 25. Create patient list and registration
  - Patient list page showing all patients
  - "Add Patient" button → patient registration form
  - Form fields: name, date of birth, gender, phone, email
  - Call POST /api/patients/ to create
  - Call GET /api/patients/ to list
  - Click patient → navigate to patient detail page
  - _Requirements: 2.1-2.7, 19.2, 19.3_

- [ ] 26. Create patient detail page with medical data entry
  - Show patient demographics
  - Medical history form: diagnoses, medications, allergies, notes
  - Lab report form: structured fields for lab values
  - "Save" buttons call POST /api/patients/{id}/history/ and /api/patients/{id}/labs/
  - Display success/error messages
  - _Requirements: 3.1-3.8, 19.4, 19.5_

- [ ] 27. Create prediction view
  - "Run Prediction" button on patient detail page
  - Call POST /api/patients/{id}/predict/
  - Display loading indicator
  - Show risk scores and categories for each disease
  - Show SHAP explanations (feature name, value, direction)
  - Color-code risk levels: Low (green), Moderate (yellow), High (red)
  - _Requirements: 4.6, 5.4, 5.5, 19.6_

- [ ] 28. Create AI recommendation view
  - "Get AI Recommendations" button (appears after predictions)
  - Call POST /api/patients/{id}/recommend/
  - Display loading indicator (may take 10-30 seconds)
  - Show AI-generated recommendations
  - Display disclaimer prominently
  - Add follow-up question input field (optional)
  - _Requirements: 12.8, 12.9, 19.7, 23.2, 23.5_

- [ ] 29. Test complete user workflow
  - Login as doctor
  - Create new patient
  - Add medical history and lab reports
  - Run prediction → verify results display
  - Get AI recommendation → verify response shows
  - Test follow-up question (if implemented)
  - Verify workflow: Login → Register Patient → Add Data → Predict → Recommend
  - _Requirements: 19.1-19.8, All workflow requirements_

---

### ✋ CHECKPOINT 5: Frontend Complete - STOP HERE

**Before finalizing:**
- ✅ Can login and see patient list
- ✅ Can create patients and add medical data
- ✅ Can run predictions and see results
- ✅ Can get AI recommendations
- ✅ Complete workflow works end-to-end

---

### 📝 MODULE 6: Documentation and Final Testing

- [ ] 30. Create comprehensive README
  - Project overview and architecture diagram
  - Technology stack explanation
  - Module-by-module breakdown
  - Installation instructions: Django setup, PostgreSQL, React frontend
  - How to run RAG setup script
  - API endpoints documentation
  - Screenshots of each screen
  - Explanation of AI Agent tool-calling mechanism
  - _Requirements: 24.1-24.6_

- [ ] 31. Final system testing
  - Test complete workflow multiple times
  - Test error cases: missing data, failed predictions, etc.
  - Verify all Django models visible in admin
  - Verify data persists correctly
  - Check for any obvious bugs
  - _Requirements: All requirements_

---

### 🎉 PROJECT COMPLETE

**Deliverables:**
- ✅ Django backend with 4 working modules
- ✅ React frontend with complete workflow
- ✅ PostgreSQL database with all data
- ✅ XGBoost models generating predictions
- ✅ SHAP explanations for interpretability
- ✅ RAG system with ChromaDB retrieving medical guidelines
- ✅ AI Agent providing clinical recommendations
- ✅ Comprehensive documentation

**Ready for:**
- Academic presentation
- Project demonstration
- Viva/interview explanations
- Portfolio showcase

## Notes

- **Mandatory Checkpoints**: Do NOT skip checkpoint approvals
- **Django First**: Always use Django built-ins before creating custom solutions
- **Simple Code**: Every function should be easy to explain during viva
- **No Optimization**: Focus on working functionality, not performance
- **Test As You Go**: Manually test each feature before moving on
- **Ask Questions**: Stop and ask if anything is unclear

## Dependencies

```txt
# Backend (requirements.txt)
Django>=4.2
djangorestframework>=3.14
psycopg2-binary>=2.9
xgboost>=1.7
shap>=0.41
joblib>=1.2
langchain>=0.1
openai>=1.0
chromadb>=0.4
PyPDF2>=3.0
numpy>=1.24
pandas>=2.0

# Frontend (package.json dependencies)
react
react-router-dom
axios
```


## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2"] },
    { "id": 2, "tasks": ["3"] },
    { "id": 3, "tasks": ["4"] },
    { "id": 4, "tasks": ["5"] },
    { "id": 5, "tasks": ["6"] },
    { "id": 6, "tasks": ["7"] },
    { "id": 7, "tasks": ["8"] },
    { "id": 8, "tasks": ["9"] },
    { "id": 9, "tasks": ["10"] },
    { "id": 10, "tasks": ["11"] },
    { "id": 11, "tasks": ["12"] },
    { "id": 12, "tasks": ["13"] },
    { "id": 13, "tasks": ["14"] },
    { "id": 14, "tasks": ["15"] },
    { "id": 15, "tasks": ["16"] },
    { "id": 16, "tasks": ["17"] },
    { "id": 17, "tasks": ["18"] },
    { "id": 18, "tasks": ["19"] },
    { "id": 19, "tasks": ["20"] },
    { "id": 20, "tasks": ["21"] },
    { "id": 21, "tasks": ["22"] },
    { "id": 22, "tasks": ["23"] },
    { "id": 23, "tasks": ["24"] },
    { "id": 24, "tasks": ["25"] },
    { "id": 25, "tasks": ["26"] },
    { "id": 26, "tasks": ["27"] },
    { "id": 27, "tasks": ["28"] },
    { "id": 28, "tasks": ["29"] },
    { "id": 29, "tasks": ["30"] },
    { "id": 30, "tasks": ["31"] }
  ]
}
```
