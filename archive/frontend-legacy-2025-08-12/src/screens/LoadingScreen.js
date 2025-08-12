/**
 * Loading Screen for AI Budget Tracker
 * Shows while authentication state is being determined
 */

import React from 'react';

const LoadingScreen = () => {
  const containerStyle = {
    minHeight: '100vh',
    backgroundColor: '#f8fafc',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '2rem',
  };

  const contentStyle = {
    textAlign: 'center',
    maxWidth: '400px',
  };

  const logoStyle = {
    fontSize: '4rem',
    marginBottom: '1rem',
  };

  const titleStyle = {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: '2rem',
  };

  const loaderStyle = {
    width: '40px',
    height: '40px',
    border: '4px solid #e2e8f0',
    borderTop: '4px solid #2563eb',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 1rem',
  };

  const subtitleStyle = {
    fontSize: '1rem',
    color: '#475569',
    fontWeight: '500',
  };

  return (
    <div style={containerStyle}>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
      <div style={contentStyle}>
        <div style={logoStyle}>💰</div>
        <h1 style={titleStyle}>AI Budget Tracker</h1>
        <div style={loaderStyle}></div>
        <p style={subtitleStyle}>Loading your financial insights...</p>
      </div>
    </div>
  );
};

export default LoadingScreen;
