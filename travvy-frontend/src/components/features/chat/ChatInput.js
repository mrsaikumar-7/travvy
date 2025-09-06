/**
 * Chat Input Component
 * 
 * Multi-modal input for text, voice, and image messages
 */

import React, { useState, useRef } from 'react';
import { 
  Input, 
  Button, 
  Space, 
  Upload, 
  message as antMessage,
  Tooltip,
  Progress 
} from 'antd';
import { 
  SendOutlined, 
  AudioOutlined, 
  PictureOutlined,
  LoadingOutlined,
  StopOutlined,
  MicrophoneIcon
} from '@ant-design/icons';

const { TextArea } = Input;

const ChatInput = ({ 
  onSendMessage, 
  onSendVoice, 
  onAnalyzeImage,
  isTyping = false,
  isRecording = false,
  isAnalyzing = false 
}) => {
  const [inputValue, setInputValue] = useState('');
  const [recordingTime, setRecordingTime] = useState(0);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordingIntervalRef = useRef(null);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;
    
    onSendMessage(inputValue.trim());
    setInputValue('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const audioChunks = [];
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        onSendVoice(audioBlob);
        
        // Clean up
        stream.getTracks().forEach(track => track.stop());
        setRecordingTime(0);
        if (recordingIntervalRef.current) {
          clearInterval(recordingIntervalRef.current);
        }
      };
      
      mediaRecorder.start();
      
      // Start timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      antMessage.error('Could not access microphone. Please check permissions.');
    }
  };

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    if (recordingIntervalRef.current) {
      clearInterval(recordingIntervalRef.current);
    }
  };

  const handleVoiceClick = () => {
    if (isRecording) {
      stopVoiceRecording();
    } else {
      startVoiceRecording();
    }
  };

  const handleImageUpload = (file) => {
    // Validate file type
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      antMessage.error('Please upload an image file!');
      return false;
    }

    // Validate file size (max 10MB)
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      antMessage.error('Image must be smaller than 10MB!');
      return false;
    }

    onAnalyzeImage(file, 'What destination or travel inspiration does this image suggest?');
    return false; // Prevent default upload
  };

  const formatRecordingTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const isDisabled = isTyping || isRecording || isAnalyzing;

  return (
    <div style={{ padding: '16px', background: '#fff', borderTop: '1px solid #f0f0f0' }}>
      {/* Recording Progress */}
      {isRecording && (
        <div style={{ marginBottom: '12px' }}>
          <Progress 
            percent={Math.min((recordingTime / 60) * 100, 100)}
            format={() => formatRecordingTime(recordingTime)}
            status="active"
            strokeColor="#ff4d4f"
          />
        </div>
      )}

      {/* Status Messages */}
      {isTyping && (
        <div style={{ marginBottom: '12px', color: '#999', fontSize: '12px' }}>
          🤖 AI is thinking...
        </div>
      )}
      
      {isAnalyzing && (
        <div style={{ marginBottom: '12px', color: '#999', fontSize: '12px' }}>
          🔍 Analyzing your image...
        </div>
      )}

      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
        {/* Text Input */}
        <div style={{ flex: 1 }}>
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              isRecording ? "Recording voice message..." :
              isTyping ? "AI is responding..." :
              isAnalyzing ? "Analyzing image..." :
              "Ask about destinations, plan trips, or share your travel ideas..."
            }
            disabled={isDisabled}
            autoSize={{ minRows: 1, maxRows: 4 }}
            style={{ resize: 'none' }}
          />
        </div>

        {/* Action Buttons */}
        <Space>
          {/* Voice Recording Button */}
          <Tooltip title={isRecording ? "Stop Recording" : "Voice Message"}>
            <Button
              type={isRecording ? "primary" : "default"}
              danger={isRecording}
              icon={
                isRecording ? <StopOutlined /> : 
                <AudioOutlined />
              }
              onClick={handleVoiceClick}
              disabled={isTyping || isAnalyzing}
              style={{
                backgroundColor: isRecording ? '#ff4d4f' : undefined,
                borderColor: isRecording ? '#ff4d4f' : undefined
              }}
            />
          </Tooltip>

          {/* Image Upload Button */}
          <Tooltip title="Analyze Image">
            <Upload
              accept="image/*"
              beforeUpload={handleImageUpload}
              showUploadList={false}
              disabled={isDisabled}
            >
              <Button
                icon={isAnalyzing ? <LoadingOutlined /> : <PictureOutlined />}
                disabled={isDisabled}
              />
            </Upload>
          </Tooltip>

          {/* Send Button */}
          <Tooltip title="Send Message">
            <Button
              type="primary"
              icon={isTyping ? <LoadingOutlined /> : <SendOutlined />}
              onClick={handleSendMessage}
              disabled={isDisabled || !inputValue.trim()}
            />
          </Tooltip>
        </Space>
      </div>

      {/* Quick Action Suggestions */}
      <div style={{ marginTop: '8px' }}>
        <Space wrap>
          <Button
            size="small"
            type="text"
            onClick={() => setInputValue('Plan a weekend trip to Paris')}
            disabled={isDisabled}
            style={{ fontSize: '11px', color: '#666' }}
          >
            Plan weekend trip
          </Button>
          <Button
            size="small"
            type="text"
            onClick={() => setInputValue('Show me budget-friendly beach destinations')}
            disabled={isDisabled}
            style={{ fontSize: '11px', color: '#666' }}
          >
            Budget beaches
          </Button>
          <Button
            size="small"
            type="text"
            onClick={() => setInputValue('I want an adventure trip for 2 weeks')}
            disabled={isDisabled}
            style={{ fontSize: '11px', color: '#666' }}
          >
            Adventure trip
          </Button>
          <Button
            size="small"
            type="text"
            onClick={() => setInputValue('What are the best food destinations?')}
            disabled={isDisabled}
            style={{ fontSize: '11px', color: '#666' }}
          >
            Food destinations
          </Button>
        </Space>
      </div>
    </div>
  );
};

export default ChatInput;
