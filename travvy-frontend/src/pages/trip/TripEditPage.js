/**
 * Trip Edit Page
 * 
 * Edit existing trip details and itinerary
 */

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Typography, Space, Result } from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';

const { Title } = Typography;

const TripEditPage = () => {
  const { tripId } = useParams();
  const navigate = useNavigate();

  return (
    <div>
      <Card>
        <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }} size="large">
          <Title level={2}>Edit Trip</Title>
          <Result
            title="Trip Editor Coming Soon"
            subTitle={`Trip ID: ${tripId} - This feature will allow you to edit trip details, modify itineraries, and customize your travel plans.`}
            extra={[
              <Button 
                type="primary" 
                key="back" 
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate(`/app/trips/${tripId}`)}
              >
                Back to Trip Details
              </Button>,
              <Button key="save" icon={<SaveOutlined />} disabled>
                Save Changes
              </Button>,
            ]}
          />
        </Space>
      </Card>
    </div>
  );
};

export default TripEditPage;
