/**
 * 404 Not Found Page
 * 
 * Displayed when user navigates to a non-existent route
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Result, Button, Typography, Space } from 'antd';
import { HomeOutlined, RocketOutlined } from '@ant-design/icons';

const { Paragraph } = Typography;

const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      background: '#f5f5f5'
    }}>
      <Result
        status="404"
        title="404"
        subTitle="Sorry, the page you visited does not exist."
        extra={
          <Space>
            <Button type="primary" onClick={() => navigate('/')}>
              <HomeOutlined /> Back Home
            </Button>
            <Button onClick={() => navigate('/app/dashboard')}>
              <RocketOutlined /> Go to Dashboard
            </Button>
          </Space>
        }
      >
        <Paragraph style={{ textAlign: 'center', color: '#666' }}>
          The page you're looking for might have been moved, deleted, or doesn't exist.
        </Paragraph>
      </Result>
    </div>
  );
};

export default NotFoundPage;
