/**
 * App Router
 * 
 * Main routing configuration for Travvy
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Spin } from 'antd';

// Layout Components
import AppLayout from './layout/AppLayout';
import AuthLayout from './layout/AuthLayout';
import ProtectedRoute from './layout/ProtectedRoute';

// Page Components
import LandingPage from '../pages/LandingPage';
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';
import OAuthCallbackPage from '../pages/auth/OAuthCallbackPage';

import Dashboard from '../pages/dashboard/Dashboard';
import MyTripsPage from '../pages/trip/MyTripsPage';
import TripCreationWizard from '../pages/trip/TripCreationWizard';
import TripDetailsPage from '../pages/trip/TripDetailsPage';
import TripEditPage from '../pages/trip/TripEditPage';

import CollaborationPage from '../pages/collaboration/CollaborationPage';
import AIChatPage from '../pages/AIChat/AIChatPage';

import ProfilePage from '../pages/profile/ProfilePage';
import SettingsPage from '../pages/settings/SettingsPage';

import NotFoundPage from '../pages/NotFoundPage';

// Context
import { useAuth } from '../context/AuthContext';

const AppRouter = () => {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Spin size="large" tip="Loading..." />
      </div>
    );
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Auth Routes */}
      <Route path="/auth" element={<AuthLayout />}>
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="callback" element={<OAuthCallbackPage />} />
      </Route>

      {/* Protected Routes */}
      <Route path="/app" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route index element={<Navigate to="/app/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        
        {/* Trip Routes */}
        <Route path="trips">
          <Route index element={<MyTripsPage />} />
          <Route path="new" element={<TripCreationWizard />} />
          <Route path=":tripId" element={<TripDetailsPage />} />
          <Route path=":tripId/edit" element={<TripEditPage />} />
          <Route path=":tripId/collaborate" element={<CollaborationPage />} />
        </Route>

        {/* AI Chat */}
        <Route path="ai-chat" element={<AIChatPage />} />
        <Route path="ai-chat/:conversationId" element={<AIChatPage />} />

        {/* User Routes */}
        <Route path="profile" element={<ProfilePage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      {/* Collaboration - Special route that can be accessed by guests */}
      <Route path="/collaborate/:tripId/:token" element={<CollaborationPage />} />

      {/* 404 Page */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRouter;
