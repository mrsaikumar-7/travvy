/**
 * Application Constants
 * 
 * Centralized constants for Travvy
 */

export const APP_CONFIG = {
  name: 'Travvy',
  version: '1.0.0',
  description: 'AI-powered trip planning platform',
};

export const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
};

export const TRIP_STATUS = {
  PLANNING: 'planning',
  UPCOMING: 'upcoming',
  IN_PROGRESS: 'in-progress',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
};

export const COLLABORATION_ROLES = {
  OWNER: 'owner',
  EDITOR: 'editor',
  VIEWER: 'viewer',
};

export const TRAVEL_STYLES = [
  'Adventure',
  'Relaxation',
  'Culture',
  'Food',
  'Nightlife',
  'Nature',
  'Photography',
  'Shopping',
  'History',
  'Art',
  'Romance',
  'Family',
  'Luxury',
  'Budget',
];

export const ACCOMMODATION_TYPES = [
  'Hotel',
  'Hostel',
  'Airbnb',
  'Resort',
  'Apartment',
  'Boutique Hotel',
  'Guesthouse',
  'Villa',
];

export const ACTIVITY_TYPES = [
  'Sightseeing',
  'Museums',
  'Outdoor Activities',
  'Food Tours',
  'Nightlife',
  'Shopping',
  'Cultural Experiences',
  'Adventure Sports',
  'Photography',
  'Local Markets',
  'Festivals',
  'Nature Tours',
  'Historical Sites',
  'Art Galleries',
];

export const CURRENCIES = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'JPY', symbol: '¥', name: 'Japanese Yen' },
  { code: 'INR', symbol: '₹', name: 'Indian Rupee' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
  { code: 'AUD', symbol: 'A$', name: 'Australian Dollar' },
];

export const DATE_FORMATS = {
  DISPLAY: 'MMM DD, YYYY',
  API: 'YYYY-MM-DD',
  PICKER: 'YYYY-MM-DD',
};

export const LOCAL_STORAGE_KEYS = {
  AUTH_TOKEN: 'authToken',
  USER_PREFERENCES: 'userPreferences',
  RECENT_SEARCHES: 'recentSearches',
};

export const NOTIFICATION_TYPES = {
  TRIP_READY: 'trip_ready',
  COLLABORATION_INVITE: 'collaboration_invite',
  TRIP_UPDATE: 'trip_update',
  REMINDER: 'reminder',
};

export const ROUTES = {
  HOME: '/',
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  DASHBOARD: '/app/dashboard',
  TRIPS: '/app/trips',
  NEW_TRIP: '/app/trips/new',
  TRIP_DETAILS: '/app/trips/:tripId',
  TRIP_EDIT: '/app/trips/:tripId/edit',
  COLLABORATION: '/app/trips/:tripId/collaborate',
  AI_CHAT: '/app/ai-chat',
  PROFILE: '/app/profile',
  SETTINGS: '/app/settings',
};
