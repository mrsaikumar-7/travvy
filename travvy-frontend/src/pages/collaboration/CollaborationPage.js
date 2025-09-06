/**
 * Collaboration Page
 * 
 * Real-time collaborative trip planning
 */

import React from 'react';
import { useParams } from 'react-router-dom';
import { Card, Typography, Result } from 'antd';
import { TeamOutlined } from '@ant-design/icons';

const { Title } = Typography;

const CollaborationPage = () => {
  const { tripId } = useParams();

  return (
    <div>
      <Card>
        <Result
          icon={<TeamOutlined style={{ color: '#1890ff' }} />}
          title="Real-time Collaboration"
          subTitle={`Trip ID: ${tripId} - This feature will enable real-time collaborative trip planning with live cursors, voting, and instant updates.`}
        />
      </Card>
    </div>
  );
};

export default CollaborationPage;
