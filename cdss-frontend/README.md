# Clinical Decision Support System - Frontend

React-based frontend for the Clinical Decision Support System.

## Features

- **Doctor Authentication**: Login with token-based auth
- **Patient Management**: Register and view patients
- **Medical Data Entry**: Add medical history and lab reports
- **Risk Prediction**: AI-powered risk assessment with SHAP explanations
- **AI Recommendations**: Evidence-based clinical recommendations from AI agent
- **Responsive Design**: Works on desktop and mobile

## Prerequisites

- Node.js (v14 or higher)
- Django backend running on http://localhost:8000

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The application will open at http://localhost:3000

## Project Structure

```
src/
├── api/
│   └── axios.js           # API configuration with auth interceptors
├── components/
│   ├── Login.js           # Login page
│   ├── PatientList.js     # Patient list and registration
│   └── PatientDetail.js   # Patient details, predictions, recommendations
├── App.js                 # Main app with routing
└── App.css                # Global styles
```

## Usage

### 1. Login
- Default credentials: `admin` / `admin123`
- Token is stored in localStorage

### 2. Patient Management
- View all patients
- Click "Add Patient" to register new patients
- Click on a patient to view details

### 3. Medical Data Entry
- Add medical history (diagnoses, medications, allergies)
- Add lab reports (glucose, HbA1c, BMI, cholesterol, BP, etc.)

### 4. Risk Prediction
- Click "Run Risk Prediction" to generate risk scores
- View risk categories: Low (green), Moderate (yellow), High (red)
- See SHAP feature importance explanations

### 5. AI Recommendations
- Click "Get AI Recommendations" after running predictions
- AI agent analyzes patient data, predictions, and medical guidelines
- Generates comprehensive clinical recommendations
- Processing time: 15-30 seconds

## API Endpoints Used

- `POST /api/auth/login/` - Doctor login
- `GET /api/patients/` - List patients
- `POST /api/patients/` - Create patient
- `GET /api/patients/{id}/` - Get patient details
- `GET /api/medical-history/?patient_id={id}` - Get medical history
- `POST /api/medical-history/` - Add medical history
- `GET /api/lab-reports/?patient_id={id}` - Get lab reports
- `POST /api/lab-reports/` - Add lab report
- `POST /api/patients/{id}/predict/` - Generate risk predictions
- `POST /api/patients/{id}/recommend/` - Get AI recommendations

## Technologies

- **React 19**: UI framework
- **React Router DOM 7**: Client-side routing
- **Axios**: HTTP client with interceptors
- **CSS3**: Styling with flexbox and grid

## Development

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Notes

- Proxy is configured to forward API requests to Django backend
- Auth token is automatically added to all API requests
- Unauthorized requests (401) automatically redirect to login
- All forms include validation and error handling
- Loading indicators shown during async operations

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
