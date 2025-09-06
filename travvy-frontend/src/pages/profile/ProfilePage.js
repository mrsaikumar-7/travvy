/**
 * Profile Page
 * 
 * User profile management and preferences
 */

import React from 'react';
import { Card, Typography, Result } from 'antd';
import { UserOutlined } from '@ant-design/icons';

const { Title } = Typography;

const ProfilePage = () => {
  return (
    <div>
      <Card>
        <Result
          icon={<UserOutlined style={{ color: '#1890ff' }} />}
          title="User Profile"
          subTitle="Manage your profile information, travel preferences, and account settings."
        />
      </Card>
    </div>
  );
};

export default ProfilePage;
