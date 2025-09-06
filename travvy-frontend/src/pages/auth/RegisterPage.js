/**
 * Register Page
 * 
 * User registration form with email/password and Google OAuth
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
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

const RegisterPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { register, googleLogin } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (values) => {
    setLoading(true);
    setError('');

    const { confirmPassword, ...userData } = values;
    const result = await register({
      ...userData,
      display_name: values.displayName,
    });
    
    if (result.success) {
      navigate('/app/dashboard');
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
      console.log('Google OAuth registration initiated');
      setError('Google OAuth integration coming soon!');
    } catch (error) {
      setError('Google registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <Title level={2}>Create Your Account</Title>
        <Text type="secondary">
          Join Travvy and start planning amazing trips
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
        onFinish={handleRegister}
        size="large"
      >
        <Form.Item
          name="displayName"
          label="Full Name"
          rules={[
            { required: true, message: 'Please enter your full name' },
            { min: 2, message: 'Name must be at least 2 characters' }
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="Enter your full name"
          />
        </Form.Item>

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
            { min: 8, message: 'Password must be at least 8 characters' }
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Enter your password"
          />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          label="Confirm Password"
          dependencies={['password']}
          rules={[
            { required: true, message: 'Please confirm your password' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('Passwords do not match'));
              },
            }),
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Confirm your password"
          />
        </Form.Item>

        <Form.Item
          name="termsAccepted"
          valuePropName="checked"
          rules={[
            {
              validator: (_, value) =>
                value ? Promise.resolve() : Promise.reject(new Error('Please accept the terms')),
            },
          ]}
        >
          <Checkbox>
            I agree to the{' '}
            <Link to="/terms" target="_blank" style={{ color: '#1890ff' }}>
              Terms of Service
            </Link>
            {' '}and{' '}
            <Link to="/privacy" target="_blank" style={{ color: '#1890ff' }}>
              Privacy Policy
            </Link>
          </Checkbox>
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            block
            style={{ height: '48px', fontSize: '16px' }}
          >
            Create Account
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
          Already have an account?{' '}
          <Link to="/auth/login" style={{ color: '#1890ff', fontWeight: '500' }}>
            Sign in
          </Link>
        </Text>
      </div>
    </div>
  );
};

export default RegisterPage;
