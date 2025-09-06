/**
 * Authentication Context
 * 
 * Manages user authentication state and related operations
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { message } from 'antd';
import { apiService } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (token) {
        // Check if it's a demo token
        if (token.startsWith('demo-jwt-token-')) {
          // Restore demo user
          const mockUser = {
            uid: 'demo-user-123',
            email: 'demo@Travvy.com',
            displayName: 'Demo User',
            photoURL: null
          };
          setUser(mockUser);
          setIsAuthenticated(true);
        } else {
          // Try to get real user profile
          try {
            const response = await apiService.auth.getProfile();
            setUser(response.data);
            setIsAuthenticated(true);
          } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('authToken');
            setIsAuthenticated(false);
          }
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('authToken');
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setLoading(true);
      
      // For demo purposes, simulate a successful login with demo credentials
      if (credentials.email === 'demo@Travvy.com' && credentials.password === 'demo123') {
        // Mock user data
        const mockUser = {
          uid: 'demo-user-123',
          email: 'demo@Travvy.com',
          displayName: 'Demo User',
          photoURL: null
        };
        
        const mockToken = 'demo-jwt-token-' + Date.now();
        
        localStorage.setItem('authToken', mockToken);
        setUser(mockUser);
        setIsAuthenticated(true);
        
        message.success('Login successful!');
        return { success: true };
      }
      
      // Try actual API call for other credentials
      try {
        const response = await apiService.auth.login(credentials);
        const { access_token, user: userData } = response.data;
        
        localStorage.setItem('authToken', access_token);
        setUser(userData);
        setIsAuthenticated(true);
        
        message.success('Login successful!');
        return { success: true };
      } catch (apiError) {
        // If API fails, show error but allow demo login to work
        const errorMessage = apiError.response?.data?.detail || 'Login failed - API not fully implemented yet';
        message.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      const errorMessage = error.message || 'Login failed';
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      
      try {
        // Try actual API first
        const response = await apiService.auth.register(userData);
        const { access_token, user: newUser } = response.data;
        
        localStorage.setItem('authToken', access_token);
        setUser(newUser);
        setIsAuthenticated(true);
        
        message.success('Registration successful!');
        return { success: true };
      } catch (apiError) {
        // Fallback to mock registration when API fails (CORS or backend issues)
        console.warn('API registration failed, using mock registration:', apiError);
        
        // Create mock user
        const mockUser = {
          uid: 'new-user-' + Date.now(),
          email: userData.email,
          displayName: userData.displayName || userData.name || 'New User',
          photoURL: null,
          createdAt: new Date().toISOString()
        };
        
        const mockToken = 'mock-registration-token-' + userData.email.replace('@', '-at-');
        
        // Simulate API delay for realism
        await new Promise(resolve => setTimeout(resolve, 800));
        
        localStorage.setItem('authToken', mockToken);
        setUser(mockUser);
        setIsAuthenticated(true);
        
        message.success('Registration successful! (Demo mode - backend integration in progress)');
        return { success: true, user: mockUser };
      }
    } catch (error) {
      const errorMessage = error.message || 'Registration failed';
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const googleLogin = async (idToken) => {
    try {
      setLoading(true);
      const response = await apiService.auth.googleLogin(idToken);
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('authToken', access_token);
      setUser(userData);
      setIsAuthenticated(true);
      
      message.success('Google login successful!');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Google login failed';
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiService.auth.logout();
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      localStorage.removeItem('authToken');
      setUser(null);
      setIsAuthenticated(false);
      message.success('Logged out successfully');
    }
  };

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }));
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    googleLogin,
    logout,
    updateUser,
    checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
