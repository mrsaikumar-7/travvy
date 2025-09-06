/**
 * AI Chat Page
 * 
 * Conversational AI assistant for trip planning with voice and image support
 */

import React, { useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Typography, 
  Button, 
  Space, 
  Divider,
  Empty,
  Spin 
} from 'antd';
import { 
  MessageOutlined,
  PlusOutlined,
  DeleteOutlined,
  DownloadOutlined,
  SettingOutlined
} from '@ant-design/icons';

import { useAIChat } from '../../context/AIChatContext';
import ChatMessage from '../../components/features/chat/ChatMessage';
import ChatInput from '../../components/features/chat/ChatInput';

const { Title, Text } = Typography;

const AIChatPage = () => {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  
  const {
    currentConversation,
    currentConversationId,
    isTyping,
    isRecording,
    isAnalyzing,
    startNewConversation,
    sendMessage,
    sendVoiceMessage,
    analyzeImage,
    clearConversation,
    setCurrentConversationId
  } = useAIChat();

  // Initialize conversation
  useEffect(() => {
    if (conversationId && conversationId !== currentConversationId) {
      setCurrentConversationId(conversationId);
    } else if (!conversationId && !currentConversationId) {
      const newId = startNewConversation();
      navigate(`/app/ai-chat/${newId}`, { replace: true });
    }
  }, [conversationId, currentConversationId, startNewConversation, setCurrentConversationId, navigate]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [currentConversation.messages, isTyping]);

  const handleSuggestedAction = (action) => {
    sendMessage(action);
  };

  const handleNewConversation = () => {
    const newId = startNewConversation();
    navigate(`/app/ai-chat/${newId}`);
  };

  const handleClearConversation = () => {
    clearConversation();
    navigate('/app/ai-chat');
  };

  const handleExportConversation = () => {
    const conversationData = {
      id: currentConversation.id,
      messages: currentConversation.messages,
      createdAt: currentConversation.createdAt,
      exportedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(conversationData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-chat-${currentConversation.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!currentConversation.id) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <Spin size="large" tip="Starting conversation..." />
      </div>
    );
  }

  return (
    <div style={{ height: 'calc(100vh - 112px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Card 
        size="small"
        style={{ 
          borderRadius: '8px 8px 0 0',
          borderBottom: '1px solid #f0f0f0',
          flexShrink: 0
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <MessageOutlined style={{ color: '#1890ff', fontSize: '20px' }} />
            <div>
              <Title level={4} style={{ margin: 0 }}>
                AI Travel Assistant
              </Title>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                Chat • Voice • Image Analysis
              </Text>
            </div>
          </Space>

          <Space>
            <Button 
              size="small" 
              icon={<PlusOutlined />}
              onClick={handleNewConversation}
            >
              New Chat
            </Button>
            <Button 
              size="small" 
              icon={<DownloadOutlined />}
              onClick={handleExportConversation}
            >
              Export
            </Button>
            <Button 
              size="small" 
              icon={<DeleteOutlined />}
              onClick={handleClearConversation}
              danger
            >
              Clear
            </Button>
          </Space>
        </div>
      </Card>

      {/* Messages Area */}
      <div 
        style={{ 
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          position: 'relative'
        }}
      >
        {currentConversation.messages.length === 0 ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%' 
          }}>
            <Empty
              image="/api/placeholder/200/150"
              description={
                <div>
                  <Title level={4}>Start a conversation</Title>
                  <Text type="secondary">
                    Ask about destinations, plan trips, upload photos, or use voice commands!
                  </Text>
                </div>
              }
            />
          </div>
        ) : (
          <>
            {/* Messages */}
            {currentConversation.messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                onActionClick={handleSuggestedAction}
              />
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div style={{ 
                display: 'flex', 
                justifyContent: 'flex-start',
                marginBottom: '16px'
              }}>
                <Card
                  size="small"
                  style={{
                    backgroundColor: '#f5f5f5',
                    borderRadius: '18px 18px 18px 6px',
                    border: 'none',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  bodyStyle={{ padding: '12px 16px' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      AI is thinking...
                    </Text>
                  </div>
                </Card>
              </div>
            )}

            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div style={{ flexShrink: 0 }}>
        <ChatInput
          onSendMessage={sendMessage}
          onSendVoice={sendVoiceMessage}
          onAnalyzeImage={analyzeImage}
          isTyping={isTyping}
          isRecording={isRecording}
          isAnalyzing={isAnalyzing}
        />
      </div>
    </div>
  );
};

export default AIChatPage;
