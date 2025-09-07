/**
 * My Trips Page
 * 
 * List of all user's trips with filtering, searching, and management options
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Row,
  Col,
  Card,
  Button,
  Input,
  Select,
  Typography,
  Space,
  Tag,
  Avatar,
  Dropdown,
  Modal,
  message,
  Empty,
  Spin,
  Progress,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  FilterOutlined,
  MoreOutlined,
  CalendarOutlined,
  TeamOutlined,
  EditOutlined,
  CopyOutlined,
  DeleteOutlined,
  ShareAltOutlined,
  EyeOutlined,
} from '@ant-design/icons';

import { useTrips } from '../../context/TripContext';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;

const MyTripsPage = () => {
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [tripToDelete, setTripToDelete] = useState(null);

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { trips, loadTrips, deleteTrip, duplicateTrip } = useTrips();

  useEffect(() => {
    loadTripsData();
  }, [searchQuery, statusFilter, sortBy]);

  useEffect(() => {
    // Check for filter from URL params
    const filter = searchParams.get('filter');
    if (filter === 'shared') {
      setStatusFilter('shared');
    }
  }, [searchParams]);

  const loadTripsData = async () => {
    setLoading(true);
    try {
      await loadTrips({
        search: searchQuery,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        sort: sortBy,
      });
    } finally {
      setLoading(false);
    }
  };

  const displayTrips = trips; // Use real trip data from context

  const calculateProgress = (trip) => {
    if (trip.status === 'completed') return 100;
    if (trip.status === 'generating') return 25;
    if (trip.status === 'planning') return 50;
    if (trip.itinerary && trip.itinerary.length > 0) return 75;
    return 25;
  };

  const getStatusColor = (status) => {
    const colors = {
      planning: 'orange',
      upcoming: 'blue',
      'in-progress': 'green',
      completed: 'green',
      cancelled: 'red',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status) => {
    const texts = {
      planning: 'Planning',
      upcoming: 'Upcoming',
      'in-progress': 'In Progress',
      completed: 'Completed',
      cancelled: 'Cancelled',
    };
    return texts[status] || status;
  };

  const handleTripAction = (action, trip) => {
    switch (action) {
      case 'view':
        navigate(`/app/trips/${trip.tripId}`);
        break;
      case 'edit':
        navigate(`/app/trips/${trip.tripId}/edit`);
        break;
      case 'duplicate':
        handleDuplicateTrip(trip.tripId);
        break;
      case 'share':
        handleShareTrip(trip.tripId);
        break;
      case 'delete':
        setTripToDelete(trip);
        setDeleteModalVisible(true);
        break;
      default:
        break;
    }
  };

  const handleDuplicateTrip = async (tripId) => {
    const result = await duplicateTrip(tripId);
    if (result.success) {
      message.success('Trip duplicated successfully');
      loadTripsData();
    }
  };

  const handleShareTrip = (tripId) => {
    navigate(`/app/trips/${tripId}/collaborate`);
  };

  const handleDeleteTrip = async () => {
    if (!tripToDelete) return;
    
    const result = await deleteTrip(tripToDelete.tripId);
    if (result.success) {
      message.success('Trip deleted successfully');
      loadTripsData();
    }
    
    setDeleteModalVisible(false);
    setTripToDelete(null);
  };

  const getActionMenuItems = (trip) => [
    {
      key: 'view',
      icon: <EyeOutlined />,
      label: 'View Trip',
      onClick: () => handleTripAction('view', trip),
    },
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: 'Edit Trip',
      onClick: () => handleTripAction('edit', trip),
    },
    {
      key: 'duplicate',
      icon: <CopyOutlined />,
      label: 'Duplicate',
      onClick: () => handleTripAction('duplicate', trip),
    },
    {
      key: 'share',
      icon: <ShareAltOutlined />,
      label: 'Share & Collaborate',
      onClick: () => handleTripAction('share', trip),
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: 'Delete',
      danger: true,
      onClick: () => handleTripAction('delete', trip),
    },
  ];

  return (
    <div>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>My Trips</Title>
          <Text type="secondary">
            Plan, organize, and manage all your travel adventures
          </Text>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            size="large"
            onClick={() => navigate('/app/trips/new')}
          >
            Create New Trip
          </Button>
        </Col>
      </Row>

      {/* Filters and Search */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="Search trips..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onSearch={loadTripsData}
              allowClear
            />
          </Col>
          <Col xs={12} sm={6} md={4}>
            <Select
              placeholder="Status"
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: '100%' }}
            >
              <Option value="all">All Status</Option>
              <Option value="planning">Planning</Option>
              <Option value="upcoming">Upcoming</Option>
              <Option value="in-progress">In Progress</Option>
              <Option value="completed">Completed</Option>
              <Option value="shared">Shared with Me</Option>
            </Select>
          </Col>
          <Col xs={12} sm={6} md={4}>
            <Select
              placeholder="Sort by"
              value={sortBy}
              onChange={setSortBy}
              style={{ width: '100%' }}
            >
              <Option value="recent">Most Recent</Option>
              <Option value="alphabetical">Alphabetical</Option>
              <Option value="date">Travel Date</Option>
              <Option value="status">Status</Option>
            </Select>
          </Col>
        </Row>
      </Card>

      {/* Trips Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" tip="Loading trips..." />
        </div>
      ) : displayTrips.length > 0 ? (
        <Row gutter={[16, 16]}>
          {displayTrips.map((trip) => (
            <Col xs={24} sm={12} lg={8} xl={6} key={trip.tripId}>
              <Card
                hoverable
                style={{ height: '100%' }}
                cover={
                  <div
                    style={{
                      height: '160px',
                      background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '18px',
                      fontWeight: '500',
                    }}
                  >
                    {trip.metadata?.destination?.name || 'Unknown Destination'}
                  </div>
                }
                actions={[
                  <Tooltip title="View Trip">
                    <Button
                      type="text"
                      icon={<EyeOutlined />}
                      onClick={() => handleTripAction('view', trip)}
                    />
                  </Tooltip>,
                  <Tooltip title="Edit Trip">
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      onClick={() => handleTripAction('edit', trip)}
                    />
                  </Tooltip>,
                  <Dropdown
                    menu={{ items: getActionMenuItems(trip) }}
                    trigger={['click']}
                  >
                    <Button type="text" icon={<MoreOutlined />} />
                  </Dropdown>,
                ]}
              >
                <Card.Meta
                  title={
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      <Text strong ellipsis style={{ fontSize: '16px' }}>
                        {trip.metadata?.title || 'Untitled Trip'}
                      </Text>
                      <Tag color={getStatusColor(trip.status)}>
                        {getStatusText(trip.status)}
                      </Tag>
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      <div>
                        <CalendarOutlined style={{ marginRight: '4px' }} />
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {trip.metadata?.dates?.startDate ? new Date(trip.metadata.dates.startDate).toLocaleDateString() : 'N/A'} - {' '}
                          {trip.metadata?.dates?.endDate ? new Date(trip.metadata.dates.endDate).toLocaleDateString() : 'N/A'}
                        </Text>
                      </div>
                      <div>
                        <TeamOutlined style={{ marginRight: '4px' }} />
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {Object.keys(trip.collaborators || {}).length} collaborators
                        </Text>
                      </div>
                      <Progress
                        percent={calculateProgress(trip)}
                        size="small"
                        showInfo={false}
                        strokeColor="#1890ff"
                      />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {calculateProgress(trip)}% planned
                      </Text>
                    </Space>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      ) : (
        <Card>
          <Empty
            description="No trips found"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" onClick={() => navigate('/app/trips/new')}>
              Create Your First Trip
            </Button>
          </Empty>
        </Card>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        title="Delete Trip"
        open={deleteModalVisible}
        onOk={handleDeleteTrip}
        onCancel={() => {
          setDeleteModalVisible(false);
          setTripToDelete(null);
        }}
        okText="Delete"
        okType="danger"
        cancelText="Cancel"
      >
        <p>
          Are you sure you want to delete "{tripToDelete?.metadata?.title}"? 
          This action cannot be undone.
        </p>
      </Modal>
    </div>
  );
};

export default MyTripsPage;
