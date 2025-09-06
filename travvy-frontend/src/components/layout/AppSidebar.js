/**
 * App Sidebar
 * 
 * Navigation sidebar with all app sections
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Typography, Space } from 'antd';
import {
  DashboardOutlined,
  CalendarOutlined,
  PlusOutlined,
  MessageOutlined,
  UserOutlined,
  TeamOutlined,
  SettingOutlined,
  RocketOutlined,
  CompassOutlined,
} from '@ant-design/icons';

const { Sider } = Layout;
const { Title } = Typography;

const AppSidebar = ({ collapsed }) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Get current selected key based on pathname
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.includes('/dashboard')) return 'dashboard';
    if (path.includes('/trips/new')) return 'new-trip';
    if (path.includes('/trips')) return 'my-trips';
    if (path.includes('/ai-chat')) return 'ai-chat';
    if (path.includes('/profile')) return 'profile';
    if (path.includes('/settings')) return 'settings';
    return 'dashboard';
  };

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      onClick: () => navigate('/app/dashboard'),
    },
    {
      type: 'divider',
    },
    {
      key: 'trip-section',
      label: 'Trip Planning',
      type: 'group',
    },
    {
      key: 'new-trip',
      icon: <PlusOutlined />,
      label: 'Create Trip',
      onClick: () => navigate('/app/trips/new'),
    },
    {
      key: 'my-trips',
      icon: <CalendarOutlined />,
      label: 'My Trips',
      onClick: () => navigate('/app/trips'),
    },
    {
      key: 'ai-chat',
      icon: <MessageOutlined />,
      label: 'AI Assistant',
      onClick: () => navigate('/app/ai-chat'),
    },
    {
      type: 'divider',
    },
    {
      key: 'collaboration-section',
      label: 'Collaboration',
      type: 'group',
    },
    {
      key: 'shared-trips',
      icon: <TeamOutlined />,
      label: 'Shared Trips',
      onClick: () => navigate('/app/trips?filter=shared'),
    },
    {
      type: 'divider',
    },
    {
      key: 'account-section',
      label: 'Account',
      type: 'group',
    },
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
  ];

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={() => {}} // Controlled by parent
      trigger={null}
      theme="light"
      width={240}
      style={{
        borderRight: '1px solid #f0f0f0',
      }}
    >
      {/* Logo/Brand */}
      <div
        style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          padding: collapsed ? '0' : '0 24px',
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        {collapsed ? (
          <RocketOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
        ) : (
          <Space>
            <RocketOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
            <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
              Travvy
            </Title>
          </Space>
        )}
      </div>

      {/* Navigation Menu */}
      <Menu
        mode="inline"
        selectedKeys={[getSelectedKey()]}
        items={menuItems}
        style={{
          border: 'none',
          height: 'calc(100vh - 64px)',
          overflowY: 'auto',
        }}
      />
    </Sider>
  );
};

export default AppSidebar;
