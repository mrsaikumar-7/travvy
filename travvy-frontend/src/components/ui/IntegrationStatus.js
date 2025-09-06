/**
 * Integration Status Component
 * 
 * Shows the current status of backend integration and available features
 */

import React, { useState } from 'react';
import { Card, Row, Col, Tag, Button, Space, Typography, Divider, Alert } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  ExclamationCircleOutlined,
  LoginOutlined,
  PlusOutlined,
  MessageOutlined,
  TeamOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

const IntegrationStatus = () => {
  const [testResults, setTestResults] = useState({});

  const features = [
    {
      name: 'Backend API Connection',
      status: 'connected',
      description: 'Basic API connectivity working',
      icon: <CheckCircleOutlined />,
      color: 'success'
    },
    {
      name: 'User Authentication',
      status: 'working',
      description: 'Login & Registration with CORS-safe fallback',
      icon: <LoginOutlined />,
      color: 'processing'
    },
    {
      name: 'Trip Creation',
      status: 'partial',
      description: 'Creates demo trips, API integration in progress',
      icon: <PlusOutlined />,
      color: 'warning'
    },
    {
      name: 'AI Chat',
      status: 'working',
      description: 'Conversational trip planning with voice & image support',
      icon: <MessageOutlined />,
      color: 'processing'
    },
    {
      name: 'Real-time Collaboration',
      status: 'planned',
      description: 'WebSocket collaboration - coming soon',
      icon: <TeamOutlined />,
      color: 'default'
    }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
      case 'working':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'partial':
        return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'planned':
      default:
        return <SyncOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
      case 'working':
        return 'success';
      case 'partial':
        return 'warning';
      case 'error':
        return 'error';
      case 'planned':
      default:
        return 'default';
    }
  };

  return (
    <Card
      title={
        <Space>
          <Title level={4} style={{ margin: 0 }}>
            🚀 Integration Status
          </Title>
        </Space>
      }
      style={{ marginBottom: '24px' }}
    >
      <Alert
        message="Frontend ↔ Backend Integration"
        description="The frontend is now connected to the backend API. Demo authentication and basic features are working!"
        type="success"
        showIcon
        style={{ marginBottom: '16px' }}
      />

      <Divider orientation="left">Feature Status</Divider>

      <Row gutter={[16, 16]}>
        {features.map((feature, index) => (
          <Col xs={24} sm={12} lg={8} key={index}>
            <Card
              size="small"
              style={{ height: '100%' }}
              title={
                <Space>
                  {getStatusIcon(feature.status)}
                  <Text strong>{feature.name}</Text>
                </Space>
              }
              extra={
                <Tag color={getStatusColor(feature.status)}>
                  {feature.status.toUpperCase()}
                </Tag>
              }
            >
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {feature.description}
              </Text>
            </Card>
          </Col>
        ))}
      </Row>

      <Divider orientation="left">Quick Tests</Divider>

      <Space wrap>
        <Button 
          type="primary" 
          onClick={() => window.location.href = '/auth/login'}
          icon={<LoginOutlined />}
        >
          Test Login
        </Button>
        <Button 
          onClick={() => window.location.href = '/app/trips/new'}
          icon={<PlusOutlined />}
        >
          Test Trip Creation
        </Button>
        <Button 
          onClick={() => window.location.href = '/app/ai-chat'}
          icon={<MessageOutlined />}
        >
          Test AI Chat
        </Button>
        <Button 
          onClick={() => window.open('http://localhost:8000/docs', '_blank')}
        >
          Backend API Docs
        </Button>
      </Space>

      <Divider />

      <Text type="secondary" style={{ fontSize: '12px' }}>
        <strong>Next Steps:</strong> 
        Complete authentication endpoints, implement real AI integration, 
        add WebSocket support for collaboration, and connect all CRUD operations.
      </Text>
    </Card>
  );
};

export default IntegrationStatus;
