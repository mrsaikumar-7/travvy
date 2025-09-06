/**
 * Settings Page
 * 
 * App settings, notifications, and preferences
 */

import React from 'react';
import { Card, Typography, Result } from 'antd';
import { SettingOutlined } from '@ant-design/icons';

const { Title } = Typography;

const SettingsPage = () => {
  return (
    <div>
      <Card>
        <Result
          icon={<SettingOutlined style={{ color: '#1890ff' }} />}
          title="Settings"
          subTitle="Configure app settings, notification preferences, privacy settings, and account options."
        />
      </Card>
    </div>
  );
};

export default SettingsPage;
