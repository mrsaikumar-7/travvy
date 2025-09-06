/**
 * API Test Component
 * 
 * Simple component to test backend API connectivity
 */

import React, { useState, useEffect } from 'react';
import { Card, Button, Typography, Space, Tag, Alert } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, SyncOutlined } from '@ant-design/icons';
import { apiService } from '../../services/api';

const { Title, Text } = Typography;

const ApiTestComponent = () => {
  const [apiStatus, setApiStatus] = useState('loading');
  const [apiResponse, setApiResponse] = useState(null);
  const [error, setError] = useState(null);

  const testApiConnection = async () => {
    try {
      setApiStatus('loading');
      setError(null);
      
      const response = await apiService.health();
      setApiResponse(response.data);
      setApiStatus('success');
    } catch (error) {
      console.error('API connection failed:', error);
      setError(error.message);
      setApiStatus('error');
    }
  };

  useEffect(() => {
    testApiConnection();
  }, []);

  const getStatusIcon = () => {
    switch (apiStatus) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'loading':
      default:
        return <SyncOutlined spin style={{ color: '#1890ff' }} />;
    }
  };

  const getStatusTag = () => {
    switch (apiStatus) {
      case 'success':
        return <Tag color="success">Connected</Tag>;
      case 'error':
        return <Tag color="error">Failed</Tag>;
      case 'loading':
      default:
        return <Tag color="processing">Connecting...</Tag>;
    }
  };

  return (
    <Card
      title={
        <Space>
          {getStatusIcon()}
          <Title level={4} style={{ margin: 0 }}>
            Backend API Connection
          </Title>
          {getStatusTag()}
        </Space>
      }
      extra={
        <Button onClick={testApiConnection} loading={apiStatus === 'loading'}>
          Test Connection
        </Button>
      }
      style={{ marginBottom: '16px' }}
    >
      {error && (
        <Alert
          message="Connection Failed"
          description={error}
          type="error"
          style={{ marginBottom: '16px' }}
        />
      )}

      {apiResponse && (
        <div>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>API Status: </Text>
              <Text>{apiResponse.message}</Text>
            </div>
            <div>
              <Text strong>Version: </Text>
              <Text>{apiResponse.version}</Text>
            </div>
            <div>
              <Text strong>Services: </Text>
              <Space>
                {apiResponse.services && Object.entries(apiResponse.services).map(([service, status]) => (
                  <Tag 
                    key={service} 
                    color={status === 'connected' || status === 'available' ? 'green' : 'red'}
                  >
                    {service}: {status}
                  </Tag>
                ))}
              </Space>
            </div>
          </Space>
        </div>
      )}
    </Card>
  );
};

export default ApiTestComponent;
