# Module 1: Patient Management - Complete Viva Guide

## Table of Contents
1. [Module Overview](#module-overview)
2. [Database Models Explanation](#database-models)
3. [Serializers Explanation](#serializers)
4. [Views and ViewSets](#views-and-viewsets)
5. [URL Routing](#url-routing)
6. [Authentication System](#authentication-system)
7. [Complete API Flow](#complete-api-flow)
8. [Testing Strategy](#testing-strategy)
9. [Viva Questions & Answers](#viva-questions-answers)

---

## Module Overview

**Module Name**: Patient Management (Module 1)  
**Purpose**: Build a complete patient data management system for doctors  
**Technologies Used**:
- **Django**: Web framework (Python)
- **Django REST Framework (DRF)**: For building REST APIs
- **PostgreSQL**: Relational database
- **Token Authentication**: Secure API access

**Key Features**:
1. Doctor authentication (login/logout)
2. Patient CRUD operations (Create, Read, Update, Delete)
3. Medical history storage
4. Lab report storage with JSON data
5. RESTful API endpoints

**Why This Module First?**  
Before implementing AI and ML features, we need a solid foundation to:
- Store patient information
- Manage medical records
- Provide secure access to doctors
- Create APIs that the frontend (React) will consume

---

## Database Models

### File: `patient_management/models.py`

This file defines **three database tables** using Django ORM.


### 1. Patient Model

```python
class Patient(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**Purpose**: Store basic patient demographic information.

**Field Explanations**:
- `name`: Patient's full name (max 100 characters)
- `date_of_birth`: Birth date for age calculation
- `gender`: Gender identification
- `phone`: Contact number
- `email`: Email address (Django validates email format)
- `created_at`: **Auto-generated timestamp** when patient is registered

**Why `auto_now_add=True`?**  
Django automatically sets this field to the current date/time when creating a new record. The doctor doesn't need to provide this—it's handled by the database.

**Magic Methods**:
```python
def __str__(self):
    return f"{self.name} (DOB: {self.date_of_birth})"
```
This makes the Django admin show "John Doe (DOB: 1990-01-01)" instead of "Patient object (1)".


**Meta Class**:
```python
class Meta:
    ordering = ['-created_at']
```
Orders patients by newest first (the `-` means descending order).

---

### 2. MedicalHistory Model

```python
class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnoses = models.TextField()
    medications = models.TextField()
    allergies = models.TextField()
    notes = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

**Purpose**: Store a patient's medical history over time. One patient can have multiple history records.

**Field Explanations**:
- `patient`: **Foreign Key** linking to Patient table
- `diagnoses`: Current and past diagnoses (e.g., "Hypertension, Type 2 Diabetes")
- `medications`: Current medications (e.g., "Metformin 500mg, Lisinopril 10mg")
- `allergies`: Known allergies (e.g., "Penicillin")
- `notes`: Additional doctor notes
- `timestamp`: When this history was recorded


**Foreign Key Relationship**:
```python
patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
```

**What is a Foreign Key?**  
A foreign key creates a relationship between two tables. Here, `MedicalHistory` is linked to `Patient`.

**What does `on_delete=models.CASCADE` mean?**  
If a patient is deleted, all their medical history records are **automatically deleted** too. This prevents orphaned records.

**Example**:
- Patient ID 1: John Doe
  - Medical History Record 1: "Hypertension diagnosed on 2023-01-15"
  - Medical History Record 2: "Diabetes diagnosed on 2023-06-20"

If John Doe is deleted, both history records are also deleted automatically.

---

### 3. LabReport Model

```python
class LabReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    lab_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

**Purpose**: Store laboratory test results for patients.


**Why JSONField?**  
Different lab tests have different parameters:
- Blood glucose test: `{"glucose": 120}`
- Complete blood count: `{"wbc": 7000, "rbc": 5.2, "hemoglobin": 14.5}`
- Lipid panel: `{"cholesterol": 190, "hdl": 50, "ldl": 120, "triglycerides": 150}`

Instead of creating separate columns for every possible lab value, we use **JSONField** to store flexible, structured data.

**Example Lab Report**:
```json
{
  "glucose": 145,
  "hba1c": 7.2,
  "cholesterol": 210,
  "blood_pressure": "140/90",
  "test_date": "2024-01-15"
}
```

**Benefits**:
- Can store any lab test without changing the database schema
- Easy to add new test types
- Keeps the model simple

---

## Serializers

### File: `patient_management/serializers.py`

**What is a Serializer?**  
A serializer converts data between:
- **Python objects** (Django models) ↔ **JSON** (for API responses)


**Why do we need serializers?**  
- The frontend (React) sends JSON data
- Django models work with Python objects
- Serializers handle the conversion automatically

### 1. PatientSerializer

```python
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'date_of_birth', 'gender', 'phone', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
```

**Explanation**:
- `model = Patient`: This serializer works with the Patient model
- `fields = [...]`: These fields are included in the JSON response
- `read_only_fields = ['id', 'created_at']`: These fields cannot be set by the user (Django generates them)

**Example JSON Output**:
```json
{
  "id": 1,
  "name": "John Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male",
  "phone": "555-0101",
  "email": "john.doe@example.com",
  "created_at": "2024-01-20T10:30:00Z"
}
```


### 2. MedicalHistorySerializer

```python
class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = ['id', 'patient', 'diagnoses', 'medications', 'allergies', 'notes', 'timestamp']
        read_only_fields = ['id', 'timestamp']
```

**Key Point**: The `patient` field expects a **patient ID** (e.g., `"patient": 1`), not the full patient object.

### 3. LabReportSerializer

```python
class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = ['id', 'patient', 'lab_data', 'timestamp']
        read_only_fields = ['id', 'timestamp']
```

**Key Point**: The `lab_data` field automatically handles JSON validation. Django ensures the data is valid JSON before saving.

---

## Views and ViewSets

### File: `patient_management/views.py`

This file contains **API endpoints** - the logic that handles HTTP requests.


### 1. Authentication Views

#### login_view

```python
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Authentication failed. Please check your username and password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
```

**Flow Explanation**:

1. **Decorator `@api_view(['POST'])`**: This function only accepts POST requests
2. **Decorator `@permission_classes([AllowAny])`**: Anyone can access (no authentication required for login itself)
3. **Extract credentials**: Get username and password from request body

4. **Django's `authenticate()`**: Checks if username/password match the database
5. **If valid**:
   - Call Django's `login()` to create a session
   - Generate or retrieve an authentication token
   - Return token to the client
6. **If invalid**: Return 401 Unauthorized error

**Why Token Authentication?**  
- The frontend stores the token (in localStorage or cookies)
- Every subsequent API request includes: `Authorization: Token abc123xyz`
- The server validates the token without checking username/password again

**Security Note**: We return a generic error message "Authentication failed" instead of "Invalid username" or "Invalid password" to prevent username enumeration attacks.

#### logout_view

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()
    logout(request)
    return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
```

**Flow**:
1. **`@permission_classes([IsAuthenticated])`**: Only logged-in users can logout
2. Delete the user's authentication token from the database
3. Call Django's `logout()` to clear the session
4. Return success message


---

### 2. ViewSets (CRUD Operations)

**What is a ViewSet?**  
A ViewSet is a Django REST Framework class that provides **multiple HTTP methods** in one place:
- `list()` → GET /api/patients/ (get all patients)
- `create()` → POST /api/patients/ (create new patient)
- `retrieve()` → GET /api/patients/1/ (get patient ID 1)
- `update()` → PUT /api/patients/1/ (update patient ID 1)
- `partial_update()` → PATCH /api/patients/1/ (partial update)
- `destroy()` → DELETE /api/patients/1/ (delete patient ID 1)

**Why use ViewSets instead of writing each function separately?**  
Django REST Framework auto-generates all CRUD operations. We don't need to write repetitive code!

#### PatientViewSet

```python
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
```

**3 Lines of Code = 6 API Endpoints!**

**Explanation**:
- `queryset = Patient.objects.all()`: Fetch all patients from the database
- `serializer_class = PatientSerializer`: Use PatientSerializer to convert data
- `permission_classes = [IsAuthenticated]`: Require authentication token


#### MedicalHistoryViewSet (with Filtering)

```python
class MedicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = MedicalHistory.objects.all()
        patient_id = self.request.query_params.get('patient_id', None)
        if patient_id is not None:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset
```

**Why the `get_queryset()` method?**  
We added **filtering** functionality:
- `GET /api/medical-history/` → Returns all medical history records
- `GET /api/medical-history/?patient_id=1` → Returns only records for patient ID 1

**How it works**:
1. Check if the request URL includes `?patient_id=...`
2. If yes, filter the queryset to show only that patient's records
3. If no, return all records

This is useful for displaying a patient's complete medical history on their detail page.

#### LabReportViewSet

Similar to MedicalHistoryViewSet, but for lab reports. Same filtering logic applies.


---

## URL Routing

### File: `patient_management/urls.py`

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'medical-history', MedicalHistoryViewSet, basename='medical-history')
router.register(r'lab-reports', LabReportViewSet, basename='lab-report')

urlpatterns = [
    path('', include(router.urls)),
]
```

**What is a Router?**  
A router **automatically generates URLs** for all ViewSet actions.

**What URLs are created?**

For `PatientViewSet` registered at `'patients'`:
- `GET /patients/` → list all patients
- `POST /patients/` → create new patient
- `GET /patients/1/` → retrieve patient ID 1
- `PUT /patients/1/` → update patient ID 1
- `PATCH /patients/1/` → partially update patient ID 1
- `DELETE /patients/1/` → delete patient ID 1

**Same pattern for**:
- `/medical-history/`
- `/lab-reports/`


### File: `cdss_backend/urls.py` (Main URL Configuration)

```python
from django.contrib import admin
from django.urls import path, include
from patient_management.views import login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/', include('patient_management.urls')),
]
```

**URL Structure**:
- `/admin/` → Django admin panel
- `/api/auth/login/` → Doctor login
- `/api/auth/logout/` → Doctor logout
- `/api/` → All patient_management URLs (patients, medical-history, lab-reports)

**Final API Endpoints**:
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET/POST /api/patients/`
- `GET/PUT/PATCH/DELETE /api/patients/{id}/`
- `GET/POST /api/medical-history/`
- `GET /api/medical-history/{id}/`
- `GET/POST /api/lab-reports/`
- `GET /api/lab-reports/{id}/`


---

## Authentication System

### File: `cdss_backend/settings.py`

```python
INSTALLED_APPS = [
    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party packages
    'rest_framework',
    'rest_framework.authtoken',  # For token authentication
    
    # Our apps
    'patient_management',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

**Configuration Explanation**:

1. **`rest_framework.authtoken`**: Enables token-based authentication
2. **`TokenAuthentication`**: Validates tokens sent in HTTP headers
3. **`SessionAuthentication`**: Allows Django admin and browsable API to work
4. **`IsAuthenticated`**: Default permission - all endpoints require authentication (except those marked `AllowAny`)


**How Token Authentication Works**:

1. **Doctor logs in** → Server generates a unique token (e.g., `9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`)
2. **Token stored in database** → Linked to the user account
3. **Frontend stores token** → In localStorage or cookies
4. **Every API request includes token** → `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`
5. **Server validates token** → If valid, request proceeds; if invalid, returns 401 Unauthorized

**Benefits of Token Authentication**:
- Stateless: Server doesn't need to maintain sessions
- Scalable: Works well with multiple servers
- Secure: Tokens can be revoked (deleted from database)
- Frontend-friendly: Easy to use with React/Angular/Vue

---

## Complete API Flow

Let me walk you through a complete user journey:

### Scenario: Doctor Registers a New Patient and Adds Lab Report

**Step 1: Doctor Logs In**

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "admin"
}
```


**Step 2: Create New Patient**

```http
POST /api/patients/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json

{
  "name": "Jane Smith",
  "date_of_birth": "1985-03-20",
  "gender": "Female",
  "phone": "555-0123",
  "email": "jane.smith@example.com"
}
```

**Response**:
```json
{
  "id": 2,
  "name": "Jane Smith",
  "date_of_birth": "1985-03-20",
  "gender": "Female",
  "phone": "555-0123",
  "email": "jane.smith@example.com",
  "created_at": "2024-01-20T14:30:00Z"
}
```

**What happened behind the scenes?**
1. Django REST Framework validated the token
2. PatientSerializer validated the input data
3. Django ORM created a new row in the `patient_management_patient` table
4. PostgreSQL auto-generated the ID (2) and timestamp
5. Serializer converted the Patient object back to JSON


**Step 3: Add Medical History**

```http
POST /api/medical-history/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json

{
  "patient": 2,
  "diagnoses": "Type 2 Diabetes, Hypertension",
  "medications": "Metformin 500mg twice daily, Lisinopril 10mg once daily",
  "allergies": "Sulfa drugs",
  "notes": "Patient reports good medication compliance"
}
```

**Response**:
```json
{
  "id": 1,
  "patient": 2,
  "diagnoses": "Type 2 Diabetes, Hypertension",
  "medications": "Metformin 500mg twice daily, Lisinopril 10mg once daily",
  "allergies": "Sulfa drugs",
  "notes": "Patient reports good medication compliance",
  "timestamp": "2024-01-20T14:35:00Z"
}
```

**Database relationship created**:
- MedicalHistory record ID 1 is now **linked** to Patient ID 2 via foreign key


**Step 4: Add Lab Report**

```http
POST /api/lab-reports/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json

{
  "patient": 2,
  "lab_data": {
    "glucose_fasting": 145,
    "hba1c": 7.2,
    "total_cholesterol": 210,
    "hdl": 45,
    "ldl": 135,
    "triglycerides": 180,
    "blood_pressure_systolic": 140,
    "blood_pressure_diastolic": 90,
    "test_date": "2024-01-18"
  }
}
```

**Response**:
```json
{
  "id": 1,
  "patient": 2,
  "lab_data": {
    "glucose_fasting": 145,
    "hba1c": 7.2,
    "total_cholesterol": 210,
    "hdl": 45,
    "ldl": 135,
    "triglycerides": 180,
    "blood_pressure_systolic": 140,
    "blood_pressure_diastolic": 90,
    "test_date": "2024-01-18"
  },
  "timestamp": "2024-01-20T14:40:00Z"
}
```

**Why this data structure is important for Module 2**:
The lab values (`glucose_fasting`, `hba1c`, `cholesterol`, etc.) will be fed into the ML models for risk prediction!


**Step 5: Retrieve Patient with Medical History**

```http
GET /api/patients/2/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response**:
```json
{
  "id": 2,
  "name": "Jane Smith",
  "date_of_birth": "1985-03-20",
  "gender": "Female",
  "phone": "555-0123",
  "email": "jane.smith@example.com",
  "created_at": "2024-01-20T14:30:00Z"
}
```

**Get Medical History for This Patient**:
```http
GET /api/medical-history/?patient_id=2
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response**:
```json
[
  {
    "id": 1,
    "patient": 2,
    "diagnoses": "Type 2 Diabetes, Hypertension",
    "medications": "Metformin 500mg twice daily, Lisinopril 10mg once daily",
    "allergies": "Sulfa drugs",
    "notes": "Patient reports good medication compliance",
    "timestamp": "2024-01-20T14:35:00Z"
  }
]
```

**Notice the filtering**: The `?patient_id=2` query parameter filtered the results to show only this patient's medical history.


---

## Testing Strategy

### File: `patient_management/tests.py`

We created **28 automated tests** covering:

### 1. Authentication Tests (7 tests)
- Valid login → returns token
- Invalid credentials → returns 401 error
- Missing credentials → returns 400 error
- Logout with valid token → deletes token
- Logout without token → returns 401 error
- Session management → verifies Django session created
- Token works for protected endpoints

### 2. Patient CRUD Tests (6 tests)
- Create patient with valid data
- Create patient with missing required fields → validation error
- List all patients
- Retrieve specific patient
- Update patient information
- Authentication required for all endpoints

### 3. Medical History Tests (4 tests)
- Create medical history for patient
- List all medical history records
- Filter medical history by patient_id
- Retrieve specific medical history record

### 4. Lab Report Tests (4 tests)
- Create lab report with JSON data
- List all lab reports
- Filter lab reports by patient_id
- Retrieve specific lab report with JSON data intact


### 5. Foreign Key Constraint Tests (3 tests)
- Delete patient → medical history records cascade deleted
- Delete patient → lab reports cascade deleted
- Delete patient → all related records (multiple) cascade deleted

### 6. Auto-Timestamp Tests (4 tests)
- Patient.created_at auto-generated
- MedicalHistory.timestamp auto-generated
- LabReport.timestamp auto-generated
- Timestamps are read-only via API (cannot be manually set)

**Why Testing is Important?**
- Ensures code works as expected
- Prevents regressions when making changes
- Documents how the system should behave
- Builds confidence in the implementation

**Test Execution**:
```bash
python manage.py test patient_management
```

**Result**: 28 tests passed in 14.931 seconds ✅

---

## Viva Questions & Answers

Here are common questions you might face during your viva, with detailed answers:


### Q1: Why did you choose Django instead of Flask?

**Answer**:
Django provides many built-in features that are essential for this project:
1. **ORM (Object-Relational Mapping)**: Instead of writing SQL queries, we use Python objects. Django automatically converts them to SQL.
2. **Built-in authentication**: Django has a complete user authentication system with password hashing, sessions, and permissions.
3. **Admin panel**: Django automatically generates an admin interface to view and manage data during development.
4. **Django REST Framework**: A powerful toolkit for building REST APIs with minimal code.
5. **Security**: Django handles common security issues like SQL injection, CSRF attacks, and XSS automatically.

Flask is more lightweight but requires more manual configuration. For an academic project with tight deadlines, Django's "batteries-included" approach saves development time.

### Q2: Explain the difference between ForeignKey and ManyToManyField?

**Answer**:
**ForeignKey (One-to-Many)**:
- One patient can have **multiple** medical history records
- Each medical history belongs to **one** patient
- Example: Patient → MedicalHistory (one-to-many)

**ManyToManyField**:
- Used when both sides can have multiple relationships
- Example: If we had a "Doctor" model and "Patient" model, one doctor treats many patients, and one patient can be treated by many doctors

In our project, we only use ForeignKey because:
- One patient has multiple medical histories
- One patient has multiple lab reports
- Each record belongs to exactly one patient


### Q3: What is the purpose of `on_delete=models.CASCADE`?

**Answer**:
`CASCADE` means "delete related records when the parent is deleted."

**Example**:
If we delete Patient ID 2 (Jane Smith):
- All her medical history records are automatically deleted
- All her lab reports are automatically deleted

**Why is this important?**
- **Data integrity**: We don't want orphaned records (medical history without a patient)
- **GDPR compliance**: If a patient requests data deletion, all their data should be removed
- **Database cleanliness**: Prevents accumulation of unused data

**Other options** (we didn't use):
- `models.PROTECT`: Cannot delete patient if they have medical records (prevents accidental deletion)
- `models.SET_NULL`: Set foreign key to NULL instead of deleting (requires `null=True`)
- `models.SET_DEFAULT`: Set to a default value

We chose CASCADE because in a clinical system, if a patient record is deleted, all associated data should be deleted too.

### Q4: Why did you use JSONField for lab reports instead of separate columns?

**Answer**:
**Flexibility**:
- Different lab tests have different parameters
- Blood glucose test: 1 value
- Complete blood count: 10+ values
- Lipid panel: 4-5 values


**Scalability**:
- Can add new lab test types without changing the database schema
- No need to run migrations every time a new test is added

**Real-world scenario**:
A hospital might add a new lab test next month. With JSONField, the system can handle it immediately without code changes.

**Drawbacks** (be honest):
- Cannot create database indexes on specific JSON fields (slower queries if we need to search by specific lab values)
- Less validation at the database level

**Why it's acceptable for this project**:
- We're not searching within JSON data frequently
- The flexibility outweighs the performance trade-off for an academic project
- PostgreSQL has good JSON support with built-in functions

### Q5: Explain how Token Authentication works?

**Answer**:
**Step-by-step flow**:

1. **Doctor logs in** with username/password
   - Request: `POST /api/auth/login/ {"username": "admin", "password": "admin123"}`

2. **Server validates credentials**
   - Django's `authenticate()` checks username/password against the database
   - Password is hashed (not stored in plain text)

3. **Server generates token**
   - A unique random string: `9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`
   - Stored in the `authtoken_token` table linked to the user


4. **Frontend stores token**
   - Saved in browser's localStorage or cookies

5. **Subsequent requests include token**
   - Every API call includes: `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

6. **Server validates token**
   - Django REST Framework checks if token exists in database
   - If valid: request proceeds
   - If invalid: returns 401 Unauthorized

**Benefits**:
- **Stateless**: Server doesn't maintain session state (good for scalability)
- **Secure**: Token can be revoked by deleting from database
- **Cross-platform**: Works with mobile apps, web apps, desktop apps
- **Performance**: No need to check username/password on every request

**Security considerations**:
- Token should be transmitted over HTTPS (encrypted)
- Token should have an expiration time (not implemented in our basic version)
- Token should be stored securely on the client side

### Q6: What is the difference between ModelSerializer and Serializer?

**Answer**:
**ModelSerializer** (what we used):
- Automatically generates fields based on the model
- Includes validation based on model field types
- Provides default `create()` and `update()` methods


**Example**:
```python
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'date_of_birth', 'gender', 'phone', 'email', 'created_at']
```
This automatically knows:
- `name` is a CharField with max_length=100
- `date_of_birth` is a DateField (validates date format)
- `email` is an EmailField (validates email format)

**Plain Serializer**:
- Requires manual field definition
- Used when you're not working directly with a model
- More control but more code

**Why we used ModelSerializer**:
- Saves time (less code to write)
- Keeps serializer and model in sync
- Automatic validation based on model constraints
- Perfect for simple CRUD operations

### Q7: Why did you use ViewSets instead of APIView or function-based views?

**Answer**:
**ViewSet** provides all CRUD operations in one class:

```python
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
```

This 4-line class gives us:
- `list()` - GET /api/patients/
- `create()` - POST /api/patients/
- `retrieve()` - GET /api/patients/1/
- `update()` - PUT /api/patients/1/
- `partial_update()` - PATCH /api/patients/1/
- `destroy()` - DELETE /api/patients/1/


**Alternative (function-based view)**:
Would require 6 separate functions, each with similar boilerplate code for:
- Parsing request data
- Validating data
- Saving to database
- Serializing response
- Error handling

**Alternative (APIView)**:
Would require manually writing methods for each HTTP method:
```python
class PatientAPIView(APIView):
    def get(self, request):
        # ... 10-15 lines of code
    
    def post(self, request):
        # ... 15-20 lines of code
    
    def put(self, request, pk):
        # ... 20-25 lines of code
```

**Why ViewSet is better for this project**:
- **DRY principle** (Don't Repeat Yourself): Eliminates repetitive code
- **Rapid development**: Perfect for academic projects with tight deadlines
- **Consistency**: All endpoints behave the same way
- **Easy to understand**: Clear structure for demonstration during viva

**When would you NOT use ViewSets?**
- Complex business logic that doesn't fit CRUD pattern
- Custom endpoints with unique behavior
- Need fine-grained control over each operation


### Q8: Explain the difference between PUT and PATCH?

**Answer**:
**PUT** (Full Update):
- Replaces the **entire resource**
- All fields must be provided
- Missing fields are set to null or default values

**Example**:
```http
PUT /api/patients/1/
{
  "name": "John Doe",
  "date_of_birth": "1990-01-01",
  "gender": "Male",
  "phone": "555-9999",
  "email": "john.updated@example.com"
}
```
If you omit `phone`, it might be set to null.

**PATCH** (Partial Update):
- Updates only the provided fields
- Other fields remain unchanged

**Example**:
```http
PATCH /api/patients/1/
{
  "phone": "555-9999"
}
```
Only the phone number changes. Name, email, etc. stay the same.

**When to use each**:
- **PUT**: When you have the complete object and want to replace it
- **PATCH**: When you only want to update specific fields (more common in UIs)

**In our project**: ViewSets provide both automatically!

