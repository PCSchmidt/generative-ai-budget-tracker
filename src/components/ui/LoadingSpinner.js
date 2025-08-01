/**
 * LoadingSpinner Component - Simple loading indicator
 * Phase 2: Core App Features - UI Enhancement
 */

import React from 'react';

const LoadingSpinner = ({ size = 'medium', color = 'var(--accent-600)' }) => {
  const sizeMap = {
    small: '20px',
    medium: '40px',
    large: '60px'
  };

  const spinnerStyle = {
    width: sizeMap[size],
    height: sizeMap[size],
    border: `3px solid var(--gray-200)`,
    borderTop: `3px solid ${color}`,
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  };

  return (
    <div>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
      <div style={spinnerStyle}></div>
    </div>
  );
};

export default LoadingSpinner;
