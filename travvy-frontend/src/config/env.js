/**
 * Environment Configuration
 * 
 * Configuration for different environments and feature flags
 */

const config = {
  // API Configuration
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  // Feature Flags
  ENABLE_DEMO_MODE: process.env.REACT_APP_ENABLE_DEMO_MODE === 'true' || true,
  ENABLE_API_LOGGING: process.env.REACT_APP_ENABLE_API_LOGGING === 'true' || true,
  
  // Debug
  DEBUG: process.env.REACT_APP_DEBUG === 'true' || process.env.NODE_ENV === 'development',
  
  // Demo Credentials
  DEMO_CREDENTIALS: {
    email: 'demo@Travvy.com',
    password: 'demo123'
  },
  
  // API Endpoints
  ENDPOINTS: {
    HEALTH: '/health',
    AUTH: {
      LOGIN: '/api/v1/auth/login',
      REGISTER: '/api/v1/auth/register',
      GOOGLE: '/api/v1/auth/google',
      ME: '/api/v1/auth/me',
      LOGOUT: '/api/v1/auth/logout',
    },
    TRIPS: {
      LIST: '/api/v1/trips',
      CREATE: '/api/v1/trips',
      DETAILS: '/api/v1/trips',
    },
    AI: {
      CONVERSATION: '/api/v1/ai/conversation',
      IMAGE_ANALYSIS: '/api/v1/ai/image-analysis',
      VOICE_INPUT: '/api/v1/ai/voice-input',
    }
  }
};

export default config;
