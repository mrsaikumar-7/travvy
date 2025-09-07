/**
 * Trip Context
 * 
 * Manages trip-related state and operations throughout the app
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { message } from 'antd';
import { apiService } from '../services/api';

const TripContext = createContext();

export const useTrips = () => {
  const context = useContext(TripContext);
  if (!context) {
    throw new Error('useTrips must be used within a TripProvider');
  }
  return context;
};

export const TripProvider = ({ children }) => {
  const [trips, setTrips] = useState([]);
  const [currentTrip, setCurrentTrip] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generatingTrip, setGeneratingTrip] = useState(false);

  // Load user's trips
  const loadTrips = async (params = {}) => {
    try {
      setLoading(true);
      const response = await apiService.trips.list(params);
      setTrips(response.data.trips);
      return response.data;
    } catch (error) {
      console.error('Failed to load trips:', error);
      message.error('Failed to load trips');
      return { trips: [], has_more: false };
    } finally {
      setLoading(false);
    }
  };

  // Create new trip
  const createTrip = async (tripData) => {
    try {
      setGeneratingTrip(true);
      
      try {
        // Try to create trip with real API
        const response = await apiService.trips.create(tripData);
        
        if (response.data.status === 'generating') {
          message.success('Trip creation started! AI is generating your itinerary...');
          // Optionally poll for completion
          pollTripGeneration(response.data.trip_id || response.data.tripId);
        }
        
        // Add to local state
        const newTrip = { 
          ...response.data, 
          status: response.data.status || 'generating' 
        };
        setTrips(prev => [newTrip, ...prev]);
        
        return { success: true, trip: newTrip };
        
      } catch (apiError) {
        // If API fails, create a mock trip for demo purposes
        console.warn('API call failed, creating mock trip:', apiError);
        
        const mockTrip = {
          tripId: 'demo-trip-' + Date.now(),
          metadata: {
            title: tripData.destination + ' Adventure',
            destination: {
              name: tripData.destination,
              placeId: 'demo-place-id',
              coordinates: { lat: 0, lng: 0 },
              country: 'Demo Country',
              city: 'Demo City',
            },
            dates: {
              startDate: tripData.start_date,
              endDate: tripData.end_date,
              duration: Math.ceil((new Date(tripData.end_date) - new Date(tripData.start_date)) / (1000 * 60 * 60 * 24)),
              flexible: false,
            },
            travelers: tripData.travelers,
            budget: {
              currency: tripData.currency,
              total: tripData.budget,
              breakdown: {
                accommodation: tripData.budget * 0.4,
                transportation: tripData.budget * 0.2,
                food: tripData.budget * 0.3,
                activities: tripData.budget * 0.1,
                miscellaneous: 0,
              },
            },
          },
          status: 'planning',
          collaborators: {
            'demo-user-123': { role: 'owner', joinedAt: new Date(), permissions: [] }
          },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        
        setTrips(prev => [mockTrip, ...prev]);
        message.success('Demo trip created! (API integration in progress)');
        
        return { success: true, trip: mockTrip };
      }
    } catch (error) {
      const errorMessage = error.message || 'Failed to create trip';
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setGeneratingTrip(false);
    }
  };

  // Get trip details
  const getTrip = async (tripId) => {
    try {
      setLoading(true);
      const response = await apiService.trips.get(tripId);
      setCurrentTrip(response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to get trip:', error);
      message.error('Failed to load trip details');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Update trip
  const updateTrip = async (tripId, updateData) => {
    try {
      const response = await apiService.trips.update(tripId, updateData);
      
      // Update local state
      setTrips(prev => 
        prev.map(trip => trip.tripId === tripId ? response.data : trip)
      );
      
      if (currentTrip?.tripId === tripId) {
        setCurrentTrip(response.data);
      }
      
      message.success('Trip updated successfully');
      return { success: true, trip: response.data };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to update trip';
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Delete trip
  const deleteTrip = async (tripId) => {
    try {
      await apiService.trips.delete(tripId);
      
      // Remove from local state
      setTrips(prev => prev.filter(trip => trip.tripId !== tripId));
      
      if (currentTrip?.tripId === tripId) {
        setCurrentTrip(null);
      }
      
      message.success('Trip deleted successfully');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete trip';
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Duplicate trip
  const duplicateTrip = async (tripId) => {
    try {
      const response = await apiService.trips.duplicate(tripId);
      
      // Add duplicated trip to local state
      setTrips(prev => [response.data.trip, ...prev]);
      
      message.success('Trip duplicated successfully');
      return { success: true, trip: response.data.trip };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to duplicate trip';
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Optimize trip
  const optimizeTrip = async (tripId, preferences) => {
    try {
      const response = await apiService.trips.optimize(tripId, preferences);
      message.success('Trip optimization started');
      
      // Optionally poll for completion
      pollOptimization(response.data.task_id);
      
      return { success: true, taskId: response.data.task_id };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to optimize trip';
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Poll trip generation status
  const pollTripGeneration = async (tripId) => {
    const maxAttempts = 60; // 5 minutes with 5-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await apiService.trips.getStatus(tripId);
        
        if (response.data.status === 'completed') {
          message.success('Your trip is ready!');
          // Refresh the trip data
          await getTrip(tripId);
          return;
        }
        
        if (response.data.status === 'failed') {
          message.error('Trip generation failed. Please try again.');
          return;
        }
        
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          message.warning('Trip generation is taking longer than expected. Please check back later.');
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    poll();
  };

  // Poll optimization status
  const pollOptimization = async (taskId) => {
    // Similar polling logic for optimization tasks
    const maxAttempts = 24; // 2 minutes with 5-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await apiService.ai.getTaskStatus(taskId);
        
        if (response.data.status === 'completed') {
          message.success('Trip optimization completed!');
          // Refresh trips
          await loadTrips();
          return;
        }
        
        if (response.data.status === 'failed') {
          message.error('Trip optimization failed. Please try again.');
          return;
        }
        
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000);
        }
      } catch (error) {
        console.error('Optimization polling error:', error);
      }
    };

    poll();
  };

  const value = {
    trips,
    currentTrip,
    loading,
    generatingTrip,
    loadTrips,
    createTrip,
    getTrip,
    updateTrip,
    deleteTrip,
    duplicateTrip,
    optimizeTrip,
    setCurrentTrip,
  };

  return (
    <TripContext.Provider value={value}>
      {children}
    </TripContext.Provider>
  );
};
