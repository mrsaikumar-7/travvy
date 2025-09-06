/**
 * Trip Details Page
 * 
 * View complete trip itinerary with all details
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Typography,
  Space,
  Skeleton,
  Result,
  Tag,
  Timeline,
  Row,
  Col,
  Avatar,
  Divider,
} from 'antd';
import {
  EditOutlined,
  ShareAltOutlined,
  CalendarOutlined,
  EnvironmentOutlined,
  TeamOutlined,
  DollarOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

const TripDetailsPage = () => {
  const { tripId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [trip, setTrip] = useState(null);

  useEffect(() => {
    loadTripDetails();
  }, [tripId]);

  const loadTripDetails = async () => {
    // TODO: Load actual trip data from API
    setTimeout(() => {
      // Mock trip data
      setTrip({
        tripId,
        title: 'Paris Adventure',
        destination: 'Paris, France',
        startDate: '2024-03-15',
        endDate: '2024-03-22',
        status: 'upcoming',
        collaborators: 3,
        budget: 5000,
        currency: 'USD',
      });
      setLoading(false);
    }, 1000);
  };

  if (loading) {
    return (
      <div>
        <Skeleton active paragraph={{ rows: 8 }} />
      </div>
    );
  }

  if (!trip) {
    return (
      <Result
        status="404"
        title="Trip Not Found"
        subTitle="The trip you're looking for doesn't exist or you don't have access to it."
        extra={
          <Button type="primary" onClick={() => navigate('/app/trips')}>
            Back to My Trips
          </Button>
        }
      />
    );
  }

  return (
    <div>
      {/* Header */}
      <Card style={{ marginBottom: '24px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space direction="vertical" size="small">
              <Title level={2} style={{ margin: 0 }}>
                {trip.title}
              </Title>
              <Space>
                <Tag color="blue" icon={<EnvironmentOutlined />}>
                  {trip.destination}
                </Tag>
                <Tag color="green" icon={<CalendarOutlined />}>
                  {new Date(trip.startDate).toLocaleDateString()} - {new Date(trip.endDate).toLocaleDateString()}
                </Tag>
                <Tag color="orange" icon={<TeamOutlined />}>
                  {trip.collaborators} collaborators
                </Tag>
                <Tag color="purple" icon={<DollarOutlined />}>
                  {trip.currency} {trip.budget}
                </Tag>
              </Space>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<ShareAltOutlined />}
                onClick={() => navigate(`/app/trips/${tripId}/collaborate`)}
              >
                Share
              </Button>
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => navigate(`/app/trips/${tripId}/edit`)}
              >
                Edit Trip
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Trip Content - Placeholder */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Itinerary" style={{ marginBottom: '16px' }}>
            <Timeline
              items={[
                {
                  dot: <ClockCircleOutlined style={{ fontSize: '16px' }} />,
                  children: (
                    <div>
                      <Title level={5}>Day 1 - Arrival in Paris</Title>
                      <Paragraph>
                        Arrive at Charles de Gaulle Airport, check into hotel, explore the neighborhood.
                      </Paragraph>
                    </div>
                  ),
                },
                {
                  dot: <ClockCircleOutlined style={{ fontSize: '16px' }} />,
                  children: (
                    <div>
                      <Title level={5}>Day 2 - Eiffel Tower & Louvre</Title>
                      <Paragraph>
                        Visit iconic landmarks and world-famous museum.
                      </Paragraph>
                    </div>
                  ),
                },
                {
                  dot: <ClockCircleOutlined style={{ fontSize: '16px' }} />,
                  children: (
                    <div>
                      <Title level={5}>Day 3 - Montmartre & Sacré-Cœur</Title>
                      <Paragraph>
                        Explore the artistic district and beautiful basilica.
                      </Paragraph>
                    </div>
                  ),
                },
              ]}
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card title="Trip Overview" style={{ marginBottom: '16px' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Duration:</Text>
                <br />
                <Text>7 days, 6 nights</Text>
              </div>
              <Divider />
              <div>
                <Text strong>Weather:</Text>
                <br />
                <Text>Spring weather, 15-20°C</Text>
              </div>
              <Divider />
              <div>
                <Text strong>Best for:</Text>
                <br />
                <Space wrap>
                  <Tag>Culture</Tag>
                  <Tag>Photography</Tag>
                  <Tag>Food</Tag>
                </Space>
              </div>
            </Space>
          </Card>

          <Card title="Collaborators">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Avatar>JD</Avatar>
                <div>
                  <div><Text strong>John Doe</Text></div>
                  <div><Text type="secondary" style={{ fontSize: '12px' }}>Owner</Text></div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Avatar>AS</Avatar>
                <div>
                  <div><Text strong>Alice Smith</Text></div>
                  <div><Text type="secondary" style={{ fontSize: '12px' }}>Editor</Text></div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Avatar>BJ</Avatar>
                <div>
                  <div><Text strong>Bob Johnson</Text></div>
                  <div><Text type="secondary" style={{ fontSize: '12px' }}>Viewer</Text></div>
                </div>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default TripDetailsPage;
