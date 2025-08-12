/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */

import React, { useMemo } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingScreen from '../../screens/LoadingScreen';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  // Fallback: if tokens exist in localStorage, treat as authenticated during hydration
  const hasLocalSession = useMemo(() => {
    try {
      const at = localStorage.getItem('accessToken');
      const us = localStorage.getItem('user');
      return Boolean(at && us);
    } catch {
      return false;
    }
  }, []);

  // Temporary debug logging to help diagnose redirects
  try {
    const lsAccess = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
    console.log('ProtectedRoute - isAuthenticated:', isAuthenticated, 'isLoading:', isLoading, 'user:', user, 'hasLSAccess:', !!lsAccess);
  } catch {}

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated && !hasLocalSession) {
    console.log('ProtectedRoute: User not authenticated, redirecting to /login');
    return <Navigate to="/login" replace />;
  }

  console.log('ProtectedRoute: User authenticated, rendering protected content');
  return children;
};

export default ProtectedRoute;