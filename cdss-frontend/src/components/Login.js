import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('/api/auth/login/', {
        username,
        password,
      });

      // Store token and username
      localStorage.setItem('authToken', response.data.token);
      localStorage.setItem('username', response.data.username);

      // Redirect to patient list
      navigate('/patients');
    } catch (err) {
      setError(
        err.response?.data?.error || 'Login failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Clinical Decision Support System</h2>
        <p style={{ textAlign: 'center', color: '#7f8c8d', marginBottom: '30px' }}>
          Doctor Login
        </p>

        {error && (
          <div className="alert alert-error">{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              className="form-control"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '10px' }}
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '14px', color: '#7f8c8d' }}>
          Don't have an account?{' '}
          <Link
            to="/register"
            style={{
              color: '#3498db',
              textDecoration: 'none',
              fontWeight: '500',
            }}
          >
            Register here
          </Link>
        </div>

        <div style={{ marginTop: '15px', textAlign: 'center', fontSize: '12px', color: '#95a5a6' }}>
          <p>Default credentials: admin / admin123</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
