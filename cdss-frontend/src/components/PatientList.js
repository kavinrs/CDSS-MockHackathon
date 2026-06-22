import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';

function PatientList() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const navigate = useNavigate();

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    date_of_birth: '',
    gender: 'Male',
    phone: '',
    email: '',
  });

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await api.get('/patients/');
      setPatients(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load patients');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post('/patients/', formData);
      setShowAddForm(false);
      setFormData({
        name: '',
        date_of_birth: '',
        gender: 'Male',
        phone: '',
        email: '',
      });
      fetchPatients();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create patient');
    } finally {
      setLoading(false);
    }
  };

  const handlePatientClick = (patientId) => {
    navigate(`/patients/${patientId}`);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    navigate('/login');
  };

  if (loading && patients.length === 0) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="navbar">
        <h1>📋 Clinical Decision Support System</h1>
        <div className="navbar-user">
          <span>👨‍⚕️ Dr. {localStorage.getItem('username')}</span>
          <button className="btn btn-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="container">
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2>Patients ({patients.length})</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowAddForm(!showAddForm)}
            >
              {showAddForm ? 'Cancel' : '+ Add Patient'}
            </button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {showAddForm && (
            <div className="card" style={{ backgroundColor: '#f8f9fa', marginBottom: '20px' }}>
              <h3>Register New Patient</h3>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Full Name *</label>
                  <input
                    type="text"
                    name="name"
                    className="form-control"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Date of Birth *</label>
                  <input
                    type="date"
                    name="date_of_birth"
                    className="form-control"
                    value={formData.date_of_birth}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Gender *</label>
                  <select
                    name="gender"
                    className="form-control"
                    value={formData.gender}
                    onChange={handleInputChange}
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Phone</label>
                  <input
                    type="tel"
                    name="phone"
                    className="form-control"
                    value={formData.phone}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    className="form-control"
                    value={formData.email}
                    onChange={handleInputChange}
                  />
                </div>

                <button type="submit" className="btn btn-success" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Patient'}
                </button>
              </form>
            </div>
          )}

          {patients.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>
              <p>No patients registered yet.</p>
              <p>Click "Add Patient" to register your first patient.</p>
            </div>
          ) : (
            <div className="patient-list">
              {patients.map((patient) => (
                <div
                  key={patient.id}
                  className="patient-card"
                  onClick={() => handlePatientClick(patient.id)}
                >
                  <h3>{patient.name}</h3>
                  <div className="patient-info">
                    <p>
                      🎂 {patient.date_of_birth} | {patient.gender} | 
                      {patient.phone ? ` 📞 ${patient.phone}` : ''} |
                      {patient.email ? ` 📧 ${patient.email}` : ''}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PatientList;
