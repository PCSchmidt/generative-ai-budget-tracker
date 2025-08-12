import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const LoginScreen = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Navigate to dashboard when authentication succeeds
  useEffect(() => {
    if (isAuthenticated) {
      console.log('User authenticated, navigating to dashboard');
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Basic validation
    if (!formData.email || !formData.password) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoading(true);

    try {
      console.log('Attempting login with:', formData.email);
      const result = await login(formData.email, formData.password);
      console.log('Login result:', result);
      
      // Navigation will happen automatically via useEffect when isAuthenticated changes
    } catch (error) {
      console.error('Login error:', error);
      setError(error.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '48px',
        width: '100%',
        maxWidth: '440px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        border: '1px solid #e2e8f0',
        position: 'relative'
      }}>
        {/* Back to Home Button */}
        <Link 
          to="/" 
          style={{
            position: 'absolute',
            top: '20px',
            left: '20px',
            color: '#64748b',
            textDecoration: 'none',
            fontSize: '24px',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => e.target.style.color = '#3b82f6'}
          onMouseLeave={(e) => e.target.style.color = '#64748b'}
        >
          ← Home
        </Link>

        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#0f172a',
            margin: '0 0 8px 0',
            letterSpacing: '-0.025em'
          }}>
            Welcome Back
          </h1>
          <p style={{
            fontSize: '16px',
            color: '#64748b',
            margin: 0
          }}>
            Sign in to your account
          </p>
          
          {/* Test credentials for development */}
          <div style={{
            backgroundColor: '#fffbeb',
            border: '1px solid #fde68a',
            borderRadius: '8px',
            padding: '12px',
            marginTop: '16px',
            fontSize: '14px',
            color: '#92400e'
          }}>
            <strong>Test Credentials:</strong><br />
            Email: demo@budgettracker.com<br />
            Password: password123
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Email Address
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '16px',
                boxSizing: 'border-box',
                backgroundColor: '#ffffff',
                transition: 'border-color 0.2s ease',
                outline: 'none'
              }}
              placeholder="you@example.com"
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
            />
          </div>

          <div style={{ marginBottom: '32px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                style={{
                  width: '100%',
                  padding: '12px 50px 12px 16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '16px',
                  boxSizing: 'border-box',
                  backgroundColor: '#ffffff',
                  transition: 'border-color 0.2s ease',
                  outline: 'none'
                }}
                placeholder="Enter your password"
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  cursor: 'pointer',
                  color: 'rgb(59, 130, 246)',
                  fontSize: '18px',
                  padding: '8px',
                  borderRadius: '6px',
                  zIndex: 1000,
                  width: '36px',
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(59, 130, 246, 0.2)';
                  e.target.style.borderColor = 'rgb(59, 130, 246)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'rgba(59, 130, 246, 0.1)';
                  e.target.style.borderColor = 'rgba(59, 130, 246, 0.3)';
                }}
              >
                {showPassword ? '👁️' : '🙈'}
              </button>
            </div>
          </div>

          {error && (
            <div style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fca5a5',
              color: '#dc2626',
              padding: '14px 16px',
              borderRadius: '8px',
              marginBottom: '24px',
              fontSize: '14px',
              fontWeight: '500'
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              background: isLoading ? '#9ca3af' : '#2563eb',
              color: 'white',
              border: 'none',
              padding: '14px 16px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              marginBottom: '24px',
              transition: 'all 0.2s ease',
              boxShadow: isLoading ? 'none' : '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
            }}
            onMouseOver={(e) => {
              if (!isLoading) {
                e.target.style.backgroundColor = '#1d4ed8';
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 4px 12px 0 rgba(37, 99, 235, 0.3)';
              }
            }}
            onMouseOut={(e) => {
              if (!isLoading) {
                e.target.style.backgroundColor = '#2563eb';
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.05)';
              }
            }}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>

          <div style={{ textAlign: 'center' }}>
            <span style={{ color: '#64748b', fontSize: '14px' }}>
              Don't have an account?{' '}
              <Link
                to="/signup"
                style={{
                  color: '#2563eb',
                  textDecoration: 'none',
                  fontWeight: '600'
                }}
              >
                Sign up
              </Link>
            </span>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginScreen;
