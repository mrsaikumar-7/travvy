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
  Progress,
  message,
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
import { useTrips } from '../../context/TripContext';

const { Title, Text, Paragraph } = Typography;

const TripDetailsPage = () => {
  const { tripId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [trip, setTrip] = useState(null);
  const { getTrip, currentTrip } = useTrips();

  useEffect(() => {
    loadTripDetails();
  }, [tripId]);

  const loadTripDetails = async () => {
    try {
      setLoading(true);
      const tripData = await getTrip(tripId);
      if (tripData) {
        setTrip(tripData);
      } else {
        // If API fails, try to use currentTrip if it matches
        if (currentTrip && currentTrip.tripId === tripId) {
          setTrip(currentTrip);
        }
      }
    } catch (error) {
      console.error('Failed to load trip details:', error);
      message.error('Failed to load trip details');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      planning: 'orange',
      generating: 'blue',
      completed: 'green',
      upcoming: 'blue',
      'in-progress': 'green',
      cancelled: 'red',
    };
    return colors[status] || 'default';
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
                {trip.metadata?.title || 'Untitled Trip'}
              </Title>
              <Space wrap>
                <Tag color="blue" icon={<EnvironmentOutlined />}>
                  {trip.metadata?.destination?.name || 'Unknown Destination'}
                </Tag>
                <Tag color="green" icon={<CalendarOutlined />}>
                  {formatDate(trip.metadata?.dates?.startDate)} - {formatDate(trip.metadata?.dates?.endDate)}
                </Tag>
                <Tag color={getStatusColor(trip.status)} icon={<ClockCircleOutlined />}>
                  {trip.status}
                </Tag>
                <Tag color="orange" icon={<TeamOutlined />}>
                  {Object.keys(trip.collaborators || {}).length} collaborators
                </Tag>
                <Tag color="purple" icon={<DollarOutlined />}>
                  {trip.metadata?.budget?.currency || 'USD'} {trip.metadata?.budget?.total || 'N/A'}
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

      {/* Trip Content */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Itinerary" style={{ marginBottom: '16px' }}>
            {trip.status === 'generating' ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Progress percent={75} status="active" />
                <div style={{ marginTop: '16px' }}>
                  <Text>AI is generating your itinerary...</Text>
                </div>
              </div>
            ) : trip.itinerary && trip.itinerary.length > 0 ? (
              <Timeline>
                {trip.itinerary.map((day, index) => (
                  <Timeline.Item
                    key={index}
                    dot={<ClockCircleOutlined style={{ fontSize: '16px' }} />}
                  >
                    <div>
                      <Title level={5}>
                        Day {day.day} - {day.theme || formatDate(day.date)}
                      </Title>
                      {day.activities && day.activities.length > 0 && (
                        <div style={{ marginBottom: '12px' }}>
                          <Text strong>Activities:</Text>
                          <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                            {day.activities.map((activity, actIndex) => (
                              <li key={actIndex}>
                                <Text>{activity.name}</Text>
                                {activity.description && (
                                  <div style={{ marginLeft: '0px', marginTop: '4px' }}>
                                    <Text type="secondary" style={{ fontSize: '12px' }}>
                                      {activity.description}
                                    </Text>
                                  </div>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {day.meals && day.meals.length > 0 && (
                        <div style={{ marginBottom: '12px' }}>
                          <Text strong>Meals:</Text>
                          <div style={{ marginTop: '8px' }}>
                            {day.meals.map((meal, mealIndex) => (
                              <Tag key={mealIndex} style={{ margin: '2px' }}>
                                {meal.type}: {meal.restaurant}
                              </Tag>
                            ))}
                          </div>
                        </div>
                      )}
                      {day.totalBudget && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          Estimated cost: {trip.metadata?.budget?.currency || 'USD'} {day.totalBudget}
                        </Text>
                      )}
                      {day.notes && (
                        <Paragraph type="secondary" style={{ marginTop: '8px', fontSize: '12px' }}>
                          {day.notes}
                        </Paragraph>
                      )}
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Text type="secondary">No itinerary available yet</Text>
              </div>
            )}
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card title="Trip Overview" style={{ marginBottom: '16px' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Duration:</Text>
                <br />
                <Text>
                  {trip.metadata?.dates?.duration || 'N/A'} days
                  {trip.metadata?.dates?.startDate && trip.metadata?.dates?.endDate && (
                    `, ${Math.max(0, (trip.metadata.dates.duration || 1) - 1)} nights`
                  )}
                </Text>
              </div>
              <Divider />
              <div>
                <Text strong>Travelers:</Text>
                <br />
                <Text>
                  {trip.metadata?.travelers?.adults || 0} adults
                  {(trip.metadata?.travelers?.children || 0) > 0 && `, ${trip.metadata.travelers.children} children`}
                  {(trip.metadata?.travelers?.infants || 0) > 0 && `, ${trip.metadata.travelers.infants} infants`}
                </Text>
              </div>
              <Divider />
              <div>
                <Text strong>Budget Breakdown:</Text>
                <br />
                <Space direction="vertical" style={{ width: '100%', marginTop: '8px' }}>
                  {trip.metadata?.budget?.breakdown && Object.entries(trip.metadata.budget.breakdown).map(([category, amount]) => (
                    <div key={category} style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text style={{ textTransform: 'capitalize' }}>{category}:</Text>
                      <Text>{trip.metadata.budget.currency} {Number(amount).toFixed(2)}</Text>
                    </div>
                  ))}
                </Space>
              </div>
              {trip.status === 'completed' && (
                <>
                  <Divider />
                  <div>
                    <Text strong>AI Generation:</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      Generated by {trip.aiGeneration?.model || 'AI'} 
                      {trip.aiGeneration?.confidence && ` (${Math.round(trip.aiGeneration.confidence * 100)}% confidence)`}
                    </Text>
                  </div>
                </>
              )}
            </Space>
          </Card>

          {/* Hotels Section */}
          {trip.hotels && trip.hotels.length > 0 && (
            <Card title="Hotel Recommendations" style={{ marginBottom: '16px' }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                {trip.hotels.slice(0, 3).map((hotel, index) => (
                  <div key={hotel.hotelId || index}>
                    <div>
                      <Text strong>{hotel.name}</Text>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          ⭐ {hotel.rating} • {hotel.location?.name}
                        </Text>
                        <Text style={{ fontSize: '12px' }}>
                          {trip.metadata?.budget?.currency} {hotel.pricePerNight}/night
                        </Text>
                      </div>
                    </div>
                    {index < Math.min(trip.hotels.length, 3) - 1 && <Divider />}
                  </div>
                ))}
              </Space>
            </Card>
          )}

          <Card title="Collaborators">
            <Space direction="vertical" style={{ width: '100%' }}>
              {Object.entries(trip.collaborators || {}).map(([userId, collaborator]) => {
                const initials = userId.slice(0, 2).toUpperCase();
                return (
                  <div key={userId} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Avatar>{initials}</Avatar>
                    <div>
                      <div><Text strong>{userId}</Text></div>
                      <div><Text type="secondary" style={{ fontSize: '12px', textTransform: 'capitalize' }}>
                        {collaborator.role || 'Member'}
                      </Text></div>
                    </div>
                  </div>
                );
              })}
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default TripDetailsPage;
