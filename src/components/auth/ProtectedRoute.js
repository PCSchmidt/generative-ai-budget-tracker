/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingScreen from '../../screens/LoadingScreen';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  // Temporary debug logging to help diagnose redirects
  console.log('ProtectedRoute - isAuthenticated:', isAuthenticated, 'isLoading:', isLoading, 'user:', user);

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    console.log('ProtectedRoute: User not authenticated, redirecting to /login');
    return <Navigate to="/login" replace />;
  }

  console.log('ProtectedRoute: User authenticated, rendering protected content');
  return children;
};

export default ProtectedRoute;