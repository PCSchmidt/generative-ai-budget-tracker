/**
 * Landing Page - AI Budget Tracker
 * Public landing page with call-to-action for signup/login
 */

import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  const containerStyle = {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
    position: 'relative'
  };

  const backgroundAnimationStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `
      radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 40% 80%, rgba(16, 185, 129, 0.1) 0%, transparent 50%)
    `,
    animation: 'float 6s ease-in-out infinite'
  };

  const contentStyle = {
    textAlign: 'center',
    position: 'relative',
    zIndex: 1,
    maxWidth: '800px'
  };

  const titleStyle = {
    fontSize: '4rem',
    fontWeight: '800',
    background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #06d6a0 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    marginBottom: '1rem',
    lineHeight: '1.1'
  };

  const subtitleStyle = {
    fontSize: '1.5rem',
    color: '#94a3b8',
    marginBottom: '3rem',
    lineHeight: '1.6'
  };

  const buttonContainerStyle = {
    display: 'flex',
    gap: '1.5rem',
    justifyContent: 'center',
    flexWrap: 'wrap'
  };

  const buttonStyle = {
    padding: '16px 32px',
    borderRadius: '12px',
    fontSize: '1.1rem',
    fontWeight: '600',
    textDecoration: 'none',
    transition: 'all 0.3s ease',
    minWidth: '180px',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center'
  };

  const primaryButtonStyle = {
    ...buttonStyle,
    background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
    color: 'white',
    border: 'none'
  };

  const secondaryButtonStyle = {
    ...buttonStyle,
    background: 'transparent',
    border: '2px solid #374151',
    color: '#f8fafc'
  };

  const featureGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '2rem',
    marginTop: '4rem',
    maxWidth: '1000px'
  };

  const featureCardStyle = {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(10px)',
    borderRadius: '16px',
    padding: '2rem',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    textAlign: 'left'
  };

  const featureIconStyle = {
    fontSize: '2.5rem',
    marginBottom: '1rem',
    display: 'block'
  };

  const featureTitleStyle = {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#f8fafc',
    marginBottom: '0.5rem'
  };

  const featureDescStyle = {
    color: '#94a3b8',
    fontSize: '1rem',
    lineHeight: '1.6'
  };

  return (
    <div style={containerStyle}>
      <style>
        {`
          @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            33% { transform: translateY(-10px) rotate(1deg); }
            66% { transform: translateY(5px) rotate(-1deg); }
          }
          
          .primary-button:hover {
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(37, 99, 235, 0.4);
          }
          
          .secondary-button:hover {
            border-color: #3b82f6 !important;
            background: rgba(59, 130, 246, 0.1) !important;
          }
        `}
      </style>
      
      <div style={backgroundAnimationStyle}></div>
      
      <div style={contentStyle}>
        <h1 style={titleStyle}>AI Budget Tracker</h1>
        <p style={subtitleStyle}>
          Take control of your finances with intelligent insights, automated categorization, 
          and personalized recommendations powered by artificial intelligence.
        </p>
        
        <div style={buttonContainerStyle}>
          <Link 
            to="/signup" 
            style={primaryButtonStyle}
            className="primary-button"
          >
            Get Started Free
          </Link>
          <Link 
            to="/login" 
            style={secondaryButtonStyle}
            className="secondary-button"
          >
            Sign In
          </Link>
        </div>

        <div style={featureGridStyle}>
          <div style={featureCardStyle}>
            <span style={featureIconStyle}>🤖</span>
            <h3 style={featureTitleStyle}>AI-Powered Insights</h3>
            <p style={featureDescStyle}>
              Get intelligent analysis of your spending patterns and personalized recommendations for better financial health.
            </p>
          </div>

          <div style={featureCardStyle}>
            <span style={featureIconStyle}>📊</span>
            <h3 style={featureTitleStyle}>Smart Categorization</h3>
            <p style={featureDescStyle}>
              Automatically categorize expenses using machine learning, saving you time and ensuring accuracy.
            </p>
          </div>

          <div style={featureCardStyle}>
            <span style={featureIconStyle}>🎯</span>
            <h3 style={featureTitleStyle}>Goal Tracking</h3>
            <p style={featureDescStyle}>
              Set financial goals and track your progress with AI-powered predictions and actionable insights.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
