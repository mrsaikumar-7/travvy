/**
 * App Header
 * 
 * Header component with navigation controls, user menu, and notifications
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout,
  Button,
  Avatar,
  Dropdown,
  Badge,
  Space,
  Typography,
  Tooltip,
} from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  PlusOutlined,
  MessageOutlined,
} from '@ant-design/icons';

const { Header } = Layout;
const { Text } = Typography;

const AppHeader = ({ collapsed, setCollapsed, user, onLogout }) => {
  const navigate = useNavigate();

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => navigate('/app/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate('/app/settings'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: onLogout,
    },
  ];

  const notificationMenuItems = [
    {
      key: 'trip-ready',
      label: (
        <div>
          <Text strong>Trip Ready!</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            Your Paris trip is ready to explore
          </Text>
        </div>
      ),
    },
    {
      key: 'collaboration-invite',
      label: (
        <div>
          <Text strong>Collaboration Invite</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            John invited you to collaborate on Tokyo trip
          </Text>
        </div>
      ),
    },
    {
      type: 'divider',
    },
    {
      key: 'view-all',
      label: 'View All Notifications',
      onClick: () => navigate('/app/notifications'),
    },
  ];

  return (
    <Header
      style={{
        background: '#fff',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #f0f0f0',
        height: '64px',
      }}
    >
      {/* Left Side - Collapse Toggle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <Button
          type="text"
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={() => setCollapsed(!collapsed)}
          style={{
            fontSize: '16px',
            width: 40,
            height: 40,
          }}
        />
      </div>

      {/* Right Side - Actions and User Menu */}
      <Space size="middle">
        {/* Quick Actions */}
        <Tooltip title="Create New Trip">
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/app/trips/new')}
          >
            New Trip
          </Button>
        </Tooltip>

        <Tooltip title="AI Chat">
          <Button
            type="text"
            icon={<MessageOutlined />}
            onClick={() => navigate('/app/ai-chat')}
            style={{ fontSize: '16px' }}
          />
        </Tooltip>

        {/* Notifications */}
        <Dropdown
          menu={{ items: notificationMenuItems }}
          trigger={['click']}
          placement="bottomRight"
        >
          <Badge count={2} size="small">
            <Button
              type="text"
              icon={<BellOutlined />}
              style={{ fontSize: '16px' }}
            />
          </Badge>
        </Dropdown>

        {/* User Menu */}
        <Dropdown
          menu={{ items: userMenuItems }}
          trigger={['click']}
          placement="bottomRight"
        >
          <div style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', gap: '8px' }}>
            <Avatar
              size="small"
              src={user?.photoURL}
              icon={<UserOutlined />}
            />
            <Text style={{ color: '#000' }}>
              {user?.displayName || user?.email?.split('@')[0] || 'User'}
            </Text>
          </div>
        </Dropdown>
      </Space>
    </Header>
  );
};

export default AppHeader;
