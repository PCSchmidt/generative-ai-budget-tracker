/**
 * Authentication Context for AI Budget Tracker
 * Manages user authentication state throughout the app
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import ApiService from '../services/api';

// Authentication Actions
const AUTH_ACTIONS = {
  LOADING: 'LOADING',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  SIGNUP_SUCCESS: 'SIGNUP_SUCCESS',
  SIGNUP_FAILURE: 'SIGNUP_FAILURE',
  TOKEN_REFRESH: 'TOKEN_REFRESH',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Initial state
const initialState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Authentication reducer
function authReducer(state, action) {
  switch (action.type) {
    case AUTH_ACTIONS.LOADING:
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
    case AUTH_ACTIONS.SIGNUP_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.SIGNUP_FAILURE:
      return {
        ...state,
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload.error,
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };

    case AUTH_ACTIONS.TOKEN_REFRESH:
      return {
        ...state,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
}

// Create context
const AuthContext = createContext();

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize authentication on app start
  useEffect(() => {
    initializeAuth();
  }, []);

  const migrateLegacyMockKeys = () => {
    // Some older builds/extensions may have used mockAccessToken/mockRefreshToken
    const legacyAccess = localStorage.getItem('mockAccessToken');
    const legacyRefresh = localStorage.getItem('mockRefreshToken');
    if (!localStorage.getItem('accessToken') && legacyAccess) {
      console.log('AuthContext: Migrating legacy mockAccessToken to accessToken');
      localStorage.setItem('accessToken', legacyAccess);
    }
    if (!localStorage.getItem('refreshToken') && legacyRefresh) {
      console.log('AuthContext: Migrating legacy mockRefreshToken to refreshToken');
      localStorage.setItem('refreshToken', legacyRefresh);
    }
  };

  const initializeAuth = async () => {
    try {
      console.log('AuthContext: Initializing authentication...');
      dispatch({ type: AUTH_ACTIONS.LOADING });

      // Migrate legacy keys if present
      migrateLegacyMockKeys();

      // Check if user data exists in localStorage
      const userString = localStorage.getItem('user');
      const accessToken = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');

      console.log('AuthContext: Checking stored auth data:', {
        hasUser: !!userString,
        hasAccessToken: !!accessToken,
        hasRefreshToken: !!refreshToken
      });

      // Treat as authenticated if we have a user and an access token (refresh token optional)
      if (userString && accessToken) {
        try {
          const user = JSON.parse(userString);
          console.log('AuthContext: Restoring session for user:', user.email);
          
          // Initialize API service with the tokens
          await ApiService.storeTokens(accessToken, refreshToken ?? null);
          
          dispatch({
            type: AUTH_ACTIONS.LOGIN_SUCCESS,
            payload: {
              user,
              accessToken,
              refreshToken: refreshToken ?? null,
            },
          });
          console.log('AuthContext: Session restored successfully');
          return;
        } catch (parseError) {
          console.error('Failed to parse stored user data:', parseError);
          // Clear invalid data
          localStorage.removeItem('user');
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
        }
      }

      // No valid auth state found - user is not authenticated
      console.log('AuthContext: No valid stored auth data, user not authenticated');
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    } catch (error) {
      console.error('Auth initialization failed:', error);
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  // Login function
  const login = async (email, password) => {
    try {
      console.log('AuthContext: Starting login process');
      dispatch({ type: AUTH_ACTIONS.LOADING });

      const result = await ApiService.login(email, password);
      console.log('AuthContext: API login result:', result);

      // Store user data and tokens in localStorage
      localStorage.setItem('user', JSON.stringify(result.user));
      localStorage.setItem('accessToken', result.access_token);
      if (result.refresh_token) {
        localStorage.setItem('refreshToken', result.refresh_token);
      } else {
        localStorage.removeItem('refreshToken');
      }

      // Store tokens in API service
      await ApiService.storeTokens(result.access_token, result.refresh_token ?? null);

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: {
          user: result.user,
          accessToken: result.access_token,
          refreshToken: result.refresh_token ?? null,
        },
      });

      console.log('AuthContext: Login successful, user authenticated');
      return { success: true };
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: { error: error.message || 'Login failed. Please try again.' },
      });
      throw error;
    }
  };

  // Signup function
  const signup = async (userData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOADING });

      const result = await ApiService.signup(userData);

      // Store user data and tokens in localStorage
      localStorage.setItem('user', JSON.stringify(result.user));
      localStorage.setItem('accessToken', result.access_token);
      if (result.refresh_token) {
        localStorage.setItem('refreshToken', result.refresh_token);
      } else {
        localStorage.removeItem('refreshToken');
      }

      // Store tokens in API service
      await ApiService.storeTokens(result.access_token, result.refresh_token ?? null);

      dispatch({
        type: AUTH_ACTIONS.SIGNUP_SUCCESS,
        payload: {
          user: result.user,
          accessToken: result.access_token,
          refreshToken: result.refresh_token ?? null,
        },
      });

      return { success: true };
    } catch (error) {
      console.error('Signup error:', error);
      dispatch({
        type: AUTH_ACTIONS.SIGNUP_FAILURE,
        payload: { error: error.message || 'Signup failed. Please try again.' },
      });
      throw error;
    }
  };

  // Logout function
  const logout = async () => {
    try {
      // Call API logout if refresh token exists
      if (state.refreshToken) {
        await ApiService.logout(state.refreshToken);
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      // Clear all stored data
      localStorage.removeItem('user');
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      await ApiService.clearTokens();
      
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Refresh token function
  const refreshToken = async () => {
    try {
      if (!state.refreshToken) {
        throw new Error('No refresh token available');
      }

      const result = await ApiService.refreshToken(state.refreshToken);

      dispatch({
        type: AUTH_ACTIONS.TOKEN_REFRESH,
        payload: {
          accessToken: result.access_token,
          refreshToken: result.refresh_token,
        },
      });

      return { success: true };
    } catch (error) {
      console.error('Token refresh failed:', error);
      // If refresh fails, logout user
      await logout();
      return { success: false, error: error.message };
    }
  };

  const value = {
    // State
    user: state.user,
    accessToken: state.accessToken,
    refreshToken: state.refreshToken,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,

    // Actions
    login,
    signup,
    logout,
    clearError,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
