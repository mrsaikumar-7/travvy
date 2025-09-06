/**
 * Trip Creation Wizard
 * 
 * Multi-step wizard for creating trips with AI assistance
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Steps,
  Card,
  Button,
  Form,
  Input,
  DatePicker,
  InputNumber,
  Select,
  Checkbox,
  Upload,
  Space,
  Typography,
  Row,
  Col,
  message,
  Divider,
  Tag,
  Progress,
} from 'antd';
import {
  EnvironmentOutlined,
  CalendarOutlined,
  UserOutlined,
  DollarOutlined,
  HeartOutlined,
  CameraOutlined,
  SoundOutlined,
  MessageOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import { useTrips } from '../../context/TripContext';

const { Step } = Steps;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { RangePicker } = DatePicker;
const { Option } = Select;

const TripCreationWizard = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [generatingTrip, setGeneratingTrip] = useState(false);
  const [tripData, setTripData] = useState({});

  const navigate = useNavigate();
  const { createTrip } = useTrips();

  const steps = [
    {
      title: 'Destination & Dates',
      icon: <EnvironmentOutlined />,
      description: 'Where and when do you want to go?',
    },
    {
      title: 'Budget & Travelers',
      icon: <DollarOutlined />,
      description: 'Set your budget and group size',
    },
    {
      title: 'Preferences',
      icon: <HeartOutlined />,
      description: 'Tell us about your travel style',
    },
    {
      title: 'AI Generation',
      icon: <RocketOutlined />,
      description: 'Let AI create your perfect itinerary',
    },
  ];

  const travelStyles = [
    'Adventure', 'Relaxation', 'Culture', 'Food', 'Nightlife', 
    'Nature', 'Photography', 'Shopping', 'History', 'Art'
  ];

  const accommodationTypes = [
    'Hotel', 'Hostel', 'Airbnb', 'Resort', 'Apartment', 'Boutique Hotel'
  ];

  const activityTypes = [
    'Sightseeing', 'Museums', 'Outdoor Activities', 'Food Tours',
    'Nightlife', 'Shopping', 'Cultural Experiences', 'Adventure Sports',
    'Photography', 'Local Markets', 'Festivals', 'Nature Tours'
  ];

  const handleNext = async () => {
    try {
      const values = await form.validateFields();
      setTripData(prev => ({ ...prev, ...values }));
      
      if (currentStep < steps.length - 1) {
        setCurrentStep(currentStep + 1);
      }
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleCreateTrip = async () => {
    try {
      setGeneratingTrip(true);
      
      const finalTripData = {
        ...tripData,
        ...(await form.validateFields()),
      };

      // Prepare trip data for API
      const apiTripData = {
        destination: finalTripData.destination,
        start_date: finalTripData.dates[0].format('YYYY-MM-DD'),
        end_date: finalTripData.dates[1].format('YYYY-MM-DD'),
        budget: finalTripData.budget,
        currency: finalTripData.currency || 'USD',
        travelers: {
          adults: finalTripData.adults || 1,
          children: finalTripData.children || 0,
          infants: finalTripData.infants || 0,
        },
        preferences: {
          travel_style: finalTripData.travelStyle || [],
          accommodation_types: finalTripData.accommodationTypes || [],
          activity_types: finalTripData.activityTypes || [],
          dietary_restrictions: finalTripData.dietaryRestrictions || [],
          accessibility: finalTripData.accessibility || {},
        },
        conversation_context: {
          user_message: finalTripData.additionalNotes || '',
          preferences: finalTripData,
        },
      };

      const result = await createTrip(apiTripData);
      
      if (result.success) {
        message.success('Trip creation started! Redirecting...');
        setTimeout(() => {
          navigate(`/app/trips/${result.trip.trip_id}`);
        }, 2000);
      }
      
    } catch (error) {
      console.error('Failed to create trip:', error);
      message.error('Failed to create trip. Please try again.');
    } finally {
      setGeneratingTrip(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div>
            <Title level={4}>Where would you like to go?</Title>
            <Form.Item
              name="destination"
              rules={[{ required: true, message: 'Please enter a destination' }]}
            >
              <Input
                size="large"
                placeholder="e.g., Paris, France or Tokyo, Japan"
                prefix={<EnvironmentOutlined />}
              />
            </Form.Item>

            <Title level={4} style={{ marginTop: '24px' }}>When are you planning to travel?</Title>
            <Form.Item
              name="dates"
              rules={[{ required: true, message: 'Please select travel dates' }]}
            >
              <RangePicker
                size="large"
                style={{ width: '100%' }}
                format="YYYY-MM-DD"
              />
            </Form.Item>

            <Form.Item name="flexible">
              <Checkbox>My dates are flexible</Checkbox>
            </Form.Item>
          </div>
        );

      case 1:
        return (
          <div>
            <Title level={4}>What's your budget?</Title>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={16}>
                <Form.Item
                  name="budget"
                  rules={[{ required: true, message: 'Please enter your budget' }]}
                >
                  <InputNumber
                    size="large"
                    style={{ width: '100%' }}
                    placeholder="Enter total budget"
                    prefix={<DollarOutlined />}
                    min={100}
                    max={100000}
                  />
                </Form.Item>
              </Col>
              <Col xs={24} sm={8}>
                <Form.Item name="currency" initialValue="USD">
                  <Select size="large">
                    <Option value="USD">USD</Option>
                    <Option value="EUR">EUR</Option>
                    <Option value="GBP">GBP</Option>
                    <Option value="JPY">JPY</Option>
                    <Option value="INR">INR</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Title level={4} style={{ marginTop: '24px' }}>How many travelers?</Title>
            <Row gutter={[16, 16]}>
              <Col xs={8}>
                <Text>Adults</Text>
                <Form.Item name="adults" initialValue={1}>
                  <InputNumber size="large" style={{ width: '100%' }} min={1} max={20} />
                </Form.Item>
              </Col>
              <Col xs={8}>
                <Text>Children</Text>
                <Form.Item name="children" initialValue={0}>
                  <InputNumber size="large" style={{ width: '100%' }} min={0} max={10} />
                </Form.Item>
              </Col>
              <Col xs={8}>
                <Text>Infants</Text>
                <Form.Item name="infants" initialValue={0}>
                  <InputNumber size="large" style={{ width: '100%' }} min={0} max={5} />
                </Form.Item>
              </Col>
            </Row>
          </div>
        );

      case 2:
        return (
          <div>
            <Title level={4}>What's your travel style?</Title>
            <Form.Item name="travelStyle">
              <Checkbox.Group>
                <Row gutter={[8, 8]}>
                  {travelStyles.map(style => (
                    <Col xs={12} sm={8} md={6} key={style}>
                      <Checkbox value={style}>{style}</Checkbox>
                    </Col>
                  ))}
                </Row>
              </Checkbox.Group>
            </Form.Item>

            <Title level={4} style={{ marginTop: '24px' }}>Accommodation preferences</Title>
            <Form.Item name="accommodationTypes">
              <Checkbox.Group>
                <Row gutter={[8, 8]}>
                  {accommodationTypes.map(type => (
                    <Col xs={12} sm={8} key={type}>
                      <Checkbox value={type}>{type}</Checkbox>
                    </Col>
                  ))}
                </Row>
              </Checkbox.Group>
            </Form.Item>

            <Title level={4} style={{ marginTop: '24px' }}>What activities interest you?</Title>
            <Form.Item name="activityTypes">
              <Checkbox.Group>
                <Row gutter={[8, 8]}>
                  {activityTypes.map(activity => (
                    <Col xs={12} sm={8} md={6} key={activity}>
                      <Checkbox value={activity}>{activity}</Checkbox>
                    </Col>
                  ))}
                </Row>
              </Checkbox.Group>
            </Form.Item>

            <Title level={4} style={{ marginTop: '24px' }}>Additional notes (optional)</Title>
            <Form.Item name="additionalNotes">
              <TextArea
                rows={4}
                placeholder="Any specific requirements, dietary restrictions, or preferences..."
              />
            </Form.Item>
          </div>
        );

      case 3:
        return (
          <div style={{ textAlign: 'center' }}>
            {generatingTrip ? (
              <div>
                <div style={{ marginBottom: '24px' }}>
                  <RocketOutlined style={{ fontSize: '64px', color: '#1890ff' }} />
                </div>
                <Title level={3}>Generating Your Perfect Trip!</Title>
                <Paragraph style={{ fontSize: '16px', color: '#666' }}>
                  Our AI is creating a personalized itinerary based on your preferences.
                  This may take a few minutes...
                </Paragraph>
                <Progress percent={75} status="active" />
                <div style={{ marginTop: '24px' }}>
                  <Tag color="processing">Analyzing destination</Tag>
                  <Tag color="processing">Finding activities</Tag>
                  <Tag color="processing">Optimizing routes</Tag>
                </div>
              </div>
            ) : (
              <div>
                <div style={{ marginBottom: '24px' }}>
                  <MessageOutlined style={{ fontSize: '64px', color: '#1890ff' }} />
                </div>
                <Title level={3}>Ready to Create Your Trip?</Title>
                <Paragraph style={{ fontSize: '16px', color: '#666' }}>
                  We'll use AI to create a personalized itinerary based on your preferences.
                  You can always modify and customize it later.
                </Paragraph>
                
                <div style={{ margin: '24px 0' }}>
                  <Space direction="vertical" style={{ width: '100%' }} size="middle">
                    <Tag color="blue">✨ AI-powered recommendations</Tag>
                    <Tag color="green">📍 Optimized routes and timing</Tag>
                    <Tag color="orange">🏨 Curated accommodation options</Tag>
                    <Tag color="purple">🍽️ Local dining suggestions</Tag>
                  </Space>
                </div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div>
      <Card>
        <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
          Create Your AI Trip
        </Title>

        <Steps current={currentStep} style={{ marginBottom: '32px' }}>
          {steps.map(step => (
            <Step
              key={step.title}
              title={step.title}
              description={step.description}
              icon={step.icon}
            />
          ))}
        </Steps>

        <Card style={{ minHeight: '400px', marginBottom: '24px' }}>
          <Form form={form} layout="vertical" size="large">
            {renderStepContent()}
          </Form>
        </Card>

        <div style={{ textAlign: 'center' }}>
          <Space size="large">
            {currentStep > 0 && (
              <Button size="large" onClick={handlePrevious} disabled={generatingTrip}>
                Previous
              </Button>
            )}
            
            {currentStep < steps.length - 1 ? (
              <Button type="primary" size="large" onClick={handleNext} disabled={generatingTrip}>
                Next
              </Button>
            ) : (
              <Button
                type="primary"
                size="large"
                onClick={handleCreateTrip}
                loading={generatingTrip}
                icon={<RocketOutlined />}
              >
                {generatingTrip ? 'Creating Trip...' : 'Generate My Trip'}
              </Button>
            )}

            <Button onClick={() => navigate('/app/trips')} disabled={generatingTrip}>
              Cancel
            </Button>
          </Space>
        </div>
      </Card>
    </div>
  );
};

export default TripCreationWizard;
