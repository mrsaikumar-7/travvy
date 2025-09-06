/**
 * Login Page
 * 
 * User login form with email/password and Google OAuth
 */

import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  Form,
  Input,
  Button,
  Typography,
  Space,
  Divider,
  Alert,
  Checkbox,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  GoogleOutlined,
  MailOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';

const { Title, Text } = Typography;

const LoginPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login, googleLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Get the redirect URL from location state
  const from = location.state?.from?.pathname || '/app/dashboard';

  const handleLogin = async (values) => {
    setLoading(true);
    setError('');

    const result = await login(values);
    
    if (result.success) {
      navigate(from, { replace: true });
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError('');

    try {
      // TODO: Implement actual Google OAuth integration
      // This is a placeholder for Google OAuth flow
      console.log('Google OAuth login initiated');
      
      // For now, show a message
      setError('Google OAuth integration coming soon!');
    } catch (error) {
      setError('Google login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <Title level={2}>Welcome Back</Title>
        <Text type="secondary">
          Sign in to continue planning your amazing trips
        </Text>
      </div>

      {error && (
        <Alert
          message={error}
          type="error"
          style={{ marginBottom: '24px' }}
          closable
          onClose={() => setError('')}
        />
      )}

      <Form
        form={form}
        layout="vertical"
        onFinish={handleLogin}
        size="large"
      >
        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: 'Please enter your email' },
            { type: 'email', message: 'Please enter a valid email' }
          ]}
        >
          <Input
            prefix={<MailOutlined />}
            placeholder="Enter your email"
          />
        </Form.Item>

        <Form.Item
          name="password"
          label="Password"
          rules={[
            { required: true, message: 'Please enter your password' },
            { min: 6, message: 'Password must be at least 6 characters' }
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Enter your password"
          />
        </Form.Item>

        <Form.Item>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>Remember me</Checkbox>
            </Form.Item>
            <Link to="/auth/forgot-password" style={{ color: '#1890ff' }}>
              Forgot password?
            </Link>
          </div>
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            block
            style={{ height: '48px', fontSize: '16px' }}
          >
            Sign In
          </Button>
        </Form.Item>
      </Form>

      <Divider>
        <Text type="secondary">Or continue with</Text>
      </Divider>

      <Button
        icon={<GoogleOutlined />}
        onClick={handleGoogleLogin}
        loading={loading}
        block
        style={{
          height: '48px',
          fontSize: '16px',
          marginBottom: '24px',
          borderColor: '#d9d9d9',
        }}
      >
        Continue with Google
      </Button>

      <div style={{ textAlign: 'center' }}>
        <Text type="secondary">
          Don't have an account?{' '}
          <Link to="/auth/register" style={{ color: '#1890ff', fontWeight: '500' }}>
            Sign up now
          </Link>
        </Text>
      </div>

      {/* Demo Credentials */}
      <div style={{ marginTop: '32px', padding: '16px', background: '#f5f5f5', borderRadius: '8px' }}>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          <strong>Demo Credentials:</strong><br />
          Email: demo@Travvy.com<br />
          Password: demo123
        </Text>
      </div>
    </div>
  );
};

export default LoginPage;
