import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axios';

function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [patient, setPatient] = useState(null);
  const [medicalHistory, setMedicalHistory] = useState([]);
  const [labReports, setLabReports] = useState([]);
  const [predictions, setPredictions] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [showHistoryForm, setShowHistoryForm] = useState(false);
  const [showLabForm, setShowLabForm] = useState(false);
  const [predicting, setPredicting] = useState(false);
  const [recommending, setRecommending] = useState(false);
  const [uploadingPdf, setUploadingPdf] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [extractedValues, setExtractedValues] = useState(null);
  const [showManualEntry, setShowManualEntry] = useState(false);

  // Form states
  const [historyForm, setHistoryForm] = useState({
    diagnoses: '',
    medications: '',
    allergies: '',
    notes: '',
  });

  const [labForm, setLabForm] = useState({
    glucose: '',
    hba1c: '',
    bmi: '',
    age: '',
    cholesterol: '',
    hdl: '',
    ldl: '',
    triglycerides: '',
    blood_pressure_systolic: '',
    blood_pressure_diastolic: '',
    heart_rate: '',
  });

  useEffect(() => {
    fetchPatientData();
  }, [id]);

  const fetchPatientData = async () => {
    try {
      const [patientRes, historyRes, labsRes] = await Promise.all([
        api.get(`/patients/${id}/`),
        api.get(`/medical-history/?patient_id=${id}`),
        api.get(`/lab-reports/?patient_id=${id}`),
      ]);

      setPatient(patientRes.data);
      setMedicalHistory(historyRes.data);
      setLabReports(labsRes.data);
      setError('');
    } catch (err) {
      setError('Failed to load patient data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/medical-history/', {
        ...historyForm,
        patient: id,
      });
      setSuccess('Medical history added successfully');
      setShowHistoryForm(false);
      setHistoryForm({ diagnoses: '', medications: '', allergies: '', notes: '' });
      fetchPatientData();
    } catch (err) {
      setError('Failed to add medical history');
    }
  };

  const handlePdfUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    console.log('PDF file selected:', file.name);

    if (!file.name.endsWith('.pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    setUploadingPdf(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('pdf_file', file);

      console.log('Uploading PDF to:', `/patients/${id}/upload-lab-report/`);

      const response = await api.post(`/patients/${id}/upload-lab-report/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Upload response:', response.data);

      const extractedData = {
        ...response.data.extracted_values,
        pdf_file_path: response.data.pdf_file_path
      };
      setExtractedValues(extractedData);
      setPdfFile(file.name);
      
      // Populate the form with extracted values
      const newLabForm = {
        glucose: response.data.extracted_values.glucose || '',
        hba1c: response.data.extracted_values.hba1c || '',
        bmi: response.data.extracted_values.bmi || '',
        age: response.data.extracted_values.age || '',
        cholesterol: response.data.extracted_values.cholesterol || '',  // Fixed: was total_cholesterol
        hdl: response.data.extracted_values.hdl || '',  // Added: was missing
        ldl: response.data.extracted_values.ldl || '',  // Added: was missing
        triglycerides: response.data.extracted_values.triglycerides || '',  // Added: was missing
        blood_pressure_systolic: response.data.extracted_values.blood_pressure_systolic || '',  // Fixed: was systolic_bp
        blood_pressure_diastolic: response.data.extracted_values.blood_pressure_diastolic || '',  // Fixed: was diastolic_bp
        heart_rate: response.data.extracted_values.heart_rate || '',
      };
      setLabForm(newLabForm);
      
      const successRate = (response.data.extraction_success_rate * 100).toFixed(0);
      setSuccess(`✅ PDF uploaded successfully! ${response.data.message}. Success rate: ${successRate}%. Please verify the values below.`);
      setShowManualEntry(true);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.error || 'Failed to upload PDF');
    } finally {
      setUploadingPdf(false);
    }
  };

  const handleLabSubmit = async (e) => {
    e.preventDefault();
    try {
      // Convert form data to numbers
      const labData = {};
      Object.keys(labForm).forEach(key => {
        if (labForm[key]) {
          labData[key] = parseFloat(labForm[key]);
        }
      });

      const labReportData = {
        patient: id,
        lab_data: labData,
      };

      // If this was from PDF upload, include the PDF path
      if (extractedValues && extractedValues.pdf_file_path) {
        labReportData.pdf_file_path = extractedValues.pdf_file_path;
      }

      await api.post('/lab-reports/', labReportData);
      
      setSuccess('Lab report saved successfully. Running risk prediction...');
      setShowLabForm(false);
      setShowManualEntry(false);
      setExtractedValues(null);
      const uploadedPdfName = pdfFile; // Store before clearing
      setPdfFile(null);
      setLabForm({
        glucose: '', hba1c: '', bmi: '', age: '',
        cholesterol: '', hdl: '', ldl: '', triglycerides: '',
        blood_pressure_systolic: '',
        blood_pressure_diastolic: '', heart_rate: '',
      });
      
      // Fetch updated patient data
      await fetchPatientData();
      
      // Auto-run prediction after saving
      setTimeout(async () => {
        try {
          setPredicting(true);
          const response = await api.post(`/patients/${id}/predict/`);
          setPredictions(response.data);
          setSuccess(`✅ Lab report saved and risk prediction complete! ${uploadedPdfName ? `(Used PDF: ${uploadedPdfName})` : ''}`);
        } catch (err) {
          setError(err.response?.data?.error || 'Failed to generate predictions');
        } finally {
          setPredicting(false);
        }
      }, 500);
    } catch (err) {
      setError('Failed to add lab report');
    }
  };

  const handleRunPrediction = async () => {
    setPredicting(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post(`/patients/${id}/predict/`);
      setPredictions(response.data);
      setSuccess('Risk predictions generated successfully');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate predictions');
    } finally {
      setPredicting(false);
    }
  };

  const handleGetRecommendation = async () => {
    setRecommending(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post(`/patients/${id}/recommend/`);
      setRecommendation(response.data);
      setSuccess('AI recommendations generated successfully');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate recommendations');
    } finally {
      setRecommending(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    navigate('/login');
  };

  const handleDeleteLabReport = async (labReportId) => {
    if (!window.confirm('Are you sure you want to delete this lab report?')) {
      return;
    }

    try {
      await api.delete(`/lab-reports/${labReportId}/`);
      setSuccess('Lab report deleted successfully');
      fetchPatientData();
      // Clear predictions if they exist
      setPredictions(null);
    } catch (err) {
      setError('Failed to delete lab report');
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!patient) {
    return <div className="container">Patient not found</div>;
  }

  return (
    <div>
      <div className="navbar">
        <h1 style={{ cursor: 'pointer' }} onClick={() => navigate('/patients')}>
          📋 Clinical Decision Support System
        </h1>
        <div className="navbar-user">
          <span>👨‍⚕️ Dr. {localStorage.getItem('username')}</span>
          <button className="btn btn-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="container">
        <button
          className="btn btn-secondary"
          onClick={() => navigate('/patients')}
          style={{ marginBottom: '15px' }}
        >
          ← Back to Patients
        </button>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {/* Patient Demographics */}
        <div className="card">
          <h2>Patient Information</h2>
          <p><strong>Name:</strong> {patient.name}</p>
          <p><strong>Date of Birth:</strong> {patient.date_of_birth}</p>
          <p><strong>Gender:</strong> {patient.gender}</p>
          <p><strong>Phone:</strong> {patient.phone || 'N/A'}</p>
          <p><strong>Email:</strong> {patient.email || 'N/A'}</p>
        </div>

        {/* Medical History */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2>Medical History ({medicalHistory.length})</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowHistoryForm(!showHistoryForm)}
            >
              {showHistoryForm ? 'Cancel' : '+ Add History'}
            </button>
          </div>

          {showHistoryForm && (
            <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '4px', marginTop: '15px' }}>
              <form onSubmit={handleHistorySubmit}>
                <div className="form-group">
                  <label>Diagnoses</label>
                  <textarea
                    className="form-control"
                    value={historyForm.diagnoses}
                    onChange={(e) => setHistoryForm({ ...historyForm, diagnoses: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Medications</label>
                  <textarea
                    className="form-control"
                    value={historyForm.medications}
                    onChange={(e) => setHistoryForm({ ...historyForm, medications: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Allergies</label>
                  <input
                    type="text"
                    className="form-control"
                    value={historyForm.allergies}
                    onChange={(e) => setHistoryForm({ ...historyForm, allergies: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Notes</label>
                  <textarea
                    className="form-control"
                    value={historyForm.notes}
                    onChange={(e) => setHistoryForm({ ...historyForm, notes: e.target.value })}
                  />
                </div>
                <button type="submit" className="btn btn-success">Save History</button>
              </form>
            </div>
          )}

          {medicalHistory.length > 0 ? (
            medicalHistory.map((history, index) => (
              <div key={index} style={{ borderTop: '1px solid #ddd', paddingTop: '10px', marginTop: '10px' }}>
                <p><strong>Date:</strong> {new Date(history.timestamp).toLocaleDateString()}</p>
                {history.diagnoses && <p><strong>Diagnoses:</strong> {history.diagnoses}</p>}
                {history.medications && <p><strong>Medications:</strong> {history.medications}</p>}
                {history.allergies && <p><strong>Allergies:</strong> {history.allergies}</p>}
                {history.notes && <p><strong>Notes:</strong> {history.notes}</p>}
              </div>
            ))
          ) : (
            <p style={{ marginTop: '15px', color: '#7f8c8d' }}>No medical history recorded</p>
          )}
        </div>

        {/* Lab Reports */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2>Lab Reports ({labReports.length})</h2>
            <button
              className="btn btn-primary"
              onClick={() => {
                setShowLabForm(!showLabForm);
                if (showLabForm) {
                  setShowManualEntry(false);
                  setExtractedValues(null);
                  setPdfFile(null);
                }
              }}
            >
              {showLabForm ? 'Cancel' : '+ Add Lab Report'}
            </button>
          </div>

          {showLabForm && (
            <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '4px', marginTop: '15px' }}>
              {!showManualEntry ? (
                <>
                  <h3 style={{ marginBottom: '15px' }}>Choose Input Method</h3>
                  
                  {/* PDF Upload Option */}
                  <div style={{ 
                    border: '2px dashed #3498db', 
                    borderRadius: '8px', 
                    padding: '20px', 
                    textAlign: 'center',
                    marginBottom: '20px',
                    backgroundColor: uploadingPdf ? '#e3f2fd' : 'white',
                    transition: 'background-color 0.3s'
                  }}>
                    <h4 style={{ marginBottom: '10px' }}>📄 Upload PDF Lab Report</h4>
                    <p style={{ color: '#7f8c8d', marginBottom: '15px' }}>
                      Upload a laboratory report PDF and we'll automatically extract the values
                    </p>
                    
                    {uploadingPdf && (
                      <div style={{ 
                        backgroundColor: '#2196f3', 
                        color: 'white', 
                        padding: '10px', 
                        borderRadius: '4px',
                        marginBottom: '15px',
                        fontWeight: 'bold'
                      }}>
                        ⏳ Uploading and extracting values... Please wait...
                      </div>
                    )}
                    
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handlePdfUpload}
                      style={{ display: 'none' }}
                      id="pdf-upload"
                      disabled={uploadingPdf}
                    />
                    <label htmlFor="pdf-upload">
                      <div
                        className="btn btn-success"
                        style={{ 
                          display: 'inline-block',
                          cursor: uploadingPdf ? 'not-allowed' : 'pointer',
                          opacity: uploadingPdf ? 0.6 : 1
                        }}
                      >
                        {uploadingPdf ? '⏳ Processing...' : '📤 Upload PDF'}
                      </div>
                    </label>
                  </div>

                  {/* Manual Entry Option */}
                  <div style={{ textAlign: 'center' }}>
                    <p style={{ color: '#7f8c8d', marginBottom: '10px' }}>OR</p>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setShowManualEntry(true)}
                    >
                      ✍️ Enter Values Manually
                    </button>
                  </div>
                </>
              ) : (
                <form onSubmit={handleLabSubmit}>
                  {pdfFile && (
                    <div style={{ 
                      backgroundColor: '#e8f5e9', 
                      padding: '10px', 
                      borderRadius: '4px', 
                      marginBottom: '15px',
                      border: '1px solid #4caf50'
                    }}>
                      <strong>📄 PDF Uploaded:</strong> {pdfFile}
                      <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#2e7d32' }}>
                        Please verify and edit the extracted values below before saving.
                      </p>
                    </div>
                  )}
                  {!pdfFile && (
                    <div style={{ marginBottom: '15px' }}>
                      <h4>Manual Entry Mode</h4>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => {
                          setShowManualEntry(false);
                          setLabForm({
                            glucose: '', hba1c: '', bmi: '', age: '',
                            cholesterol: '', hdl: '', ldl: '', triglycerides: '',
                            blood_pressure_systolic: '',
                            blood_pressure_diastolic: '', heart_rate: '',
                          });
                        }}
                        style={{ marginTop: '5px', fontSize: '12px', padding: '5px 10px' }}
                      >
                        ← Back to Upload Options
                      </button>
                    </div>
                  )}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                  <div className="form-group">
                    <label>Glucose (mg/dL)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-control"
                      value={labForm.glucose}
                      onChange={(e) => setLabForm({ ...labForm, glucose: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>HbA1c (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-control"
                      value={labForm.hba1c}
                      onChange={(e) => setLabForm({ ...labForm, hba1c: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>BMI</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-control"
                      value={labForm.bmi}
                      onChange={(e) => setLabForm({ ...labForm, bmi: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Age</label>
                    <input
                      type="number"
                      className="form-control"
                      value={labForm.age}
                      onChange={(e) => setLabForm({ ...labForm, age: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Cholesterol (mg/dL)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-control"
                      value={labForm.cholesterol}
                      onChange={(e) => setLabForm({ ...labForm, cholesterol: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>HDL (mg/dL)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-control"
                      value={labForm.hdl}
                      onChange={(e) => setLabForm({ ...labForm, hdl: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>LDL (mg/dL)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-control"
                      value={labForm.ldl}
                      onChange={(e) => setLabForm({ ...labForm, ldl: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Triglycerides (mg/dL)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-control"
                      value={labForm.triglycerides}
                      onChange={(e) => setLabForm({ ...labForm, triglycerides: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>BP Systolic (mmHg)</label>
                    <input
                      type="number"
                      className="form-control"
                      value={labForm.blood_pressure_systolic}
                      onChange={(e) => setLabForm({ ...labForm, blood_pressure_systolic: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>BP Diastolic (mmHg)</label>
                    <input
                      type="number"
                      className="form-control"
                      value={labForm.blood_pressure_diastolic}
                      onChange={(e) => setLabForm({ ...labForm, blood_pressure_diastolic: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Heart Rate (bpm)</label>
                    <input
                      type="number"
                      className="form-control"
                      value={labForm.heart_rate}
                      onChange={(e) => setLabForm({ ...labForm, heart_rate: e.target.value })}
                    />
                  </div>
                </div>
                <button type="submit" className="btn btn-success" style={{ marginTop: '10px' }}>
                  Save Lab Report
                </button>
              </form>
            )}
          </div>
        )}

        {labReports.length > 0 ? (
            labReports.map((lab, index) => (
              <div key={index} style={{ 
                borderTop: '1px solid #ddd', 
                paddingTop: '10px', 
                marginTop: '10px',
                position: 'relative'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <p><strong>Date:</strong> {new Date(lab.timestamp).toLocaleDateString()}</p>
                  <button
                    onClick={() => handleDeleteLabReport(lab.id)}
                    style={{
                      backgroundColor: '#e74c3c',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      padding: '5px 10px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = '#c0392b'}
                    onMouseOut={(e) => e.target.style.backgroundColor = '#e74c3c'}
                  >
                    🗑️ Delete
                  </button>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginTop: '10px' }}>
                  {Object.entries(lab.lab_data).map(([key, value]) => (
                    <div key={key}>
                      <strong>{key}:</strong> {value}
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <p style={{ marginTop: '15px', color: '#7f8c8d' }}>No lab reports recorded</p>
          )}
        </div>

        {/* Run Prediction Button */}
        {labReports.length > 0 && (
          <div className="card">
            <h2>Risk Prediction</h2>
            <p style={{ marginBottom: '15px', color: '#7f8c8d' }}>
              Run AI-powered risk prediction based on lab reports
            </p>
            <button
              className="btn btn-success"
              onClick={handleRunPrediction}
              disabled={predicting}
            >
              {predicting ? 'Generating Predictions...' : '🔍 Run Risk Prediction'}
            </button>

            {predictions && predictions.highest_risk && (
              <div style={{ marginTop: '20px' }}>
                <h3>Highest Risk Prediction</h3>
                
                {/* PDF Info Banner */}
                {predictions.pdf_filename && (
                  <div style={{
                    backgroundColor: '#e8f5e9',
                    border: '1px solid #4caf50',
                    borderRadius: '4px',
                    padding: '10px',
                    marginBottom: '15px'
                  }}>
                    <strong>📄 Predicted using PDF:</strong> {predictions.pdf_filename}
                    <br />
                    <small style={{ color: '#2e7d32' }}>
                      Uploaded: {predictions.pdf_upload_timestamp ? new Date(predictions.pdf_upload_timestamp).toLocaleString() : 'N/A'}
                    </small>
                  </div>
                )}
                
                <div style={{ borderTop: '1px solid #ddd', padding: '15px 0' }}>
                  <h4>{predictions.highest_risk.disease_type.replace('_', ' ').toUpperCase()}</h4>
                  <p>
                    <strong>Risk Score:</strong> {(predictions.highest_risk.risk_score * 100).toFixed(2)}%
                    <span
                      className={`risk-badge risk-${predictions.highest_risk.risk_category.toLowerCase()}`}
                      style={{ marginLeft: '10px' }}
                    >
                      {predictions.highest_risk.risk_category}
                    </span>
                  </p>
                  
                  {predictions.highest_risk.shap_explanations && predictions.highest_risk.shap_explanations.length > 0 && (
                    <div style={{ marginTop: '10px' }}>
                      <strong>Key Factors:</strong>
                      <ul>
                        {predictions.highest_risk.shap_explanations.slice(0, 5).map((shap, i) => (
                          <li key={i}>
                            {shap.feature_name}: {shap.shap_value.toFixed(4)} 
                            ({shap.direction === 'increases_risk' ? '⬆️ increases' : '⬇️ decreases'} risk)
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                
                {/* Show all predictions link */}
                <details style={{ marginTop: '15px' }}>
                  <summary style={{ cursor: 'pointer', color: '#3498db', fontWeight: 'bold' }}>
                    View All Predictions
                  </summary>
                  <div style={{ marginTop: '10px' }}>
                    {predictions.all_predictions.map((pred, index) => (
                      <div key={index} style={{ borderTop: '1px solid #eee', padding: '10px 0' }}>
                        <h5>{pred.disease_type.replace('_', ' ').toUpperCase()}</h5>
                        <p>
                          Risk Score: {(pred.risk_score * 100).toFixed(2)}% 
                          <span className={`risk-badge risk-${pred.risk_category.toLowerCase()}`} style={{ marginLeft: '10px' }}>
                            {pred.risk_category}
                          </span>
                        </p>
                      </div>
                    ))}
                  </div>
                </details>
              </div>
            )}
          </div>
        )}

        {/* AI Recommendations */}
        {predictions && (
          <div className="card">
            <h2>AI Clinical Recommendations</h2>
            <p style={{ marginBottom: '15px', color: '#7f8c8d' }}>
              Get evidence-based clinical recommendations from AI agent
            </p>
            
            {recommending && (
              <div className="alert alert-info">
                🤖 AI Agent is analyzing patient data, predictions, and medical guidelines...
                <br />
                This may take 15-30 seconds.
              </div>
            )}

            <button
              className="btn btn-primary"
              onClick={handleGetRecommendation}
              disabled={recommending}
            >
              {recommending ? 'Generating Recommendations...' : '🤖 Get AI Recommendations'}
            </button>

            {recommendation && (
              <div style={{ marginTop: '20px' }}>
                <div className="recommendation">
                  {recommendation.recommendation.split('\n').map((line, i) => {
                    // Bold section headers
                    if (line.includes('**') || line.startsWith('PATIENT SUMMARY') || 
                        line.startsWith('RISK ASSESSMENT') || line.startsWith('CLINICAL RECOMMENDATIONS') ||
                        line.startsWith('NEXT ACTIONS') || line.startsWith('DISCLAIMER')) {
                      return <p key={i} style={{ fontWeight: 'bold', marginTop: '15px' }}>{line.replace(/\*\*/g, '')}</p>;
                    }
                    return <p key={i}>{line}</p>;
                  })}
                </div>

                <div className="disclaimer">
                  <strong>⚠️ Important:</strong> These are AI-generated recommendations for decision support only. 
                  The doctor retains final clinical decision-making authority.
                </div>

                <div style={{ marginTop: '15px', fontSize: '12px', color: '#7f8c8d' }}>
                  <p>Tools used: {recommendation.tools_used.join(', ')}</p>
                  <p>Steps: {recommendation.steps_count}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default PatientDetail;
