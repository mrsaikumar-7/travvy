/**
 * Auth Layout
 * 
 * Layout for authentication pages (login, register, etc.)
 */

import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Layout, Row, Col, Typography, Space } from 'antd';
import { RocketOutlined } from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';

const { Content } = Layout;
const { Title, Text } = Typography;

const AuthLayout = () => {
  const { isAuthenticated } = useAuth();

  // Redirect to dashboard if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/app/dashboard" replace />;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px',
        }}
      >
        <Row
          style={{
            width: '100%',
            maxWidth: '1200px',
            minHeight: '600px',
          }}
        >
          {/* Left Side - Branding */}
          <Col
            xs={0}
            md={12}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px 0 0 12px',
              padding: '48px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              color: 'white',
            }}
          >
            <Space direction="vertical" size="large" align="center">
              <RocketOutlined style={{ fontSize: '64px' }} />
              <Title level={1} style={{ color: 'white', textAlign: 'center' }}>
                Travvy
              </Title>
              <Text
                style={{
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontSize: '18px',
                  textAlign: 'center',
                  lineHeight: 1.6,
                }}
              >
                Plan your perfect trip with the power of AI. Get personalized itineraries,
                real-time collaboration, and intelligent recommendations.
              </Text>
              
              <div style={{ marginTop: '32px' }}>
                <Space direction="vertical" align="center">
                  <Text style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                    ✨ AI-Powered Trip Generation
                  </Text>
                  <Text style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                    🤝 Real-time Collaboration
                  </Text>
                  <Text style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                    🎯 Personalized Recommendations
                  </Text>
                  <Text style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                    📱 Voice & Image Input
                  </Text>
                </Space>
              </div>
            </Space>
          </Col>

          {/* Right Side - Auth Form */}
          <Col
            xs={24}
            md={12}
            style={{
              background: 'white',
              borderRadius: {
                xs: '12px',
                md: '0 12px 12px 0',
              },
              padding: '48px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <div style={{ width: '100%', maxWidth: '400px' }}>
              <Outlet />
            </div>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default AuthLayout;
