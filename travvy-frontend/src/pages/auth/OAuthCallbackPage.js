/**
 * OAuth Callback Page
 * 
 * Handles OAuth callback and redirects to appropriate page
 */

import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Spin, Result, Button } from 'antd';
import { useAuth } from '../../context/AuthContext';

const OAuthCallbackPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { googleLogin } = useAuth();

  useEffect(() => {
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    try {
      // Get parameters from URL
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');

      if (error) {
        throw new Error(`OAuth error: ${error}`);
      }

      if (!code) {
        throw new Error('No authorization code received');
      }

      // TODO: Implement actual OAuth token exchange
      // This would typically involve:
      // 1. Exchange code for access token
      // 2. Get user info from Google
      // 3. Login user in our system

      console.log('OAuth callback received:', { code, state });
      
      // For now, redirect to login
      setError('OAuth integration is not fully implemented yet');
      
      setTimeout(() => {
        navigate('/auth/login');
      }, 3000);
      
    } catch (err) {
      console.error('OAuth callback error:', err);
      setError(err.message || 'OAuth authentication failed');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <Spin size="large" />
        <div>Completing authentication...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Result
          status="error"
          title="Authentication Failed"
          subTitle={error}
          extra={[
            <Button type="primary" key="login" onClick={() => navigate('/auth/login')}>
              Back to Login
            </Button>,
            <Button key="home" onClick={() => navigate('/')}>
              Go Home
            </Button>,
          ]}
        />
      </div>
    );
  }

  return null;
};

export default OAuthCallbackPage;
