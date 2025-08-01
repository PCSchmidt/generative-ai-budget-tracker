/**
 * Development Mode Indicator
 * Shows when the app is using mock data
 */

import React from 'react';
import { apiService } from '../../services/api';

const DevModeIndicator = () => {
  // Only show in development mode
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  const indicatorStyle = {
    position: 'fixed',
    top: '10px',
    right: '10px',
    backgroundColor: '#fbbf24',
    color: '#92400e',
    padding: '8px 12px',
    borderRadius: '6px',
    fontSize: '12px',
    fontWeight: '600',
    zIndex: 1000,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
    border: '1px solid #f59e0b'
  };

  return (
    <div style={indicatorStyle}>
      🚧 DEV MODE - Mock Data
    </div>
  );
};

export default DevModeIndicator;
