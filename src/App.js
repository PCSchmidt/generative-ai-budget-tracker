/**
 * AI Budget Tracker - Phase 2 Modern UI/UX
 * Professional fintech web application with authentication
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Import screens
import LandingPage from './screens/LandingPage';
import LoginScreen from './screens/auth/LoginScreen';
import SignupScreen from './screens/auth/SignupScreen';
import DashboardScreen from './screens/dashboard/DashboardScreen';
import AIDashboardScreen from './screens/main/DashboardScreen';

// Import global styles
import './styles/GlobalStyles.css';
import GlobalBanner from './components/ui/GlobalBanner';
import DevModeIndicator from './components/dev/DevModeIndicator';

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <GlobalBanner />
          <DevModeIndicator />
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginScreen />} />
            <Route path="/signup" element={<SignupScreen />} />
            
            {/* Protected routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <DashboardScreen />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/ai-dashboard" 
              element={
                <ProtectedRoute>
                  <AIDashboardScreen />
                </ProtectedRoute>
              } 
            />
            
            {/* Redirect unknown routes to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}
