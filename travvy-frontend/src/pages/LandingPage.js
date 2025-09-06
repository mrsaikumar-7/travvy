/**
 * Landing Page
 * 
 * Public landing page with hero section, features, and call-to-action
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout,
  Button,
  Typography,
  Row,
  Col,
  Card,
  Space,
  Divider,
} from 'antd';
import {
  RocketOutlined,
  StarOutlined,
  TeamOutlined,
  MessageOutlined,
  CameraOutlined,
  SoundOutlined,
  GlobalOutlined,
} from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph } = Typography;

const LandingPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const features = [
    {
      icon: <StarOutlined style={{ fontSize: '24px', color: '#1890ff' }} />,
      title: 'AI-Powered Planning',
      description: 'Get personalized trip recommendations powered by advanced AI algorithms.',
    },
    {
      icon: <TeamOutlined style={{ fontSize: '24px', color: '#1890ff' }} />,
      title: 'Real-time Collaboration',
      description: 'Plan trips together with friends and family in real-time.',
    },
    {
      icon: <MessageOutlined style={{ fontSize: '24px', color: '#1890ff' }} />,
      title: 'Smart Chat Assistant',
      description: 'Chat with our AI assistant to refine and optimize your travel plans.',
    },
    {
      icon: <CameraOutlined style={{ fontSize: '24px', color: '#1890ff' }} />,
      title: 'Image Recognition',
      description: 'Upload photos to get destination suggestions and travel inspiration.',
    },
    {
      icon: <SoundOutlined style={{ fontSize: '24px', color: '#1890ff' }} />,
      title: 'Voice Commands',
      description: 'Use voice commands to quickly add destinations and preferences.',
    },
    {
      icon: <GlobalOutlined style={{ fontSize: '24px', color: '#1890ff' }} />,
      title: 'Global Destinations',
      description: 'Discover and plan trips to destinations worldwide with local insights.',
    },
  ];

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate('/app/dashboard');
    } else {
      navigate('/auth/register');
    }
  };

  const handleSignIn = () => {
    if (isAuthenticated) {
      navigate('/app/dashboard');
    } else {
      navigate('/auth/login');
    }
  };

  return (
    <Layout>
      {/* Header */}
      <Header
        style={{
          background: '#fff',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          padding: '0 24px',
        }}
      >
        <Row justify="space-between" align="middle" style={{ height: '100%' }}>
          <Col>
            <Space>
              <RocketOutlined style={{ fontSize: '28px', color: '#1890ff' }} />
              <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
                Travvy
              </Title>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button type="text" onClick={handleSignIn}>
                {isAuthenticated ? 'Dashboard' : 'Sign In'}
              </Button>
              <Button type="primary" onClick={handleGetStarted}>
                {isAuthenticated ? 'Go to App' : 'Get Started'}
              </Button>
            </Space>
          </Col>
        </Row>
      </Header>

      {/* Main Content */}
      <Content>
        {/* Hero Section */}
        <div
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '120px 24px',
            textAlign: 'center',
          }}
        >
          <Row justify="center">
            <Col xs={24} md={16} lg={12}>
              <Title level={1} style={{ color: 'white', fontSize: '48px', marginBottom: '24px' }}>
                Plan Your Perfect Trip with AI
              </Title>
              <Paragraph
                style={{
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontSize: '20px',
                  marginBottom: '40px',
                }}
              >
                Create personalized travel itineraries, collaborate with friends, 
                and discover amazing destinations with our AI-powered trip planner.
              </Paragraph>
              <Space size="large">
                <Button
                  type="primary"
                  size="large"
                  style={{
                    background: '#fff',
                    color: '#1890ff',
                    border: 'none',
                    height: '50px',
                    padding: '0 32px',
                    fontSize: '16px',
                  }}
                  onClick={handleGetStarted}
                >
                  Start Planning Now
                </Button>
                <Button
                  size="large"
                  style={{
                    background: 'transparent',
                    color: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.5)',
                    height: '50px',
                    padding: '0 32px',
                    fontSize: '16px',
                  }}
                >
                  Watch Demo
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        {/* Features Section */}
        <div style={{ padding: '120px 24px' }}>
          <Row justify="center" style={{ marginBottom: '80px' }}>
            <Col xs={24} md={16} lg={12} style={{ textAlign: 'center' }}>
              <Title level={2}>Why Choose Travvy?</Title>
              <Paragraph style={{ fontSize: '18px', color: '#666' }}>
                Discover the features that make trip planning effortless and enjoyable.
              </Paragraph>
            </Col>
          </Row>

          <Row gutter={[32, 32]} justify="center">
            {features.map((feature, index) => (
              <Col xs={24} sm={12} lg={8} key={index}>
                <Card
                  style={{
                    height: '100%',
                    textAlign: 'center',
                    border: 'none',
                    boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
                  }}
                >
                  <div style={{ marginBottom: '16px' }}>
                    {feature.icon}
                  </div>
                  <Title level={4}>{feature.title}</Title>
                  <Paragraph style={{ color: '#666' }}>
                    {feature.description}
                  </Paragraph>
                </Card>
              </Col>
            ))}
          </Row>
        </div>

        {/* CTA Section */}
        <div
          style={{
            background: '#f5f5f5',
            padding: '80px 24px',
            textAlign: 'center',
          }}
        >
          <Row justify="center">
            <Col xs={24} md={16} lg={12}>
              <Title level={2}>Ready to Start Your Journey?</Title>
              <Paragraph style={{ fontSize: '18px', color: '#666', marginBottom: '32px' }}>
                Join thousands of travelers who are already using Travvy to create
                unforgettable travel experiences.
              </Paragraph>
              <Button
                type="primary"
                size="large"
                onClick={handleGetStarted}
                style={{
                  height: '50px',
                  padding: '0 48px',
                  fontSize: '16px',
                }}
              >
                Get Started Free
              </Button>
            </Col>
          </Row>
        </div>
      </Content>

      {/* Footer */}
      <Footer style={{ textAlign: 'center', background: '#001529', color: 'white' }}>
        <Row justify="center">
          <Col>
            <Space>
              <RocketOutlined style={{ color: '#1890ff' }} />
              <span>Travvy © 2024. All rights reserved.</span>
            </Space>
          </Col>
        </Row>
      </Footer>
    </Layout>
  );
};

export default LandingPage;
