/**
 * Chat Message Component
 * 
 * Individual message bubble for AI chat conversations
 */

import React from 'react';
import { Avatar, Card, Typography, Space, Button, Image, Tag } from 'antd';
import { 
  UserOutlined, 
  RobotOutlined, 
  CopyOutlined, 
  ShareAltOutlined,
  PictureOutlined 
} from '@ant-design/icons';
import moment from 'moment';

const { Text, Paragraph } = Typography;

const ChatMessage = ({ message, onActionClick }) => {
  const isUser = message.type === 'user';
  const isAI = message.type === 'ai';

  const handleSuggestedAction = (action) => {
    if (onActionClick) {
      onActionClick(action);
    }
  };

  const formatMessageText = (text) => {
    if (!text) return '';
    
    // Convert markdown-style formatting to JSX
    const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*')) {
        return <em key={index}>{part.slice(1, -1)}</em>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={index} style={{ background: '#f5f5f5', padding: '2px 4px', borderRadius: '3px' }}>{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '16px',
        gap: '12px'
      }}
    >
      {/* AI Avatar (left side) */}
      {isAI && (
        <Avatar
          size="large"
          style={{
            backgroundColor: '#1890ff',
            flexShrink: 0
          }}
          icon={<RobotOutlined />}
        />
      )}

      {/* Message Content */}
      <div
        style={{
          maxWidth: '70%',
          minWidth: '200px'
        }}
      >
        <Card
          size="small"
          style={{
            backgroundColor: isUser ? '#1890ff' : '#f5f5f5',
            color: isUser ? 'white' : 'black',
            borderRadius: isUser ? '18px 18px 6px 18px' : '18px 18px 18px 6px',
            border: 'none',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}
          bodyStyle={{
            padding: '12px 16px'
          }}
        >
          {/* Text Content */}
          {message.content.text && (
            <Paragraph
              style={{
                margin: 0,
                color: isUser ? 'white' : 'black',
                whiteSpace: 'pre-wrap',
                lineHeight: '1.5'
              }}
            >
              {formatMessageText(message.content.text)}
            </Paragraph>
          )}

          {/* Image Content */}
          {message.content.image && (
            <div style={{ marginTop: message.content.text ? '8px' : 0 }}>
              <Image
                src={message.content.image.url}
                alt="Uploaded image"
                style={{
                  maxWidth: '100%',
                  borderRadius: '8px'
                }}
                preview={{
                  mask: <PictureOutlined style={{ fontSize: '20px' }} />
                }}
              />
              {message.content.image.prompt && (
                <Text
                  type="secondary"
                  style={{
                    fontSize: '12px',
                    fontStyle: 'italic',
                    color: isUser ? 'rgba(255,255,255,0.8)' : 'rgba(0,0,0,0.6)',
                    display: 'block',
                    marginTop: '4px'
                  }}
                >
                  "{message.content.image.prompt}"
                </Text>
              )}
            </div>
          )}

          {/* Voice Content */}
          {message.content.voice && (
            <div style={{ marginTop: message.content.text ? '8px' : 0 }}>
              <audio controls style={{ width: '100%' }}>
                <source src={message.content.voice.url} type="audio/wav" />
                Your browser does not support the audio element.
              </audio>
              {message.content.voice.transcription && (
                <Text
                  type="secondary"
                  style={{
                    fontSize: '12px',
                    fontStyle: 'italic',
                    color: isUser ? 'rgba(255,255,255,0.8)' : 'rgba(0,0,0,0.6)',
                    display: 'block',
                    marginTop: '4px'
                  }}
                >
                  Transcription: "{message.content.voice.transcription}"
                </Text>
              )}
            </div>
          )}

          {/* Timestamp */}
          <Text
            style={{
              fontSize: '10px',
              color: isUser ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.5)',
              display: 'block',
              marginTop: '8px',
              textAlign: 'right'
            }}
          >
            {moment(message.timestamp).format('h:mm A')}
          </Text>
        </Card>

        {/* AI Suggested Actions */}
        {isAI && message.content.suggested_actions && message.content.suggested_actions.length > 0 && (
          <div style={{ marginTop: '8px' }}>
            <Space wrap>
              {message.content.suggested_actions.map((action, index) => (
                <Button
                  key={index}
                  size="small"
                  type="default"
                  style={{
                    borderRadius: '12px',
                    fontSize: '12px'
                  }}
                  onClick={() => handleSuggestedAction(action)}
                >
                  {action}
                </Button>
              ))}
            </Space>
          </div>
        )}

        {/* Message Actions */}
        {isAI && (
          <div style={{ marginTop: '8px', textAlign: 'right' }}>
            <Space>
              <Button
                type="text"
                size="small"
                icon={<CopyOutlined />}
                onClick={() => navigator.clipboard?.writeText(message.content.text)}
                style={{ fontSize: '12px', color: '#999' }}
              >
                Copy
              </Button>
              <Button
                type="text"
                size="small"
                icon={<ShareAltOutlined />}
                style={{ fontSize: '12px', color: '#999' }}
              >
                Share
              </Button>
            </Space>
          </div>
        )}
      </div>

      {/* User Avatar (right side) */}
      {isUser && (
        <Avatar
          size="large"
          style={{
            backgroundColor: '#52c41a',
            flexShrink: 0
          }}
          icon={<UserOutlined />}
        />
      )}
    </div>
  );
};

export default ChatMessage;
