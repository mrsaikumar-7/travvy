/**
 * Dashboard Page
 * 
 * Main dashboard with overview of user's trips, recent activity, and quick actions
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Row,
  Col,
  Card,
  Statistic,
  Button,
  Typography,
  List,
  Avatar,
  Space,
  Progress,
  Tag,
  Empty,
  Spin,
} from 'antd';
import {
  PlusOutlined,
  CalendarOutlined,
  TeamOutlined,
  GlobalOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  MessageOutlined,
} from '@ant-design/icons';

import { useAuth } from '../../context/AuthContext';
import { useTrips } from '../../context/TripContext';
import ApiTestComponent from '../../components/ui/ApiTestComponent';
import IntegrationStatus from '../../components/ui/IntegrationStatus';

const { Title, Text, Paragraph } = Typography;

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalTrips: 0,
    upcomingTrips: 0,
    sharedTrips: 0,
    countriesVisited: 0,
  });

  const navigate = useNavigate();
  const { user } = useAuth();
  const { trips, loadTrips } = useTrips();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load recent trips
      await loadTrips({ limit: 5 });
      
      // Calculate stats (mock data for now)
      setStats({
        totalTrips: 12,
        upcomingTrips: 3,
        sharedTrips: 5,
        countriesVisited: 8,
      });
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const recentTrips = [
    {
      id: '1',
      title: 'Paris Adventure',
      destination: 'Paris, France',
      status: 'upcoming',
      startDate: '2024-03-15',
      collaborators: 3,
      progress: 85,
    },
    {
      id: '2',
      title: 'Tokyo Explorer',
      destination: 'Tokyo, Japan', 
      status: 'planning',
      startDate: '2024-04-20',
      collaborators: 1,
      progress: 45,
    },
    {
      id: '3',
      title: 'Bali Retreat',
      destination: 'Bali, Indonesia',
      status: 'completed',
      startDate: '2024-01-10',
      collaborators: 2,
      progress: 100,
    },
  ];

  const recentActivity = [
    {
      id: '1',
      type: 'trip_created',
      message: 'Created new trip "Paris Adventure"',
      time: '2 hours ago',
      icon: <PlusOutlined style={{ color: '#1890ff' }} />,
    },
    {
      id: '2',
      type: 'collaboration',
      message: 'John shared "Tokyo Explorer" with you',
      time: '5 hours ago',
      icon: <TeamOutlined style={{ color: '#52c41a' }} />,
    },
    {
      id: '3',
      type: 'ai_generated',
      message: 'AI completed itinerary for "Bali Retreat"',
      time: '1 day ago',
      icon: <MessageOutlined style={{ color: '#722ed1' }} />,
    },
  ];

  const getStatusColor = (status) => {
    const colors = {
      upcoming: 'blue',
      planning: 'orange',
      completed: 'green',
      cancelled: 'red',
    };
    return colors[status] || 'default';
  };

  const getStatusIcon = (status) => {
    const icons = {
      upcoming: <CalendarOutlined />,
      planning: <ClockCircleOutlined />,
      completed: <CheckCircleOutlined />,
    };
    return icons[status] || <ClockCircleOutlined />;
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" tip="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div>
      {/* Integration Status */}
      <IntegrationStatus />

      {/* Welcome Section */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          Welcome back, {user?.displayName?.split(' ')[0] || 'Traveler'}! 👋
        </Title>
        <Paragraph style={{ fontSize: '16px', color: '#666' }}>
          Ready to plan your next amazing adventure?
        </Paragraph>
      </div>

      {/* Stats Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Total Trips"
              value={stats.totalTrips}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Upcoming"
              value={stats.upcomingTrips}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Shared Trips"
              value={stats.sharedTrips}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Countries"
              value={stats.countriesVisited}
              prefix={<GlobalOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Recent Trips */}
        <Col xs={24} lg={16}>
          <Card
            title="Recent Trips"
            extra={
              <Button type="link" onClick={() => navigate('/app/trips')}>
                View All
              </Button>
            }
          >
            {recentTrips.length > 0 ? (
              <List
                itemLayout="horizontal"
                dataSource={recentTrips}
                renderItem={(trip) => (
                  <List.Item
                    actions={[
                      <Button
                        type="link"
                        onClick={() => navigate(`/app/trips/${trip.id}`)}
                      >
                        View
                      </Button>,
                    ]}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar
                          style={{
                            backgroundColor: getStatusColor(trip.status) === 'blue' ? '#1890ff' : 
                                           getStatusColor(trip.status) === 'green' ? '#52c41a' : '#fa8c16'
                          }}
                          icon={getStatusIcon(trip.status)}
                        />
                      }
                      title={
                        <Space>
                          <Text strong>{trip.title}</Text>
                          <Tag color={getStatusColor(trip.status)}>
                            {trip.status}
                          </Tag>
                        </Space>
                      }
                      description={
                        <div>
                          <div>{trip.destination}</div>
                          <div style={{ marginTop: '8px' }}>
                            <Progress percent={trip.progress} size="small" />
                            <Text type="secondary" style={{ fontSize: '12px', marginTop: '4px' }}>
                              {trip.collaborators} collaborators
                            </Text>
                          </div>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty
                description="No trips yet"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Button type="primary" onClick={() => navigate('/app/trips/new')}>
                  Create Your First Trip
                </Button>
              </Empty>
            )}
          </Card>
        </Col>

        {/* Quick Actions & Recent Activity */}
        <Col xs={24} lg={8}>
          {/* Quick Actions */}
          <Card title="Quick Actions" style={{ marginBottom: '16px' }}>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Button
                type="primary"
                icon={<PlusOutlined />}
                block
                size="large"
                onClick={() => navigate('/app/trips/new')}
              >
                Create New Trip
              </Button>
              <Button
                icon={<MessageOutlined />}
                block
                onClick={() => navigate('/app/ai-chat')}
              >
                Chat with AI Assistant
              </Button>
              <Button
                icon={<TeamOutlined />}
                block
                onClick={() => navigate('/app/trips?filter=shared')}
              >
                View Shared Trips
              </Button>
            </Space>
          </Card>

          {/* Recent Activity */}
          <Card title="Recent Activity">
            <List
              size="small"
              dataSource={recentActivity}
              renderItem={(activity) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={activity.icon}
                    title={
                      <Text style={{ fontSize: '14px' }}>
                        {activity.message}
                      </Text>
                    }
                    description={
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {activity.time}
                      </Text>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
