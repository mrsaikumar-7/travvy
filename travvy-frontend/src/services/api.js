/**
 * API Service Configuration
 * 
 * Centralized API configuration and service methods for Travvy
 */

import axios from 'axios';
import { message } from 'antd';

// API Base Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error;
    
    if (response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      return Promise.reject(error);
    }
    
    if (response?.status >= 500) {
      message.error('Server error occurred. Please try again later.');
    }
    
    return Promise.reject(error);
  }
);

// API Service Methods
export const apiService = {
  // Auth endpoints
  auth: {
    googleLogin: (idToken) => api.post('/api/v1/auth/google', { id_token: idToken }),
    login: (credentials) => api.post('/api/v1/auth/login', credentials),
    register: (userData) => api.post('/api/v1/auth/register', userData),
    refreshToken: (refreshToken) => api.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),
    logout: () => api.post('/api/v1/auth/logout'),
    getProfile: () => api.get('/api/v1/auth/me'),
  },

  // Trip endpoints
  trips: {
    create: (tripData) => api.post('/api/v1/trips', tripData),
    list: (params) => api.get('/api/v1/trips', { params }),
    get: (tripId) => api.get(`/api/v1/trips/${tripId}`),
    update: (tripId, updateData) => api.put(`/api/v1/trips/${tripId}`, updateData),
    delete: (tripId) => api.delete(`/api/v1/trips/${tripId}`),
    duplicate: (tripId) => api.post(`/api/v1/trips/${tripId}/duplicate`),
    optimize: (tripId, preferences) => api.post(`/api/v1/trips/${tripId}/optimize`, preferences),
    getStatus: (tripId) => api.get(`/api/v1/trips/${tripId}/status`),
  },

  // AI endpoints
  ai: {
    startConversation: (messageData) => api.post('/api/v1/ai/conversation', messageData),
    analyzeImage: (imageFile, prompt) => {
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('prompt', prompt);
      return api.post('/api/v1/ai/image-analysis', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
    processVoice: (audioFile) => {
      const formData = new FormData();
      formData.append('audio', audioFile);
      return api.post('/api/v1/ai/voice-input', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
    getTaskStatus: (taskId) => api.get(`/api/v1/ai/task/${taskId}`),
    getSuggestions: (query) => api.post('/api/v1/ai/suggestions', { query }),
    enhanceItinerary: (tripId, enhancementType) => 
      api.post('/api/v1/ai/enhance-itinerary', { trip_id: tripId, enhancement_type: enhancementType }),
  },

  // Collaboration endpoints
  collaboration: {
    invite: (tripId, inviteData) => api.post(`/api/v1/collaboration/trips/${tripId}/invite`, inviteData),
    createVote: (tripId, voteData) => api.post(`/api/v1/collaboration/trips/${tripId}/vote`, voteData),
    castVote: (tripId, voteId, selections) => 
      api.post(`/api/v1/collaboration/trips/${tripId}/votes/${voteId}/cast`, { selections }),
    getSession: (tripId) => api.get(`/api/v1/collaboration/trips/${tripId}/session`),
    joinCollaboration: (tripId, invitationToken) => 
      api.post(`/api/v1/collaboration/trips/${tripId}/join`, { invitation_token: invitationToken }),
  },

  // User endpoints
  users: {
    getProfile: () => api.get('/api/v1/users/me'),
    updateProfile: (profileData) => api.put('/api/v1/users/me', profileData),
    updatePreferences: (preferences) => api.put('/api/v1/users/me/preferences', preferences),
    getStats: () => api.get('/api/v1/users/me/stats'),
    deleteAccount: () => api.delete('/api/v1/users/me'),
  },

  // Notification endpoints
  notifications: {
    list: () => api.get('/api/v1/notifications'),
    updatePreferences: (preferences) => api.put('/api/v1/notifications/preferences', preferences),
    markAsRead: (notificationId) => api.post(`/api/v1/notifications/${notificationId}/mark-read`),
  },

  // Analytics endpoints
  analytics: {
    getUserAnalytics: (period = '30d') => api.get('/api/v1/analytics/user', { params: { period } }),
    getSystemAnalytics: (period = '7d') => api.get('/api/v1/analytics/system', { params: { period } }),
  },

  // Health check
  health: () => api.get('/health'),
};

export default api;
