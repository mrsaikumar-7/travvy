/**
 * Main App Component
 * 
 * Root component with routing, context providers, and global styles
 */

import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider, App as AntApp } from 'antd';
import { AuthProvider } from './context/AuthContext';
import { TripProvider } from './context/TripContext';
import { AIChatProvider } from './context/AIChatContext';
import AppRouter from './components/AppRouter';

// Ant Design theme configuration
const theme = {
  token: {
    // Primary color
    colorPrimary: '#1890ff',
    
    // Layout
    borderRadius: 8,
    
    // Typography
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: 14,
    
    // Spacing
    paddingContentHorizontalLG: 24,
    
    // Colors
    colorBgContainer: '#ffffff',
    colorBorderSecondary: '#f0f0f0',
    
    // Components
    controlHeight: 40,
    controlHeightLG: 48,
  },
  components: {
    Layout: {
      bodyBg: '#f5f5f5',
      headerBg: '#ffffff',
      siderBg: '#ffffff',
    },
    Menu: {
      itemBg: 'transparent',
      subMenuItemBg: 'transparent',
      itemSelectedBg: '#e6f4ff',
      itemHoverBg: '#f5f5f5',
    },
    Card: {
      borderRadiusLG: 12,
      paddingLG: 24,
    },
    Button: {
      borderRadius: 8,
      controlHeight: 40,
      controlHeightLG: 48,
    },
    Input: {
      borderRadius: 8,
      controlHeight: 40,
      controlHeightLG: 48,
    },
  },
};

const App = () => {
  return (
    <ConfigProvider theme={theme}>
      <AntApp>
        <BrowserRouter>
          <AuthProvider>
            <TripProvider>
              <AIChatProvider>
                <div className="App">
                  <AppRouter />
                </div>
              </AIChatProvider>
            </TripProvider>
          </AuthProvider>
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  );
};

export default App;
